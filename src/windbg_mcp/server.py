"""WinDbgMCP Server - FastMCP Protocol Implementation & Extended Reverse-Engineering Tools."""

from __future__ import annotations

import atexit
import glob
import os
import re
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP, Context

from windbg_mcp.ai_provider import AIProviderConfig, get_available_ai_providers
from windbg_mcp.cdb_session import (
    attach_live_process_session,
    open_cdb_dump_session,
    open_cdb_remote_session,
)
from windbg_mcp.cfg_builder import build_cfg_mermaid
from windbg_mcp.debug_session import DebugSession, DebuggerError
from windbg_mcp.kd_session import open_kd_session
from windbg_mcp.re_engines import (
    diff_memory_bytes,
    reconstruct_struct_definition,
    synthesize_crash_triage_report,
    build_api_trace_payload,
    parse_pe_header_in_memory,
    audit_kernel_integrity_report,
    scan_stack_spoofing_report,
    find_rop_gadgets_report,
    audit_heap_corruption_report,
)

# Initialize FastMCP Server
mcp = FastMCP(
    "windbg-mcp",
    instructions="Model Context Protocol (MCP) server for WinDbg & WinDbgX with DebugExt reverse-engineering tools.",
)

# Active debug sessions dictionary: session_id -> DebugSession
SESSIONS: Dict[str, DebugSession] = {}
ACTIVE_SESSION_ID: Optional[str] = None


def cleanup_all_sessions():
    """Safety cleanup handler to kill orphaned debugger processes on server shutdown."""
    for sid, session in list(SESSIONS.items()):
        try:
            session.close(resume_kernel=False)
        except Exception:
            pass
    SESSIONS.clear()


# Register cleanup at Python process exit
atexit.register(cleanup_all_sessions)


def get_session(session_id: Optional[str] = None) -> DebugSession:
    """Retrieve specified or default active session, automatically pruning dead/terminated sessions."""
    global ACTIVE_SESSION_ID

    # Prune closed or terminated sessions automatically
    for sid in list(SESSIONS.keys()):
        sess = SESSIONS[sid]
        if sess.closed or (sess.process and sess.process.poll() is not None):
            SESSIONS.pop(sid, None)
            if ACTIVE_SESSION_ID == sid:
                ACTIVE_SESSION_ID = list(SESSIONS.keys())[-1] if SESSIONS else None

    target_id = session_id or ACTIVE_SESSION_ID
    if not target_id:
        if SESSIONS:
            target_id = list(SESSIONS.keys())[-1]
        else:
            raise DebuggerError("No active debug session available. Open a dump, remote server, live process, or KD session first.")

    session = SESSIONS.get(target_id)
    if not session:
        raise DebuggerError(f"Session '{target_id}' not found or closed. Active sessions: {list(SESSIONS.keys())}")
    return session


# -----------------------------------------------------------------------------
# Category A: Session & Target Connection Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def list_sessions() -> str:
    """List all active debugging sessions and indicate the default active session."""
    if not SESSIONS:
        return "No open debugging sessions."

    lines = ["Active Debugging Sessions:"]
    for sid, sess in SESSIONS.items():
        active_flag = " (ACTIVE)" if sid == ACTIVE_SESSION_ID else ""
        lines.append(f" - [{sess.debugger_type.upper()}] {sid}{active_flag}")
    return "\n".join(lines)


@mcp.tool()
def switch_session(session_id: str) -> str:
    """Switch the default active session to the specified session_id."""
    global ACTIVE_SESSION_ID
    if session_id not in SESSIONS:
        return f"Error: Session '{session_id}' does not exist. Open sessions: {list(SESSIONS.keys())}"
    ACTIVE_SESSION_ID = session_id
    return f"Switched default active session to '{session_id}'."


