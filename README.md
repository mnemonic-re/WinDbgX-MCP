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

## Live GUI Progress Watching & AI Intent Streaming

If you want to watch AI debugging progress live on your desktop inside the graphical **WinDbg GUI** (`WinDbgX` / `DbgX.Shell.exe`):

1. Launch **WinDbg GUI** on desktop, open your target executable or attach to your process.
2. In the WinDbg GUI command bar at the bottom, type:
   ```text
   .server tcp:port=5005
   ```
3. Ask your AI assistant to connect:
   ```python
   open_cdb_remote(connection_string="tcp:Port=5005,Server=localhost")
   ```
4. **Live AI Intent Streaming**: MCP execution tools support an optional `reasoning` parameter. When passed, WinDbgMCP streams `=== [AI INTENT]: <reasoning> ===` banners live into the WinDbg console right before command execution.
5. **Milestone Banners**: The AI can write prominent double-bordered block banners into WinDbg GUI using `annotate_session(milestone="...")` for major phase shifts.

*The AI assistant will drive the session remotely while every step and reasoning banner executes live before your eyes in your WinDbg GUI window!*

---

## Transport Modes: `stdio` (IPC) vs `sse` (Network HTTP)

WinDbgMCP supports two transport protocols:

1. **Stdio Mode (Default)**:
   - Launched automatically by desktop AI clients (Antigravity, Claude, Cursor) as a local background process via stdin/stdout.
   - Zero network overhead, zero firewall prompts, 100% local IPC.
   ```bash
   python -m windbg_mcp
   ```

2. **SSE HTTP Network Mode (`--sse`)**:
   - Spins up a web server listening on a TCP port (e.g. `8000`) for remote debugging, web-based LLM apps, or cross-machine AI execution.
   ```bash
   python -m windbg_mcp --sse --port 8000
   ```

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

> [!NOTE]
> **Machine-Independent Path Resolution**: WinDbgMCP automatically resolves all environment paths (`_NT_SYMBOL_PATH`, `_NT_DEBUGGER_EXTENSION_PATH`, Python binaries) dynamically using Windows environment variables (`%USERPROFILE%`, `%LOCALAPPDATA%`, `%SystemDrive%`, `%ProgramFiles%`) without hardcoding personal user directory names or hostnames.

---

## Supported Models Catalog (Frontier & Free Tier)

WinDbgMCP supports dynamic resolution for all modern LLM providers:

- **Google Gemini**: `gemini-3.5-flash` *(Recommended)*, `gemini-3.5-flash-lite`, `gemini-3.6-flash`, `gemini-3.7-flash`, `gemini-3.1-pro-preview`, `gemini-2.5-pro`
- **OpenAI Frontier**: `gpt-5.6`, `gpt-5.5`, `gpt-5`, `gpt-4.5`, `gpt-4o`
- **Anthropic Frontier**: `claude-5-opus`, `claude-4.5-sonnet`, `claude-4-opus`, `claude-3-7-sonnet`, `claude-3-5-sonnet-20241022`
- **Mistral AI**: `codestral-latest`, `mistral-large-latest`, `mistral-small-latest`
- **Groq & Cerebras**: `deepseek-r1-distill-llama-70b`, `kimi-k2-instruct`, `llama-3.3-70b-versatile`, `gpt-oss-120b`
- **OpenRouter Free Tier Examples**:
  - `nvidia/nemotron-3-nano-30b-a3b:free`
  - `google/gemma-4-31b-it:free`
  - `poolside/laguna-s-2.1:free`
  - `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`
  - `nvidia/nemotron-3-super-120b-a12b:free`
  - `nvidia/nemotron-3-ultra-550b-a55b:free`
  - `openai/gpt-oss-20b:free`
