"""Core debugger subprocess driver for CDB / KD session management.

Manages process creation, stdout/stderr background reader threads,
monotonic sequence markers for command completion detection,
CTRL+BREAK signals for breaking into running targets, and
async execution state resynchronization.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import threading
import time
from typing import List, Optional

from windbg_mcp.filter import sanitize_debug_output

# Regex for CDB/KD prompt lines (e.g. 0:000>, 3: kd>)
PROMPT_REGEX = re.compile(r"^\d+:.*>\s*$")

# Base completion marker string
MARKER_BASE = "COMMAND_COMPLETED_MARKER"

# Commands that resume target execution (g-class)
RESUME_COMMANDS = {"g", "gh", "gn", "gc", "gu", "p", "t", "pa", "ta"}


class DebuggerError(Exception):
    """Raised when a debugger session fails or encounters an unrecoverable error."""


class DebugSession:
    """Manages an active cdb.exe or kd.exe debugger process."""

    def __init__(self, session_id: str, debugger_type: str = "cdb"):
        self.session_id = session_id
        self.debugger_type = debugger_type  # "cdb" or "kd"
        self.process: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()
        self.output_buffer: List[str] = []
        self.reader_thread: Optional[threading.Thread] = None
        self.sequence_number = 0
        self.is_running_target = False
        self.closed = False

    @property
    def _seq(self) -> int:
        return self.sequence_number

    def _build_marker_command(self) -> str:
        """Increment sequence counter and build echo marker string."""
        self.sequence_number += 1
        return f".echo {MARKER_BASE}_{self.sequence_number}"

    def _is_resume_command(self, command: str) -> bool:
        """Check if command resumes execution without halting for output markers."""
        clean = command.strip()
        first_token = clean.split()[0].lower() if clean else ""
        return first_token in RESUME_COMMANDS

    def start(self, cmd_args: List[str], timeout_seconds: float = 60.0) -> str:
        """Launch the debugger process and await the initial prompt."""
        try:
            self.process = subprocess.Popen(
                cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            )
        except Exception as e:
            raise DebuggerError(f"Failed to launch debugger binary '{cmd_args[0]}': {e}")

        self.reader_thread = threading.Thread(target=self._read_output_loop, daemon=True)
        self.reader_thread.start()

        # Wait for initial banner and prompt
        initial_output = self._wait_for_initial_prompt(timeout_seconds)
        
        # Load DebugExt (de.dll) automatically if available
        self._try_load_extension()

        return initial_output

    def _read_output_loop(self) -> None:
        """Background thread reading lines from debugger stdout."""
        if not self.process or not self.process.stdout:
            return

        for line in self.process.stdout:
            with self.lock:
                self.output_buffer.append(line)

    def _wait_for_initial_prompt(self, timeout_seconds: float) -> str:
        """Read output until the debugger reaches its first command prompt."""
        start_time = time.time()
        lines: List[str] = []

        while time.time() - start_time < timeout_seconds:
            if self.process and self.process.poll() is not None:
                raise DebuggerError(f"Debugger process terminated unexpectedly with code {self.process.returncode}")

            with self.lock:
                if self.output_buffer:
                    lines.extend(self.output_buffer)
                    self.output_buffer.clear()

            # Check if any line matches prompt
            full_text = "".join(lines)
            if any(PROMPT_REGEX.search(l) for l in lines[-5:]):
                return sanitize_debug_output(full_text)

            time.sleep(0.05)

        raise DebuggerError(f"Debugger timed out after {timeout_seconds}s waiting for initial prompt.")

    def _try_load_extension(self) -> None:
        """Attempt to load de.dll (DebugExt) automatically."""
        try:
            self.run_command(".load de", timeout_seconds=5.0)
        except Exception:
            pass  # Silent fallback if de.dll is not in search path

    def run_command(self, command: str, timeout_seconds: float = 60.0) -> str:
        """Execute a WinDbg command and return its full output."""
        if self.closed or not self.process or self.process.poll() is not None:
            raise DebuggerError(f"Session '{self.session_id}' is closed or debugger process died.")

        clean_cmd = command.strip()

        # Check if this is an execution resume command (e.g. 'g')
        if self._is_resume_command(clean_cmd):
            return self._run_resume_command(clean_cmd)

        self.sequence_number += 1
        seq_id = self.sequence_number
        marker = f"{MARKER_BASE}_{seq_id}"

        # Send command followed by echo marker
        full_payload = f"{clean_cmd}\n.echo {marker}\n"

        with self.lock:
            self.output_buffer.clear()

        try:
            if self.process.stdin:
                self.process.stdin.write(full_payload)
                self.process.stdin.flush()
        except Exception as e:
            raise DebuggerError(f"Failed to write payload to debugger stdin: {e}")

        # Await marker in stdout
        start_time = time.time()
        captured_lines: List[str] = []

        while time.time() - start_time < timeout_seconds:
            if self.process.poll() is not None:
                raise DebuggerError(f"Debugger exited while executing command '{clean_cmd}'.")

            with self.lock:
                if self.output_buffer:
                    captured_lines.extend(self.output_buffer)
                    self.output_buffer.clear()

            # Look for sequence marker in lines
            marker_found = False
            result_lines: List[str] = []

            for line in captured_lines:
                if marker in line:
                    marker_found = True
                    break
                result_lines.append(line)

            if marker_found:
                full_result = "".join(result_lines)
                return sanitize_debug_output(full_result)

            time.sleep(0.05)

        # Handle command timeout: send CTRL+BREAK to regain prompt
        self.send_ctrl_break()
        raise DebuggerError(f"Command '{clean_cmd}' timed out after {timeout_seconds}s. Target broke in with CTRL+BREAK.")

    def _run_resume_command(self, command: str) -> str:
        """Handle execution resume commands like 'g' without blocking on markers."""
        try:
            if self.process and self.process.stdin:
                self.process.stdin.write(f"{command}\n")
                self.process.stdin.flush()
                self.is_running_target = True
        except Exception as e:
            raise DebuggerError(f"Failed to send resume command '{command}': {e}")

        time.sleep(0.1)
        return sanitize_debug_output(f"[Target Resumed Execution] Executed '{command}'. Use 'wait_for_break' or 'send_ctrl_break'.\n")

    def send_ctrl_break(self) -> str:
        """Send CTRL+BREAK to halt a running target."""
        if not self.process or self.process.poll() is not None:
            raise DebuggerError("Cannot send CTRL+BREAK: process is not active.")

        try:
            if os.name == "nt":
                # Send CTRL+BREAK via Windows API signal
                os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.kill(self.process.pid, signal.SIGINT)

            self.is_running_target = False
            time.sleep(0.2)
            return sanitize_debug_output("[CTRL+BREAK Sent] Target broke in. Debugger prompt ready.\n")
        except Exception as e:
            raise DebuggerError(f"Failed to send CTRL+BREAK: {e}")

    def wait_for_break(self, timeout_seconds: float = 300.0) -> str:
        """Asynchronously block until target halts on a breakpoint or exception."""
        start_time = time.time()
        lines: List[str] = []

        while time.time() - start_time < timeout_seconds:
            if self.process and self.process.poll() is not None:
                raise DebuggerError("Debugger process terminated while waiting for target break.")

            with self.lock:
                if self.output_buffer:
                    lines.extend(self.output_buffer)
                    self.output_buffer.clear()

            if any(PROMPT_REGEX.search(l) for l in lines[-5:]):
                self.is_running_target = False
                return sanitize_debug_output("".join(lines))

            time.sleep(0.1)

        return sanitize_debug_output(f"[Wait Timeout] Target still running after {timeout_seconds}s.\n")

    def close(self, resume_kernel: bool = True) -> str:
        """Close debugger process and cleanup handles."""
        if self.closed:
            return "Session already closed."

        self.closed = True
        if self.process and self.process.poll() is None:
            try:
                if self.debugger_type == "kd" and resume_kernel:
                    self.process.stdin.write("g\n.detach\nq\n")
                else:
                    self.process.stdin.write("q\n")
                self.process.stdin.flush()
                self.process.wait(timeout=3.0)
            except Exception:
                self.process.kill()

        return f"Session '{self.session_id}' closed successfully."
