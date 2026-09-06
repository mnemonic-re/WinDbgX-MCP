"""User-mode CDB session management (Crash Dumps, Remote Servers, and Live Process Attach)."""

from __future__ import annotations

import os
import uuid
from typing import List, Optional

from windbg_mcp.debug_session import DebugSession, DebuggerError


def find_cdb_executable() -> str:
    """Locate cdb.exe in system PATH or Windows Kits directories."""
    # Check PATH
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path_dir, "cdb.exe")
        if os.path.isfile(candidate):
            return candidate

    # Check default Windows Kits locations
    kits_dirs = [
        r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe",
        r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\cdb.exe",
        r"C:\Program Files\Windows Kits\10\Debuggers\x64\cdb.exe",
    ]

    for candidate in kits_dirs:
        if os.path.isfile(candidate):
            return candidate

    return "cdb.exe"  # Fallback to PATH lookup


def open_cdb_dump_session(
    dump_path: str,
    symbols_path: Optional[str] = None,
    include_stack: bool = True,
    include_modules: bool = True,
    timeout_seconds: float = 180.0,
) -> tuple[str, DebugSession]:
    """Launch cdb.exe to analyze a crash dump (.dmp) file."""
    if not os.path.isfile(dump_path):
        raise DebuggerError(f"Crash dump file not found: '{dump_path}'")

    cdb_bin = find_cdb_executable()
    cmd_args = [cdb_bin, "-z", dump_path]

    if symbols_path:
        cmd_args.extend(["-y", symbols_path])

    session_id = f"cdb-dump-{uuid.uuid4().hex[:8]}"
    session = DebugSession(session_id, debugger_type="cdb")

    try:
        initial_output = session.start(cmd_args, timeout_seconds=timeout_seconds)

        # Initial crash dump triage
        triage_cmd = ".lastevent; !analyze -v"
        if include_stack:
            triage_cmd += "; kb"
        if include_modules:
            triage_cmd += "; lm"

        triage_output = session.run_command(triage_cmd, timeout_seconds=timeout_seconds)
        full_output = f"session_id: {session_id}\n\n=== INITIAL BANNER ===\n{initial_output}\n=== INITIAL TRIAGE ===\n{triage_output}"

        return full_output, session
    except Exception as e:
        session.close()
        raise DebuggerError(f"Failed to initialize dump session: {e}") from e


def open_cdb_remote_session(
    connection_string: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 60.0,
) -> tuple[str, DebugSession]:
    """Attach cdb.exe to a remote user-mode debug server (-remote)."""
    cdb_bin = find_cdb_executable()
    cmd_args = [cdb_bin, "-remote", connection_string]

    if symbols_path:
        cmd_args.extend(["-y", symbols_path])

    session_id = f"cdb-remote-{uuid.uuid4().hex[:8]}"
    session = DebugSession(session_id, debugger_type="cdb")

    output = session.start(cmd_args, timeout_seconds=timeout_seconds)
    full_output = f"session_id: {session_id}\n\n{output}"

    return full_output, session


def attach_live_process_session(
    target: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 60.0,
) -> tuple[str, DebugSession]:
    """Attach cdb.exe to a live running process by PID or image name."""
    cdb_bin = find_cdb_executable()
    cmd_args = [cdb_bin]

    if target.isdigit():
        cmd_args.extend(["-p", target])
    else:
        cmd_args.extend(["-pn", target])

    if symbols_path:
        cmd_args.extend(["-y", symbols_path])

    session_id = f"cdb-attach-{uuid.uuid4().hex[:8]}"
    session = DebugSession(session_id, debugger_type="cdb")

    output = session.start(cmd_args, timeout_seconds=timeout_seconds)
    full_output = f"session_id: {session_id}\n\n{output}"

    return full_output, session