- **Ollama Cloud & Local AI (LM Studio)**: `qwen3-coder`, `gpt-oss:120b`, `qwen2.5-coder-14b-instruct-abliterated@q5_k_m`, `codestral-22b-v0.1-abliterated-v3`

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
| `annotate_session` | Execution | Write prominent milestone/reasoning block banners into WinDbg GUI |
| `send_ctrl_break` | Execution | Interrupt running target & resynchronize debugger prompt |
| `wait_for_break` | Execution | Asynchronously block until target halts on a breakpoint or exception |
| `render_control_flow_graph`| Visual | Build native Mermaid CFG diagram (`graph TD`) for Antigravity artifacts |
| `dump_memory_visual` | Visual | Format memory bytes in clean hex/ASCII markdown tables |
| `dump_rwx_payload` | Visual | Dump unpacked memory regions/shellcode to disk files |
| `update_scratchpad` | Reporting | Append live notes/traces to `analysis/<FILE_NAME>/mds/scratchpad.md` |
| `generate_final_report`| Reporting | Synthesize scratchpad into `analysis/<FILE_NAME>/mds/<FILE_NAME>_Final_Report.md` |
| `inspect_function_args`| DebugExt | Inspect live fastcall/stdcall parameters & string/symbol previews |
| `scan_string_references`| DebugExt | Scan module code/data for ASCII and UTF-16 strings (`strref`) |
| `find_code_xrefs` | DebugExt | Locate code references (`CALL`, `JMP`, `RIP-rel`) to target address |
| `audit_memory_regions`| DebugExt | Audit virtual memory protection states & flag RWX regions (`memmap`) |
| `translate_offset` | DebugExt | Convert RVA, Raw File Offset (fo2va), or VA to File Offset (va2fo) |
| `generate_signature` | DebugExt | Generate relocatable byte pattern signature (`makesig`) |
| `scan_hooks_and_injections`| DebugExt| Detect inline detours, IAT hooks, driver IRP table hooks, shellcode |
| `audit_pe_security` | DebugExt | Audit PE headers, ASLR/DEP/CFG, PEB anti-debug, & TEB stack limits |
| `diff_memory_snapshots` | Superpower | Compare byte regions, page protection, and pointers between two memory snapshots |
| `triage_crash_report` | Superpower | Automated BSOD & crash dump root-cause analyzer (RCA) |
| `reconstruct_struct` | Superpower | Auto-reconstruct C/C++ struct definitions & ReClass.NET schemas from memory |
| `trace_api_calls` | Superpower | Generate WinAPI tracing breakpoint sets & argument interception payloads |
| `unpack_dynamic_pe` | Superpower | Scan dynamic memory for PE signatures (MZ/PE), validate headers, & export payloads |
| `audit_kernel_integrity` | Superpower | Audit kernel EPROCESS lists, SSDT tables, & driver dispatch arrays for DKOM & rootkits |
| `scan_stack_spoofing` | Superpower | Inspect thread stack frames for unbacked return addresses, alignment anomalies, & ROP chains |
| `find_rop_gadgets` | Superpower | Scan executable modules for ROP gadgets (pop rcx; ret, mov [rax], rbx, stack pivots) |
| `audit_heap_corruption` | Superpower | Automate !heap -p -a & Pageheap diagnostics to pinpoint corrupted chunk headers & UAF bugs |
| `get_ai_provider_status` | AI Management | Scan 11 AI providers (Gemini, OpenAI, Anthropic, etc.) & env setup status |
| `configure_ai_provider` | AI Management | Initialize & validate AI provider config from environment variables |

---

## Operational & Setup Guides

- **[AI Provider Setup & Environment Guide](guides/AI_Provider_Setup_Guide.md)**: Detailed configuration for Google Gemini, OpenAI, Anthropic, Mistral, Groq, Cerebras, Ollama, LM Studio, and OpenRouter outside of IDEs (PowerShell, CMD, Bash) and inside MCP host JSONs.
- **[AI Operational & Reversing Guide](guides/AI_Guide.md)**: Workspace directory hygiene rules (`analysis/<TARGET>/`), token-efficient live reversing protocols, and command reference catalogs.
- **[Advanced Usage & Multi-Session Guide](guides/Advanced_Usage_Guide.md)**: Full architecture guide for remote CDB servers, kernel debugging, and multi-client setups.

