"""Kernel-mode KD session management (KDNET, VM Named Pipes, Serial)."""

from __future__ import annotations

import os
import uuid
from typing import Optional

from windbg_mcp.debug_session import DebugSession, DebuggerError


def find_kd_executable() -> str:
    """Locate kd.exe in system PATH or Windows Kits directories."""
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path_dir, "kd.exe")
        if os.path.isfile(candidate):
            return candidate

    kits_dirs = [
        r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\kd.exe",
        r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\kd.exe",
        r"C:\Program Files\Windows Kits\10\Debuggers\x64\kd.exe",
    ]

    for candidate in kits_dirs:
        if os.path.isfile(candidate):
            return candidate

    return "kd.exe"


def open_kd_session(
    connection_string: str,
    symbols_path: Optional[str] = None,
    timeout_seconds: float = 120.0,
) -> tuple[str, DebugSession]:
    """Attach kd.exe to a kernel debugging target (-k)."""
    kd_bin = find_kd_executable()
    cmd_args = [kd_bin, "-k", connection_string]

    if symbols_path:
        cmd_args.extend(["-y", symbols_path])

    session_id = f"kd-{uuid.uuid4().hex[:8]}"
    session = DebugSession(session_id, debugger_type="kd")

    output = session.start(cmd_args, timeout_seconds=timeout_seconds)
    full_output = f"session_id: {session_id}\n\n{output}"

    return full_output, session