@mcp.tool()
def list_dumps(directory_path: Optional[str] = None, recursive: bool = False) -> str:
    """Enumerate crash dump files (.dmp) in local or specified directory."""
    target_dir = directory_path or os.environ.get("LOCALAPPDATA", "C:\\")
    pattern = os.path.join(target_dir, "**", "*.dmp") if recursive else os.path.join(target_dir, "*.dmp")
    matches = glob.glob(pattern, recursive=recursive)

    if not matches:
        return f"No .dmp files found in '{target_dir}'."

    results = []
    for path in matches[:50]:
        try:
            stat = os.stat(path)
            size_mb = stat.st_size / (1024 * 1024)
            results.append(f" - {path} ({size_mb:.2f} MB)")
        except Exception:
            results.append(f" - {path}")

    return f"Found {len(matches)} dump files:\n" + "\n".join(results)


PROTOCOL_DRIVER_BANNER = (
    "\n\n========================================================\n"
    "[SYSTEM DRIVER PROTOCOL - WINDBGMCP]:\n"
    "1. HYGIENE: Store ALL analysis logs in analysis/<TARGET>/mds/scratchpad.md and scripts in analysis/<TARGET>/scripts/\n"
    "2. DEBUGEXT: For complex targets & reversing, use DebugExt (!de.disasm, !de.dq, !de.dp, !de.hooks, !de.strref, !de.xrefs, !de.args, !de.vtable, !de.memmap, !de.pe)\n"
    "3. REPORTING: Generate analysis/<TARGET>/mds/<TARGET>_Final_Report.md upon completing task.\n"
    "========================================================\n"
)


@mcp.tool()
def open_cdb_dump(
    dump_path: str,
    symbols_path: Optional[str] = None,
    include_stack: bool = True,
    include_modules: bool = True,
    timeout_seconds: float = 180.0,
) -> str:
    """Open a crash dump (.dmp) and run initial analysis (!analyze -v, stack, modules). Returns session_id."""
    global ACTIVE_SESSION_ID
    output, session = open_cdb_dump_session(
        dump_path=dump_path,
        symbols_path=symbols_path,
        include_stack=include_stack,
        include_modules=include_modules,
        timeout_seconds=timeout_seconds,
    )
    SESSIONS[session.session_id] = session
    ACTIVE_SESSION_ID = session.session_id
    return output + PROTOCOL_DRIVER_BANNER


@mcp.tool()
def open_cdb_remote(
    connection_string: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 60.0,
) -> str:
    """Attach to a user-mode remote debugging server (-remote tcp:Port=..., npipe:Pipe=...). Returns session_id."""
    global ACTIVE_SESSION_ID
    output, session = open_cdb_remote_session(
        connection_string=connection_string,
        symbols_path=symbols_path,
        timeout_seconds=timeout_seconds,
    )
    SESSIONS[session.session_id] = session
    ACTIVE_SESSION_ID = session.session_id
    return output + PROTOCOL_DRIVER_BANNER


@mcp.tool()
def open_kd_session_tool(
    connection_string: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 120.0,
) -> str:
    """Attach to a kernel-mode target using kd.exe (-k net:..., com:pipe...). Returns session_id."""
    global ACTIVE_SESSION_ID
    output, session = open_kd_session(
        connection_string=connection_string,
        symbols_path=symbols_path,
        timeout_seconds=timeout_seconds,
    )
    SESSIONS[session.session_id] = session
    ACTIVE_SESSION_ID = session.session_id
    return output + PROTOCOL_DRIVER_BANNER


@mcp.tool()
def attach_live_process(
    target: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 60.0,
) -> str:
    """Attach cdb.exe directly to a live running process by PID or executable name (e.g. '1234' or 'notepad.exe'). Returns session_id."""
    global ACTIVE_SESSION_ID
    output, session = attach_live_process_session(
        target=target,
        symbols_path=symbols_path,
        timeout_seconds=timeout_seconds,
    )
    SESSIONS[session.session_id] = session
    ACTIVE_SESSION_ID = session.session_id
    return output + PROTOCOL_DRIVER_BANNER


