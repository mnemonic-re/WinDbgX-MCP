"""WinDbgMCP Server - FastMCP Protocol Implementation & Extended Reverse-Engineering Tools."""

from __future__ import annotations

import atexit
import glob
import os
import re
import signal
import sys
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP, Context

from windbg_mcp.cdb_session import (
    attach_live_process_session,
    open_cdb_dump_session,
    open_cdb_remote_session,
)
from windbg_mcp.cfg_builder import build_cfg_mermaid
from windbg_mcp.debug_session import DebugSession, DebuggerError
from windbg_mcp.kd_session import open_kd_session

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
    """Retrieve the specified session or the active default session."""
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
    return output


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
    return output


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
    return output


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
    return output


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
def run_cdb_command(command: str, session_id: Optional[str] = None, timeout_seconds: float = 60.0) -> str:
    """Run any WinDbg user-mode command on an open cdb session (e.g., 'kb', 'lm', '!heap')."""
    session = get_session(session_id)
    return session.run_command(command, timeout_seconds=timeout_seconds)


@mcp.tool()
def run_kd_command(command: str, session_id: Optional[str] = None, timeout_seconds: float = 120.0) -> str:
    """Run any command on an open kernel-mode (kd) session (e.g., '!process 0 0', '!thread')."""
    session = get_session(session_id)
    return session.run_command(command, timeout_seconds=timeout_seconds)


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
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Visual] Disassemble target routine and build a native Mermaid flowchart (graph TD) for artifact rendering."""
    session = get_session(session_id)
    raw_disasm = session.run_command(f"u {target_address_or_symbol} L{instruction_count}")
    mermaid_cfg = build_cfg_mermaid(raw_disasm, title=f"CFG: {target_address_or_symbol}")

    return f"### Control Flow Graph for {target_address_or_symbol}\n\n{mermaid_cfg}\n\n### Raw Disassembly\n```assembly\n{raw_disasm}\n```"


@mcp.tool()
def dump_memory_visual(
    address: str,
    length: int = 128,
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Visual] Display formatted memory bytes with hex, ASCII, and symbol labels in a clean table."""
    session = get_session(session_id)
    raw_db = session.run_command(f"db {address} L{length}")
    raw_dc = session.run_command(f"dc {address} L{length}")

    return f"### Memory Dump: {address} ({length} bytes)\n\n#### Hex & ASCII (`db`)\n```text\n{raw_db}\n```\n\n#### Dword & Symbol Preview (`dc`)\n```text\n{raw_dc}\n```"


@mcp.tool()
def dump_rwx_payload(
    address: str,
    length: int,
    output_filename: str,
    session_id: Optional[str] = None,
) -> str:
    """[Antigravity Artifact] Write raw memory buffer (shellcode/unpacked binary) to a local file for offline malware analysis."""
    session = get_session(session_id)
    cmd = f".writemem {output_filename} {address} L?{length}"
    result = session.run_command(cmd)
    return f"Wrote memory region [{address} -> +0x{length:X}] to '{output_filename}'. Output:\n{result}"


@mcp.tool()
def inspect_function_args(target: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Inspect live function calling convention parameters (args/params) with string/symbol previews."""
    session = get_session(session_id)
    cmd = f"args {target}" if target else "args"
    return session.run_command(cmd)


@mcp.tool()
def scan_string_references(module_name: str, session_id: Optional[str] = None) -> str:
    """[DebugExt] Scan module code/data sections for ASCII and UTF-16 string references (strref)."""
    session = get_session(session_id)
    return session.run_command(f"strref {module_name}")


@mcp.tool()
def find_code_xrefs(target_address_or_symbol: str, module_name: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Locate code cross-references (CALL, JMP, RIP-relative) to target address/symbol (xrefs)."""
    session = get_session(session_id)
    cmd = f"xrefs {target_address_or_symbol} {module_name}" if module_name else f"xrefs {target_address_or_symbol}"
    return session.run_command(cmd)


@mcp.tool()
def audit_memory_regions(session_id: Optional[str] = None) -> str:
    """[DebugExt] Audit virtual memory protection states and highlight dangerous PAGE_EXECUTE_READWRITE (RWX) pages (memmap)."""
    session = get_session(session_id)
    return session.run_command("memmap")


@mcp.tool()
def translate_offset(mode: str, arg1: str, arg2: Optional[str] = None, session_id: Optional[str] = None) -> str:
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

    return session.run_command(cmd)


@mcp.tool()
def generate_signature(address_or_symbol: str, length: int = 32, session_id: Optional[str] = None) -> str:
    """[DebugExt] Generate relocatable AOB signature with wildcards (makesig) or search pattern (findsig)."""
    session = get_session(session_id)
    return session.run_command(f"makesig {address_or_symbol} {length}")


@mcp.tool()
def scan_hooks_and_injections(audit_type: str = "hooks", module_name: Optional[str] = None, session_id: Optional[str] = None) -> str:
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

    return session.run_command(cmd)


@mcp.tool()
def audit_pe_security(target: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """[DebugExt] Audit PE headers, ASLR/DEP/CFG mitigations, PEB anti-debug flags, and TEB stack limits (pe/peb/teb)."""
    session = get_session(session_id)
    cmd = f"pe {target}" if target else "pe"
    return session.run_command(cmd)


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

def run_server():
    """Run the FastMCP server on stdio."""
    mcp.run()


if __name__ == "__main__":
    run_server()
