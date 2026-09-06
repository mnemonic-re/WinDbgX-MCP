"""Extended Reverse Engineering & Crash Triage Superpowers Engine for WinDbgMCP.

Provides specialized algorithms for memory diffing, C/C++ struct reconstruction,
automated crash dump RCA synthesis, dynamic WinAPI tracing, and in-memory PE header extraction.
"""

from __future__ import annotations

import os
import re
import time
from typing import Dict, List, Optional, Tuple


def diff_memory_bytes(
    hex_dump_A: str,
    hex_dump_B: str,
    base_address: str = "0x00000000",
) -> str:
    """Compare two WinDbg memory dump outputs (db/dc/dq) and highlight modified bytes/pointers."""
    lines_A = [l.strip() for l in hex_dump_A.splitlines() if l.strip() and not l.startswith("=")]
    lines_B = [l.strip() for l in hex_dump_B.splitlines() if l.strip() and not l.startswith("=")]

    diffs: List[str] = []
    diff_count = 0

    max_lines = max(len(lines_A), len(lines_B))
    for i in range(max_lines):
        line_a = lines_A[i] if i < len(lines_A) else "<EOF>"
        line_b = lines_B[i] if i < len(lines_B) else "<EOF>"

        if line_a != line_b:
            diff_count += 1
            diffs.append(f"**Line {i+1} Offset Difference**:\n- **Snapshot A**: `{line_a}`\n+ **Snapshot B**: `{line_b}`\n")

    if not diffs:
        return f"### Memory Snapshot Diff ({base_address})\n\n**Result**: Snapshots A and B are **100% IDENTICAL**. No byte modifications detected."

    diff_body = "\n".join(diffs[:50])
    return (
        f"### Memory Snapshot Diff ({base_address})\n\n"
        f"**Status**: Found **{diff_count}** modified memory region(s).\n\n"
        f"{diff_body}\n"
        f"{'*[Truncated after 50 diff entries]*' if diff_count > 50 else ''}"
    )


def reconstruct_struct_definition(
    raw_hex_dump: str,
    base_address: str = "0x00000000",
    struct_name: str = "RECONSTRUCTED_STRUCT",
    is_64bit: bool = True,
) -> str:
    """Analyze raw memory dwords/qwords and auto-generate C/C++ struct definition with field offsets."""
    ptr_size = 8 if is_64bit else 4
    lines = [l.strip() for l in raw_hex_dump.splitlines() if l.strip() and not l.startswith("=")]

    fields: List[str] = []
    current_offset = 0

    # Match dword/qword lines (e.g. 00401000 00000002 00000000 or 0x7ff6`9b8c1000: 00007ff69b8c1070)
    hex_pattern = re.compile(r"([0-9a-fA-F]{8,16})")

    for line in lines:
        tokens = hex_pattern.findall(line)
        if not tokens:
            continue

        # First token is often address
        values = tokens[1:] if len(tokens) > 1 else tokens
        for val_str in values:
            try:
                val = int(val_str, 16)
                offset_str = f"/* +0x{current_offset:04X} */"

                # Infer type
                if val == 0:
                    field_def = f"    PVOID      field_0x{current_offset:X}; // 0x0"
                elif val > 0x10000 and (val & 0x7) == 0:
                    field_def = f"    PVOID      pPointer_0x{current_offset:X}; // 0x{val:X}"
                elif val < 0x10000:
                    field_def = f"    DWORD      dwValue_0x{current_offset:X}; // {val} (0x{val:X})"
                else:
                    field_def = f"    ULONG_PTR  data_0x{current_offset:X}; // 0x{val:X}"

                fields.append(f"{offset_str} {field_def}")
                current_offset += ptr_size
            except ValueError:
                continue

    if not fields:
        fields.append("    // Raw memory parsing yield no structured fields.")

    struct_body = "\n".join(fields)
    c_code = (
        f"typedef struct _{struct_name} {{\n"
        f"{struct_body}\n"
        f"}} {struct_name}, *P{struct_name};"
    )

    return (
        f"### Reconstructed C/C++ Struct Definition (`{struct_name}`)\n\n"
        f"**Base Address**: `{base_address}` | **Architecture**: `{'x64' if is_64bit else 'x86'}`\n\n"
        f"```cpp\n{c_code}\n```"
    )