@mcp.tool()
def close_session(session_id: Optional[str] = None, resume_kernel: bool = True) -> str:
    """Close an active debugging session and release process handles."""
    global ACTIVE_SESSION_ID
    target_id = session_id or ACTIVE_SESSION_ID
    if not target_id:
        return "No active session to close."

    session = SESSIONS.pop(target_id, None)
    if not session:
        return f"Session '{target_id}' not found."

    if ACTIVE_SESSION_ID == target_id:
        ACTIVE_SESSION_ID = list(SESSIONS.keys())[-1] if SESSIONS else None

    return session.close(resume_kernel=resume_kernel)


# -----------------------------------------------------------------------------
# Category B: Execution Control & Synchronization
# -----------------------------------------------------------------------------

@mcp.tool()
def annotate_session(
    milestone: str,
    category: str = "MILESTONE",
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Visual] Write a prominent milestone or reasoning banner directly into the live WinDbg GUI output window."""
    session = get_session(session_id)
    return session.annotate_session(milestone, category=category)


def _get_analysis_dir(target_name: str) -> tuple[Path, str]:
    """Helper to resolve root/analysis/FILE_NAME/mds directory structure."""
    clean_name = re.sub(r"[^\w\.-]", "_", target_name.strip())
    clean_base = clean_name.rsplit(".", 1)[0] if "." in clean_name and not clean_name.startswith(".") else clean_name
    if not clean_base:
        clean_base = "general"

    analysis_dir = Path(os.getcwd()) / "analysis" / clean_base / "mds"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    return analysis_dir, clean_base


@mcp.tool()
def update_scratchpad(
    target_name: str,
    section_title: str,
    content: str,
) -> str:
    """[Antigravity Artifact] Append live analysis notes, register state, and command intent to root/analysis/FILE_NAME/mds/scratchpad.md."""
    analysis_dir, clean_base = _get_analysis_dir(target_name)
    scratchpad_path = analysis_dir / "scratchpad.md"

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_entry = f"\n\n---\n\n### [{section_title}] - {timestamp}\n\n{content.strip()}\n"

    if not scratchpad_path.exists():
        header = f"# Debugging Scratchpad: {clean_base}\n\nLive execution log & incremental reverse-engineering notes.\n"
        with open(scratchpad_path, "w", encoding="utf-8") as f:
            f.write(header)

    with open(scratchpad_path, "a", encoding="utf-8") as f:
        f.write(formatted_entry)

    return f"Updated live scratchpad at '{scratchpad_path}' with section '{section_title}'."


@mcp.tool()
def generate_final_report(
    target_name: str,
    executive_summary: str,
    key_findings: Optional[List[str]] = None,
) -> str:
    """[Antigravity Artifact] Synthesize live scratchpad entries into a publication-grade final report at root/analysis/FILE_NAME/mds/FILE_NAME_Final_Report.md."""
    analysis_dir, clean_base = _get_analysis_dir(target_name)
    scratchpad_path = analysis_dir / "scratchpad.md"
    report_filename = f"{clean_base}_Final_Report.md"
    report_path = analysis_dir / report_filename

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    raw_scratchpad = ""
    if scratchpad_path.exists():
        with open(scratchpad_path, "r", encoding="utf-8") as f:
            raw_scratchpad = f.read()

    findings_block = ""
    if key_findings:
        findings_items = "\n".join(f"- {f}" for f in key_findings)
        findings_block = f"## 2. Key Findings & Technical Evidence\n\n{findings_items}\n\n"
    elif not raw_scratchpad:
        findings_block = "## 2. Key Findings & Technical Evidence\n\n- Dynamic analysis completed.\n\n"

    report_content = (
        f"# {clean_base} - Technical Analysis Final Report\n\n"
        f"**Target Binary/Driver**: `{clean_base}`  \n"
        f"**Report Generated**: `{timestamp}`  \n\n"
        f"## 1. Executive Summary\n\n{executive_summary.strip()}\n\n"
        f"{findings_block}"
        f"## 3. Dynamic Debugging & Reverse-Engineering Trace Log\n\n"
        f"{raw_scratchpad if raw_scratchpad else '*No scratchpad entries recorded.*'}\n\n"
        f"---\n"
        f"*Report synthesized automatically by WinDbgMCP.*"
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return f"Generated final analysis report at '{report_path}'."


@mcp.tool()
def diff_memory_snapshots(
    snapshot_A_cmd: str,
    snapshot_B_cmd: str,
    base_address: str = "0x00000000",
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Visual] Execute memory dumps before/after routine execution and generate detailed byte/pointer diffs."""
    session = get_session(session_id)
    dump_A = session.run_command(snapshot_A_cmd)
    dump_B = session.run_command(snapshot_B_cmd)
    return diff_memory_bytes(dump_A, dump_B, base_address=base_address)


