# Developer Guide for WinDbgMCP

## Environment & Build Setup
- **Python**: Python 3.11+ required.
- **Dependencies**: `mcp[cli]`, `pydantic`.
- **Run Server**: `python -m windbg_mcp`
- **Run Tests**: `python -m unittest discover -s tests`

## System Environment Variables
- `_NT_SYMBOL_PATH`: `srv*C:\Symbols*https://msdl.microsoft.com/download/symbols`
- `_NT_DEBUGGER_EXTENSION_PATH`: Path to `de.dll` build output (`DebugExt\x64\Release`)

## Core Architecture
- `src/windbg_mcp/server.py`: FastMCP server entry point, registering 18+ tools, 4 prompts, and multi-session state.
- `src/windbg_mcp/debug_session.py`: `DebugSession` subprocess driver managing sequence markers (`COMMAND_COMPLETED_MARKER_<n>`), execution resumption, and `CTRL+BREAK` signaling.
- `src/windbg_mcp/cdb_session.py`: User-mode crash dump, remote server, and live process attach drivers.
- `src/windbg_mcp/kd_session.py`: Kernel-mode debugger driver for KDNET, VM pipe, and serial targets.
- `src/windbg_mcp/cfg_builder.py`: Basic block parser and Mermaid flowchart generator (`graph TD`) for Antigravity visual rendering.
- `src/windbg_mcp/filter.py`: PII, token, and IP address output sanitizer.

## Design Rules
1. **Never block on resume commands**: `g`, `gh`, `gn`, `gc`, `gu` must return immediately without waiting for sequence echo markers.
2. **Monotonic Markers**: All non-resume commands append `.echo COMMAND_COMPLETED_MARKER_<seq_id>` to ensure output isolation.
3. **Session Cleanup**: Always register `atexit` handlers so orphaned `cdb.exe`/`kd.exe` processes are terminated on shutdown.
