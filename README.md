# WinDbgMCP

Model Context Protocol (MCP) server for **WinDbg** & **WinDbgX**, custom-built for **Google Antigravity**, Claude Code, Cursor, Windsurf, VS Code, OpenAI / OpenAI-Compatible frameworks, and Local LLMs (Ollama / LM Studio).

WinDbgMCP bridges AI coding assistants directly into live Windows debugging sessions (user-mode, kernel-mode, remote targets, and crash dumps), pairing standard debugger automation with custom reverse-engineering superpowers ported from **DebugExt** (`de.dll`).

---

## Quick Start (Automated Bootstrap)

Automate all environment checks, debugger binary discovery (`cdb.exe`/`kd.exe`), symbol directory creation (`C:\Symbols`), and auto-register WinDbgMCP into all local AI client configurations with a single command:

```bash
python scripts/install_mcp.py
```
*(or `python -m windbg_mcp.bootstrap`)*

---

## Capabilities Overview

- **Unrestricted WinDbg Command Passthrough**:
  - AI agents can execute **ANY** native command, meta-command, or bang extension via `run_cdb_command` or `run_kd_command` (`k`, `r`, `u`, `dt`, `!process`, `!thread`, `!heap`, `!address`, `bp`, `ba`, `.reload`, etc.).
- **4 Connection Modes**:
  - Crash Dump Triage (`open_cdb_dump`)
  - User-Mode Remote Server (`open_cdb_remote`)
  - Kernel Debugging Target (`open_kd_session` via KDNET, VM Pipe, Serial)
  - Live Local Process Attach (`attach_live_process` by PID or Process Name)
- **Multi-Session Orchestration**:
  - Debug user-mode processes and kernel drivers concurrently (`list_sessions`, `switch_session`).
- **Google Antigravity Visual Artifact Tools**:
  - **`render_control_flow_graph`**: Disassembles target functions into basic blocks and outputs native **Mermaid flowcharts (`graph TD`)** rendered visually in Antigravity artifacts.
  - **`dump_memory_visual`**: Formatted hex/ASCII byte tables with symbol annotations.
  - **`dump_rwx_payload`**: Dumps unpacked dynamic memory buffers to disk for malware payload analysis.
- **Extended Reverse Engineering Tools (DebugExt Port)**:
  - Calling convention parameter inspection (`inspect_function_args`).
  - String reference scanner (`scan_string_references`).
  - Code XREF finder (`find_code_xrefs`).
  - Virtual memory protection auditor & RWX alerts (`audit_memory_regions`).
  - Static (Ghidra/PE-bear) <-> Live Memory offset converter (`translate_offset` for `rva`, `fo2va`, `va2fo`).
  - Relocatable AOB pattern generator (`generate_signature`).
  - Hook, injection & shellcode detector (`scan_hooks_and_injections`).
  - PE header, PEB anti-debug & TEB stack audit (`audit_pe_security`).

---

## Multi-Client Setup (`configs/`)

WinDbgMCP ships with ready-to-use configuration files under `configs/`:

- **Google Antigravity & Claude Code**: `configs/antigravity.mcp.json` or root `mcp.json`
- **Claude Desktop**: `configs/claude_desktop.json`
- **Cursor**: `configs/cursor.mcp.json`
- **Windsurf**: `configs/windsurf.mcp.json`
- **VS Code / Roo Code / Continue**: `configs/vscode_mcp.json`
- **OpenAI & OpenAI-Compatible (OpenRouter, vLLM, LiteLLM)**: `configs/openai_agents.json`
- **Local LLMs (Ollama, LM Studio, Jan, LocalAI)**: `configs/local_ollama_lmstudio.json`

---

## Tool Reference Catalog

| Tool | Category | Description |
| :--- | :--- | :--- |
| `list_sessions` | Session | Enumerate open sessions & active default session |
| `switch_session` | Session | Switch active default session by `session_id` |
| `list_dumps` | Session | Enumerate `.dmp` crash dump files with file metadata |
| `open_cdb_dump` | Session | Open crash dump & run initial triage (`!analyze -v`, `kb`, `lm`) |
| `open_cdb_remote` | Session | Connect to user-mode remote debugger server (`tcp`, `npipe`, `com`) |
| `open_kd_session` | Session | Attach to kernel target via KDNET (`net`), VM Pipe (`com:pipe`), or Serial |
| `attach_live_process` | Session | Attach `cdb.exe` to a live running process by PID or name |
| `close_session` | Session | Safely close debugging session (supports `resume=true` for kernel) |
| `run_cdb_command` | Execution | Execute ANY user-mode command (`k`, `r`, `u`, `dt`, `!heap`, etc.) |
| `run_kd_command` | Execution | Execute ANY kernel-mode command (`!process 0 0`, `!thread`, `vertarget`) |
| `send_ctrl_break` | Execution | Interrupt running target & resynchronize debugger prompt |
| `wait_for_break` | Execution | Asynchronously block until target halts on a breakpoint or exception |
| `render_control_flow_graph`| Visual | Build native Mermaid CFG diagram (`graph TD`) for Antigravity artifacts |
| `dump_memory_visual` | Visual | Format memory bytes in clean hex/ASCII markdown tables |
| `dump_rwx_payload` | Visual | Dump unpacked memory regions/shellcode to disk files |
| `inspect_function_args`| DebugExt | Inspect live fastcall/stdcall parameters & string/symbol previews |
| `scan_string_references`| DebugExt | Scan module code/data for ASCII and UTF-16 strings (`strref`) |
| `find_code_xrefs` | DebugExt | Locate code references (`CALL`, `JMP`, `RIP-rel`) to target address |
| `audit_memory_regions`| DebugExt | Audit virtual memory protection states & flag RWX regions (`memmap`) |
| `translate_offset` | DebugExt | Convert RVA, Raw File Offset (fo2va), or VA to File Offset (va2fo) |
| `generate_signature` | DebugExt | Generate relocatable byte pattern signature (`makesig`) |
| `scan_hooks_and_injections`| DebugExt| Detect inline detours, IAT hooks, driver IRP table hooks, shellcode |
| `audit_pe_security` | DebugExt | Audit PE headers, ASLR/DEP/CFG, PEB anti-debug, & TEB stack limits |