@mcp.tool()
def triage_crash_report(
    dump_path: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 180.0,
) -> str:
    """[Antigravity Artifact] Perform full BSOD or user-mode crash dump triage and generate executive Root Cause Analysis (RCA) report."""
    raw_output, session = open_cdb_dump_session(
        dump_path=dump_path,
        symbols_path=symbols_path,
        include_stack=True,
        include_modules=True,
        timeout_seconds=timeout_seconds,
    )
    rca_report = synthesize_crash_triage_report(dump_path, raw_output)

    # Save report to root/analysis/FILE_NAME/mds/
    target_name = os.path.basename(dump_path)
    analysis_dir, clean_base = _get_analysis_dir(target_name)
    report_path = analysis_dir / f"{clean_base}_RCA_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(rca_report)

    return f"Crash Triage Complete! RCA report saved to '{report_path}'. Summary:\n\n{rca_report}"


@mcp.tool()
def reconstruct_struct(
    address: str,
    length: int = 64,
    struct_name: str = "RECONSTRUCTED_STRUCT",
    is_64bit: bool = True,
    session_id: Optional[str] = None,
) -> str:
    """[DebugExt] Inspect raw memory address, analyze pointers/dwords, and auto-generate C/C++ struct definition code."""
    session = get_session(session_id)
    cmd = f"dq {address} L{length // 8}" if is_64bit else f"dd {address} L{length // 4}"
    raw_dump = session.run_command(cmd, reasoning=f"Dumping memory bytes at {address} for C/C++ struct reconstruction")
    return reconstruct_struct_definition(raw_dump, base_address=address, struct_name=struct_name, is_64bit=is_64bit)


@mcp.tool()
def trace_api_calls(
    api_name: str,
    module_name: str = "kernel32",
    session_id: Optional[str] = None,
) -> str:
    """[DebugExt] Dynamically trace WinAPI calls (VirtualAlloc, WriteProcessMemory, etc.) and log arguments/stack trace upon execution."""
    session = get_session(session_id)
    bp_cmd, reasoning = build_api_trace_payload(api_name=api_name, module_name=module_name)
    return session.run_command(bp_cmd, reasoning=reasoning)


@mcp.tool()
def unpack_dynamic_pe(
    address: str,
    length: int,
    output_filename: str,
    session_id: Optional[str] = None,
) -> str:
    """[DebugExt] Scan memory region for hidden PE header (MZ), validate structure, and dump unpacked payload to disk artifact."""
    session = get_session(session_id)
    raw_dump = session.run_command(f"db {address} L32", reasoning=f"Scanning memory at {address} for hidden PE header (MZ)")
    valid, pe_info = parse_pe_header_in_memory(raw_dump, base_address=address)

    if not valid:
        return pe_info

    writemem_cmd = f".writemem {output_filename} {address} L?{length}"
    export_result = session.run_command(writemem_cmd, reasoning=f"Exporting unpacked PE payload to disk artifact '{output_filename}'")
    return f"{pe_info}\n\n### Export Result\n```text\n{export_result}\n```"