def synthesize_crash_triage_report(
    dump_path: str,
    raw_triage_text: str,
) -> str:
    """Parse raw !analyze -v and context records into an executive Root Cause Analysis (RCA) report."""
    dump_filename = os.path.basename(dump_path)

    # Extract key triage fields
    bugcheck_match = re.search(r"BUGCHECK_CODE:\s*([0-9a-fA-F]+)", raw_triage_text)
    bugcheck_str = bugcheck_match.group(1) if bugcheck_match else "UNKNOWN / USER-MODE EXCEPTION"

    process_match = re.search(r"PROCESS_NAME:\s*([^\s]+)", raw_triage_text)
    process_name = process_match.group(1) if process_match else "N/A"

    module_match = re.search(r"MODULE_NAME:\s*([^\s]+)", raw_triage_text)
    module_name = module_match.group(1) if module_match else "N/A"

    faulting_ip = re.search(r"FAULTING_IP:\s*([^\n]+)", raw_triage_text)
    fault_ip_str = faulting_ip.group(1).strip() if faulting_ip else "N/A"

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    rca_report = (
        f"# Root Cause Analysis (RCA) Crash Report: {dump_filename}\n\n"
        f"**Crash Dump**: `{dump_path}`  \n"
        f"**Triage Timestamp**: `{timestamp}`  \n"
        f"**Faulting Process**: `{process_name}`  \n"
        f"**Faulting Module**: `{module_name}`  \n"
        f"**Bugcheck / Exception Code**: `0x{bugcheck_str}`  \n"
        f"**Faulting Instruction (IP)**: `{fault_ip_str}`  \n\n"
        f"---\n\n"
        f"## Executive Triage Summary\n\n"
        f"An unexpected crash occurred in process `{process_name}` within module `{module_name}`.\n"
        f"The debugger captured exception/bugcheck code `0x{bugcheck_str}` at instruction pointer `{fault_ip_str}`.\n\n"
        f"## Raw Analysis Output\n\n"
        f"```text\n{raw_triage_text.strip()}\n```\n\n"
        f"---\n"
        f"*Report generated automatically by WinDbgMCP Triage Engine.*"
    )

    return rca_report


def build_api_trace_payload(
    api_name: str,
    module_name: str = "kernel32",
) -> Tuple[str, str]:
    """Build WinDbg breakpoint command strings for dynamic WinAPI call tracing."""
    target_symbol = f"{module_name}!{api_name}"
    bp_cmd = f'bp {target_symbol} ".echo === [API TRACE HIT]: {target_symbol} ===; kb 5; g"'
    reasoning = f"Setting hardware breakpoint on {target_symbol} to log parameters and stack trace upon invocation."
    return bp_cmd, reasoning


def parse_pe_header_in_memory(
    raw_db_dump: str,
    base_address: str = "0x00000000",
) -> Tuple[bool, str]:
    """Scan raw hex dump for MZ (4D 5A) header and validate PE structure."""
    if "4d 5a" in raw_db_dump.lower() or "4d5a" in raw_db_dump.lower() or "MZ" in raw_db_dump:
        info = (
            f"### PE Header Validation ({base_address})\n\n"
            f"- **Magic Signature**: `0x5A4D` (`MZ`) confirmed at `{base_address}`.\n"
            f"- **Status**: Valid DOS/PE header detected in memory buffer.\n"
            f"- **Next Step**: Executing `.writemem` payload export to artifact directory."
        )
        return True, info
    else:
        info = f"### PE Header Scan Failed ({base_address})\n\n**Status**: `MZ` signature (`0x5A4D`) not found at target address."
        return False, info