@mcp.tool()
def audit_kernel_integrity(
    process_list_cmd: str = "!process 0 0",
    ssdt_dump_cmd: Optional[str] = None,
    drivers_dump_cmd: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[Score 8 Superpower] Audit kernel EPROCESS lists, System Service Descriptor Table (SSDT), and driver MajorFunction arrays for DKOM rootkits, hidden processes, and unbacked hooks."""
    session = get_session(session_id)
    raw_proc = session.run_command(process_list_cmd, reasoning="Auditing kernel EPROCESS list for DKOM hidden processes")
    raw_ssdt = session.run_command(ssdt_dump_cmd, reasoning="Dumping SSDT dispatch table") if ssdt_dump_cmd else ""
    raw_drivers = session.run_command(drivers_dump_cmd, reasoning="Auditing driver MajorFunction dispatch tables") if drivers_dump_cmd else ""
    return audit_kernel_integrity_report(raw_proc, raw_ssdt, raw_drivers)


@mcp.tool()
def scan_stack_spoofing(
    stack_cmd: str = "kb 20",
    memory_map_cmd: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[Score 8 Superpower] Inspect thread stack frames for unbacked return addresses (pointing to unmapped/RWX memory), stack pointer alignment anomalies, and fake stack frames (ROP chains)."""
    session = get_session(session_id)
    raw_stack = session.run_command(stack_cmd, reasoning="Inspecting thread callstack for unbacked return addresses and stack spoofing")
    raw_map = session.run_command(memory_map_cmd, reasoning="Fetching virtual memory map for stack frame protection audit") if memory_map_cmd else ""
    return scan_stack_spoofing_report(raw_stack, raw_map)


@mcp.tool()
def find_rop_gadgets(
    disassemble_cmd: str = "u 0x00401000 L100",
    target_module: str = "target",
    session_id: Optional[str] = None,
) -> str:
    """[Score 7 Superpower] Scan loaded executable modules for useful ROP gadgets (e.g. pop rcx; ret, mov [rax], rbx; ret, xchg rax, rsp), filtering and categorizing them by register operation."""
    session = get_session(session_id)
    raw_disasm = session.run_command(disassemble_cmd, reasoning=f"Scanning disassembly of {target_module} for ROP gadgets ending in ret")
    return find_rop_gadgets_report(raw_disasm, target_module=target_module)


@mcp.tool()
def audit_heap_corruption(
    heap_cmd: str = "!heap -p -a",
    pageheap_cmd: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[Score 7 Superpower] Automate WinDbg !heap -p -a and Pageheap diagnostic flags to pinpoint corrupted chunk headers, freed allocation stack traces, and invalid free (UAF) addresses."""
    session = get_session(session_id)
    raw_heap = session.run_command(heap_cmd, reasoning="Auditing heap structures for chunk header corruption and allocation traces")
    raw_pageheap = session.run_command(pageheap_cmd, reasoning="Dumping Pageheap diagnostic fault log") if pageheap_cmd else ""
    return audit_heap_corruption_report(raw_heap, raw_pageheap)




@mcp.tool()
def update_analysis_report(
    section_title: str,
    content: str,
    report_filename: str = "analysis_report.md",
    target_name: str = "general",
) -> str:
    """[Antigravity Artifact] Append technical analysis section to target scratchpad log at root/analysis/FILE_NAME/mds/scratchpad.md."""
    return update_scratchpad(target_name=target_name, section_title=section_title, content=content)


@mcp.tool()
def run_cdb_command(
    command: str,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout_seconds: float = 60.0,
) -> str:
    """Run any WinDbg user-mode command on an open cdb session (e.g., 'kb', 'lm', '!heap'). Pass reasoning to display intent live in WinDbg GUI."""
    session = get_session(session_id)
    return session.run_command(command, timeout_seconds=timeout_seconds, reasoning=reasoning)


@mcp.tool()
def run_kd_command(
    command: str,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
    timeout_seconds: float = 120.0,
) -> str:
    """Run any command on an open kernel-mode (kd) session (e.g., '!process 0 0', '!thread'). Pass reasoning to display intent live in WinDbg GUI."""
    session = get_session(session_id)
    return session.run_command(command, timeout_seconds=timeout_seconds, reasoning=reasoning)


@mcp.tool()
def send_ctrl_break(session_id: Optional[str] = None) -> str:
    """Send CTRL+BREAK to halt a running target and force prompt resynchronization."""
    session = get_session(session_id)
    return session.send_ctrl_break()


@mcp.tool()
def wait_for_break(session_id: Optional[str] = None, timeout_seconds: float = 300.0) -> str:
    """Asynchronously wait for a target to stop on a breakpoint or exception."""
    session = get_session(session_id)
    return session.wait_for_break(timeout_seconds=timeout_seconds)


# -----------------------------------------------------------------------------
# Category C: Extended Reverse-Engineering & Visual Artifact Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def render_control_flow_graph(
    target_address_or_symbol: str,
    instruction_count: int = 50,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Visual] Disassemble target routine and build a native Mermaid flowchart (graph TD) for artifact rendering."""
    session = get_session(session_id)
    raw_disasm = session.run_command(f"u {target_address_or_symbol} L{instruction_count}", reasoning=reasoning)
    mermaid_cfg = build_cfg_mermaid(raw_disasm, title=f"CFG: {target_address_or_symbol}")

    return f"### Control Flow Graph for {target_address_or_symbol}\n\n{mermaid_cfg}\n\n### Raw Disassembly\n```assembly\n{raw_disasm}\n```"


@mcp.tool()
def dump_memory_visual(
    address: str,
    length: int = 128,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Visual] Display formatted memory bytes with hex, ASCII, and symbol labels in a clean table."""
    session = get_session(session_id)
    raw_db = session.run_command(f"db {address} L{length}", reasoning=reasoning)
    raw_dc = session.run_command(f"dc {address} L{length}")

    return f"### Memory Dump: {address} ({length} bytes)\n\n#### Hex & ASCII (`db`)\n```text\n{raw_db}\n```\n\n#### Dword & Symbol Preview (`dc`)\n```text\n{raw_dc}\n```"


@mcp.tool()
def dump_rwx_payload(
    address: str,
    length: int,
    output_filename: str,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Artifact] Write raw memory buffer (shellcode/unpacked binary) to a local file for offline malware analysis."""
    session = get_session(session_id)
    cmd = f".writemem {output_filename} {address} L?{length}"
    result = session.run_command(cmd, reasoning=reasoning)
    return f"Wrote memory region [{address} -> +0x{length:X}] to '{output_filename}'. Output:\n{result}"


@mcp.tool()
def inspect_function_args(target: Optional[str] = None, reasoning: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Inspect live function calling convention parameters (args/params) with string/symbol previews."""
    session = get_session(session_id)
    cmd = f"args {target}" if target else "args"
    return session.run_command(cmd, reasoning=reasoning)


@mcp.tool()
def scan_string_references(module_name: str, reasoning: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Scan module code/data sections for ASCII and UTF-16 string references (strref)."""
    session = get_session(session_id)
    return session.run_command(f"strref {module_name}", reasoning=reasoning)


@mcp.tool()
def find_code_xrefs(
    target_address_or_symbol: str,
    module_name: Optional[str] = None,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[DebugExt] Locate code cross-references (CALL, JMP, RIP-relative) to target address/symbol (xrefs)."""
    session = get_session(session_id)
    cmd = f"xrefs {target_address_or_symbol} {module_name}" if module_name else f"xrefs {target_address_or_symbol}"
    return session.run_command(cmd, reasoning=reasoning)


@mcp.tool()
def audit_memory_regions(reasoning: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Audit virtual memory protection states and highlight dangerous PAGE_EXECUTE_READWRITE (RWX) pages (memmap)."""
    session = get_session(session_id)
    return session.run_command("memmap", reasoning=reasoning)


@mcp.tool()
def translate_offset(
    mode: str,
    arg1: str,
    arg2: Optional[str] = None,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[DebugExt] Perform static (Ghidra/PE-bear) <-> live memory address translations.

    Modes:
      - 'rva': Jump to module RVA offset (e.g. mode='rva', arg1='AdvancedTarget', arg2='10F0')
      - 'fo2va': Raw disk File Offset -> live Virtual Address (e.g. mode='fo2va', arg1='AdvancedTarget', arg2='400')
      - 'va2fo': Live Address/Symbol -> RVA & Raw File Offset (e.g. mode='va2fo', arg1='AdvancedTarget!TestComplexApi')
    """
    session = get_session(session_id)
    if mode.lower() in {"rva", "gooffset"}:
        cmd = f"gooffset {arg1} {arg2}" if arg2 else f"gooffset {arg1}"
    elif mode.lower() in {"fo2va", "fileoffset", "fo"}:
        cmd = f"fo2va {arg1} {arg2}" if arg2 else f"fo2va {arg1}"
    elif mode.lower() in {"va2fo", "offsetof", "rvaof"}:
        cmd = f"va2fo {arg1}"
    else:
        return f"Unknown translation mode '{mode}'. Use 'rva', 'fo2va', or 'va2fo'."

    return session.run_command(cmd, reasoning=reasoning)


@mcp.tool()
def generate_signature(address_or_symbol: str, length: int = 32, reasoning: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Generate relocatable AOB signature with wildcards (makesig) or search pattern (findsig)."""
    session = get_session(session_id)
    return session.run_command(f"makesig {address_or_symbol} {length}", reasoning=reasoning)


@mcp.tool()
def scan_hooks_and_injections(
    audit_type: str = "hooks",
    module_name: Optional[str] = None,
    reasoning: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """[DebugExt] Scan for inline detours, IAT hooks, driver IRP hooks, shellcode pages, or code caves.

    Audit types: 'hooks', 'irphooks', 'injections', 'codecaves'.
    """
    session = get_session(session_id)
    t = audit_type.lower()
    if t == "hooks":
        cmd = f"hooks {module_name}" if module_name else "hooks"
    elif t == "irphooks":
        cmd = f"irphooks {module_name}" if module_name else "irphooks"
    elif t == "injections":
        cmd = "injections"
    elif t == "codecaves":
        cmd = f"codecaves {module_name}" if module_name else "codecaves"
    else:
        return f"Unknown audit type '{audit_type}'. Use 'hooks', 'irphooks', 'injections', or 'codecaves'."

    return session.run_command(cmd, reasoning=reasoning)


@mcp.tool()
def audit_pe_security(target: Optional[str] = None, reasoning: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Audit PE headers, ASLR/DEP/CFG mitigations, PEB anti-debug flags, and TEB stack limits (pe/peb/teb)."""
    session = get_session(session_id)
    cmd = f"pe {target}" if target else "pe"
    return session.run_command(cmd, reasoning=reasoning)


# -----------------------------------------------------------------------------
# Category H: AI Provider Management Tools
# -----------------------------------------------------------------------------

@mcp.tool()
def get_ai_provider_status() -> str:
    """Scan and list all 17 supported AI Providers (Gemini, OpenAI, Anthropic, DeepSeek, Mistral, Groq, Cerebras, Together, Grok/xAI, Fireworks, Perplexity, Cohere, Ollama, LM Studio, OpenRouter) and environment variable setup status."""
    providers = get_available_ai_providers()
    lines = ["### Supported AI Providers & Environment Status\n"]
    lines.append("| Provider | Environment Variable | Configuration Status | Value / Note |")
    lines.append("| :--- | :--- | :--- | :--- |")

    for p_name, details in providers.items():
        status_icon = "✅ Configured" if details["configured"] else "❌ Missing Environment Variable"
        lines.append(f"| `{p_name}` | `{details['env_var']}` | {status_icon} | `{details['status']}` |")

    lines.append("\n> **Note**: API keys are dynamically resolved from environment variables with zero hardcoding.")
    return "\n".join(lines)


@mcp.tool()
def configure_ai_provider(
    provider: str = "openrouter",
    model: str = "gpt-4o",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Initialize and validate an AI provider configuration (Gemini, OpenAI, Anthropic, DeepSeek, Mistral, Groq, Cerebras, Together, Grok/xAI, Fireworks, Perplexity, Cohere, Ollama, LM Studio, OpenRouter)."""
    try:
        cfg = AIProviderConfig(
            provider=provider,
            model=model,
            base_url=base_url,
            api_key=api_key,
        )
        info = cfg.to_dict()
        return (
            f"### AI Provider Configured Successfully\n\n"
            f"- **Provider**: `{info['provider']}`\n"
            f"- **Base URL**: `{info['base_url']}`\n"
            f"- **Model**: `{info['model']}`\n"
            f"- **API Key Set**: `{info['api_key_set']}` (Masked: `{info['masked_api_key']}`)"
        )
    except Exception as e:
        return f"### AI Provider Configuration Error\n\n**Error**: {str(e)}"



# -----------------------------------------------------------------------------
# MCP Prompts Protocol Registration
# -----------------------------------------------------------------------------

@mcp.prompt()
def crash_analyst() -> str:
    """System prompt for crash dump triage specialists."""
    return "You are an expert Windows Crash Dump Triage Specialist operating through WinDbgMCP. Perform root-cause analysis using open_cdb_dump, get_stack_trace, disassemble_at, and get_memory_map."


@mcp.prompt()
def malware_reversing() -> str:
    """System prompt for reverse engineers & threat analysts."""
    return "You are a Senior Reverse Engineer using WinDbgMCP. Disassemble binaries, scan for inline detours, IAT hooks, shellcode injections, extract string references, and create relocatable AOB signatures."


@mcp.prompt()
def kernel_investigator() -> str:
    """System prompt for Windows kernel & rootkit analysts."""
    return "You are a Windows Kernel Systems Specialist using WinDbgMCP. Investigate driver routines, system call tables, IRP dispatchers, DKOM, and kernel memory corruption using open_kd_session."


@mcp.prompt()
def windbg_doctor() -> str:
    """System prompt for WinDbg environment & symbol path diagnostics."""
    return "You are a Debugger Troubleshooting Expert. Diagnose symbol path issues (_NT_SYMBOL_PATH), verify DebugExt (de.dll) status, and recover stuck sessions using send_ctrl_break."


# -----------------------------------------------------------------------------
# Main entry point for standalone server launch
# -----------------------------------------------------------------------------

def run_server(
    transport: str = "stdio",
    host: str = "0.0.0.0",
    port: int = 8000,
    custom_hook_path: Optional[str] = None,
):
    """Run the FastMCP server on stdio or sse transport with optional custom hook."""
    if custom_hook_path:
        from windbg_mcp.custom_hook import load_custom_hook
        try:
            loaded = load_custom_hook(custom_hook_path)
            print(f"[*] Loaded custom hook from '{loaded.path}'")
        except Exception as e:
            print(f"[!] Failed to load custom hook: {e}")

    if transport.lower() == "sse":
        print(f"[*] Starting WinDbgMCP on SSE HTTP transport ({host}:{port})...")
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
