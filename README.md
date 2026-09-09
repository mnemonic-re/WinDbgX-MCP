# WinDbgMCP

> [!IMPORTANT]
> **DEVELOPMENT NOTICE**: WinDbgMCP & DebugExt (`de.dll`) are under active development. **Pull Requests (PRs) are currently CLOSED**. However, feedback and **Issues** are welcome — please report bugs or feature suggestions on GitHub Issues! Visit our [GitHub Wiki](https://github.com/mnemonic-re/WinDbgX-MCP/wiki) for full documentation, command catalogs, and setup guides.


> [!CAUTION]
> **CRITICAL SECURITY LOCK**: The master driver [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md) is set to **Read-Only** by default to prevent prompt injection and unauthorized modification during live AI debugging sessions. If you need to edit master directives:
> 1. Unlock: `attrib -r SYSTEM_PROMPT.md` *(or `(Get-Item SYSTEM_PROMPT.md).IsReadOnly = $false` in PowerShell)*
> 2. Make your edits and save.
> 3. Re-lock for security: `attrib +r SYSTEM_PROMPT.md` *(or `(Get-Item SYSTEM_PROMPT.md).IsReadOnly = $true`)*

Model Context Protocol (MCP) server for **WinDbg** & **WinDbgX**, custom-built for **Google Antigravity**, Claude Code, Cursor, Codex, Cline, Windsurf, VS Code, OpenAI / OpenAI-Compatible frameworks, and Local LLMs (Ollama / LM Studio).

WinDbgMCP bridges AI coding assistants directly into live Windows debugging sessions (user-mode, kernel-mode, remote targets, and crash dumps), pairing standard debugger automation with advanced reverse-engineering analysis engines ported from **DebugExt** (`de.dll`).

---

## Installation & Distribution

WinDbgMCP is distributed as a self-contained Python package bundling pre-compiled native `de.dll` binaries (x64 and x86). No C++ compiler or manual path configuration required.

### Option 1: Direct Pip Wheel Installation (Pre-built Package)
Install the pre-built `.whl` package directly via `pip`:
```bash
pip install https://raw.githubusercontent.com/mnemonic-re/WinDbgX-MCP/main/WinDbgMCP/dist/windbg_mcp-0.1.0-py3-none-any.whl
```
*(Or install locally if you cloned the repository: `pip install dist/windbg_mcp-0.1.0-py3-none-any.whl`)*

### Option 2: Install from GitHub Repository Source
```bash
pip install git+https://github.com/mnemonic-re/WinDbgX-MCP.git#subdirectory=WinDbgMCP
```

### Option 3: Global Command Line Entry Point
Once installed, launch the MCP server binary from any terminal or AI client host configuration:
```bash
windbg-mcp --help
```

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

## 📖 Real-World Case Study & Tool Usage Example

For a complete end-to-end demonstration of **WinDbgMCP** tool usage — featuring an AI agent performing automated assembly disassembly, algorithm extraction, key calculation for `GigaApp.exe`, and live visual stepping — read our published research article:

👉 **[WinDbgX-MCP AI Reverse Engineering Protocol (GigaApp Case Study)](https://mnemonic-re.github.io/research-notebook/research/windbgx-mcp-ai-reverse-engineering-protocol/)**

---

## Transport Modes: `stdio` (IPC) vs `sse` (Network HTTP)

WinDbgMCP supports two transport protocols:

1. **Stdio Mode (Default)**:
   - Launched automatically by desktop AI clients (Antigravity, Claude, Cursor, Codex, Cline) as a local background process via stdin/stdout.
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
  - Kernel Debugging Target (`open_kd_session_tool` via KDNET, VM Pipe, Serial)
  - Live Local Process Attach (`attach_live_process` by PID or Process Name)
- **Multi-Session Orchestration**:
  - Debug user-mode processes and kernel drivers concurrently (`list_sessions`, `switch_session`).
- **Google Antigravity Visual Artifact Tools**:
  - **`render_control_flow_graph`**: Disassembles target functions into basic blocks and outputs native **Mermaid flowcharts (`graph TD`)** rendered visually in Antigravity artifacts.
  - **`dump_memory_visual`**: Formatted hex/ASCII byte tables with symbol annotations.
  - **`dump_rwx_payload`**: Dumps unpacked dynamic memory buffers to disk for malware payload analysis.
- **Extended Reverse Engineering & Analysis Engines**:
  - Calling convention parameter inspection (`inspect_function_args`).
  - String reference scanner (`scan_string_references`).
  - Code XREF finder (`find_code_xrefs`).
  - Virtual memory protection auditor & RWX alerts (`audit_memory_regions`).
  - Static (Ghidra/PE-bear) <-> Live Memory offset converter (`translate_offset` for `rva`, `fo2va`, `va2fo`).
  - Relocatable AOB pattern generator (`generate_signature`).
  - Hook, injection & shellcode detector (`scan_hooks_and_injections`).
  - PE header, PEB anti-debug & TEB stack audit (`audit_pe_security`).
  - Memory snapshot byte & pointer diffing (`diff_memory_snapshots`).
  - Automated BSOD & crash dump Root Cause Analysis (`triage_crash_report`).
  - Dynamic C/C++ struct & offset reconstructor (`reconstruct_struct`).
  - Dynamic WinAPI tracing payload generator (`trace_api_calls`).
  - Dynamic PE header scanner & payload unpacker (`unpack_dynamic_pe`).
  - Kernel EPROCESS lists, SSDT & driver dispatch auditor (`audit_kernel_integrity`).
  - Thread callstack unbacked return address & spoofing scanner (`scan_stack_spoofing`).
  - Automated ROP gadget finder & categorizer (`find_rop_gadgets`).
  - Heuristic heap corruption & UAF detector (`audit_heap_corruption`).

---

## Multi-Client Setup (`configs/`)

WinDbgMCP ships with ready-to-use configuration files under `configs/`:

- **Google Antigravity & Claude Code**: `configs/antigravity.mcp.json` or root `mcp.json`
- **Claude Desktop**: `configs/claude_desktop.json`
- **Cursor**: `configs/cursor.mcp.json`
- **Codex**: `configs/codex.mcp.json`
- **Cline (VS Code)**: `configs/cline.mcp.json`
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

## Complete WinDbgMCP FastMCP Tool Reference (38 Tools)

| Tool Name | Category | Description |
| :--- | :--- | :--- |
| **`list_sessions`** | Session | Enumerate all open sessions & indicate active default session. |
| **`switch_session`** | Session | Switch active default session by `session_id`. |
| **`list_dumps`** | Session | Enumerate `.dmp` crash dump files with file metadata. |
| **`open_cdb_dump`** | Session | Open crash dump & run initial triage (`!analyze -v`, `kb`, `lm`). |
| **`open_cdb_remote`** | Session | Connect to user-mode remote debugger server (`tcp`, `npipe`, `com`). |
| **`open_kd_session_tool`** | Session | Attach to kernel target via KDNET (`net`), VM Pipe (`com:pipe`), or Serial. |
| **`attach_live_process`** | Session | Attach `cdb.exe` to a live running process by PID or executable name. |
| **`close_session`** | Session | Safely close debugging session (supports `resume=true` for kernel targets). |
| **`run_cdb_command`** | Execution | Execute ANY user-mode command (`k`, `r`, `u`, `dt`, `!heap`, etc.). |
| **`run_kd_command`** | Execution | Execute ANY kernel-mode command (`!process 0 0`, `!thread`, `vertarget`). |
| **`annotate_session`** | Execution | Write prominent milestone/reasoning block banners into WinDbg GUI console. |
| **`send_ctrl_break`** | Execution | Interrupt running target & resynchronize debugger prompt. |
| **`wait_for_break`** | Execution | Asynchronously block until target halts on a breakpoint or exception. |
| **`render_control_flow_graph`**| Visual | Build native Mermaid CFG diagram (`graph TD`) for Antigravity visual rendering. |
| **`dump_memory_visual`** | Visual | Format memory bytes in clean hex/ASCII markdown tables with symbol labels. |
| **`dump_rwx_payload`** | Visual | Dump unpacked memory regions/shellcode to local disk files. |
| **`update_scratchpad`** | Reporting | Append live notes/traces to `analysis/<TARGET>/mds/scratchpad.md`. |
| **`generate_final_report`**| Reporting | Synthesize scratchpad into `analysis/<TARGET>/mds/<TARGET>_Final_Report.md`. |
| **`update_analysis_report`** | Reporting | Append technical analysis section to target scratchpad log. |
| **`inspect_function_args`**| DebugExt | Inspect live fastcall/stdcall parameters & string/symbol previews. |
| **`scan_string_references`**| DebugExt | Scan module code/data for ASCII and UTF-16 strings (`strref`). |
| **`find_code_xrefs`** | DebugExt | Locate code references (`CALL`, `JMP`, `RIP-rel`) to target address (`xrefs`). |
| **`audit_memory_regions`**| DebugExt | Audit virtual memory protection states & flag RWX pages (`memmap`). |
| **`translate_offset`** | DebugExt | Convert RVA, Raw File Offset (`fo2va`), or VA to File Offset (`va2fo`). |
| **`generate_signature`** | DebugExt | Generate relocatable byte pattern signature (`makesig` / `findsig`). |
| **`scan_hooks_and_injections`**| DebugExt| Detect inline detours, IAT hooks, driver IRP table hooks, and shellcode. |
| **`audit_pe_security`** | DebugExt | Audit PE headers, ASLR/DEP/CFG, PEB anti-debug, & TEB stack limits. |
| **`diff_memory_snapshots`** | Analysis Engine | Compare byte regions, page protection, and pointers between two memory snapshots. |
| **`triage_crash_report`** | Analysis Engine | Automated BSOD & crash dump root-cause analyzer (RCA). |
| **`reconstruct_struct`** | Analysis Engine | Auto-reconstruct C/C++ struct definitions & ReClass.NET schemas from raw memory. |
| **`trace_api_calls`** | Analysis Engine | Generate WinAPI tracing breakpoint sets & argument interception payloads. |
| **`unpack_dynamic_pe`** | Analysis Engine | Scan dynamic memory for PE signatures (MZ/PE), validate headers, & export payloads. |
| **`audit_kernel_integrity`** | Analysis Engine | Audit kernel EPROCESS lists, SSDT tables, & driver dispatch arrays for DKOM & rootkits. |
| **`scan_stack_spoofing`** | Analysis Engine | Inspect thread stack frames for unbacked return addresses, alignment anomalies, & ROP chains. |
| **`find_rop_gadgets`** | Analysis Engine | Scan executable modules for ROP gadgets (pop rcx; ret, mov [rax], rbx, stack pivots). |
| **`audit_heap_corruption`** | Analysis Engine | Automate !heap -p -a & Pageheap diagnostics to pinpoint corrupted chunk headers & UAF bugs. |
| **`get_ai_provider_status`** | AI Management | Scan 11 AI providers (Gemini, OpenAI, Anthropic, etc.) & env setup status. |
| **`configure_ai_provider`** | AI Management | Initialize & validate AI provider config from environment variables. |

---

## DebugExt (`de.dll`) Complete Command Reference Catalog

Below is the complete reference catalog of ported bang (`!de.*`) commands provided by **DebugExt** (`de.dll`).

### Loading & Unloading `de.dll` in WinDbg / CDB:
- **Automatic Load**: `.load de` *(WinDbgMCP automatically configures `_NT_DEBUGGER_EXTENSION_PATH`)*
- **Explicit 64-bit Load**: `.load binaries\extensions\x64\de.dll`
- **Explicit 32-bit Load**: `.load binaries\extensions\x86\de.dll`
- **Unload**: `.unload de`
- **Interactive Help**: `!de.dxhelp`

```text
============================================================
 DebugExt - Analysis & Navigation Command Reference
============================================================

Navigation Shortcuts:
  si                         Step Into
  so                         Step Over
  su                         Step Out
  ret                        Run to RET
  toaddr <address>           Run to address
  tobranch                   Run to branch
  tocall                     Run to CALL

Utilities:
  !de.regs                          Display registers
  !de.disasm (dis / disasm)         Disassemble with DML colorization
  !de.lmod                          List loaded modules
  !de.dxhelp                        Display DebugExt help

Memory Inspection (x64dbg style):
  !de.dq (dqx <addr> [L-20])        DML QWord dump + ASCII + symbols/strings
  !de.dd (ddx <addr> [L-20])        DML DWord dump + ASCII + symbols/strings
  !de.db (dbx <addr> [L-20])        DML Byte dump + ASCII + dimmed nulls
  !de.dp (dpx / tele <addr> [L-20]) Telescoping pointer chain dump
  !de.dumpmem (dxx <addr> [L-20])   Smart architecture-aware memory dump

Function Analysis:
  !de.function                      Inspect current function
  !de.function <address>            Find function containing address
  !de.function <function>           Resolve function by symbol name

Call Graph & Stack Analysis:
  !de.bt (bt / callstack)           DML Callstack & parameter retriever
  !de.callees                       List callees of current function
  !de.callees <address>             List callees of function at address
  !de.callees <function>            List callees of named function
  !de.callers                       List callers of current function
  !de.callers <address>             List callers of function at address
  !de.callers <function>            List callers of named function

Hook & Security Scanner:
  !de.vtable (vtable <ptr> [cnt])   Inspect virtual method table & detours
  !de.hooks (hooks [module])        Scan module for inline / IAT detour hooks
  !de.injections (injections)       Scan unmapped executable pages / reflective DLLs
  !de.codecaves (codecaves [mod])   Scan module PE alignment gaps for code caves

PE & Windows Internals:
  !de.peb (peb)                     PEB anti-debug audit & process parameters
  !de.teb (teb)                     Thread Environment Block & stack limits
  !de.pe (pe <mod/addr>)            PE header & security mitigations audit (ASLR/DEP/CFG)

Advanced Reversing & Inspection (x64dbg style):
  !de.args (args / params)           Inspect live function calling convention parameters
  !de.strref (strref / strings) [mod] Scan module for ASCII & UTF-16 string references
  !de.xrefs (xrefs / xref) <target>  Find code cross-references (CALL/JMP/RIP-rel) to target
  !de.memmap (memmap / pages)        Virtual memory protection & commit map + RWX alert

Offsets & Address Translations:
  !de.gooffset (gooffset / rva) [mod] <off>  Go to RVA offset in module & disassemble
  !de.fo2va (fo2va / fileoffset / fo) <off>  Convert Raw Disk File Offset to live Virtual Address
  !de.va2fo (va2fo / offsetof / rvaof) <addr> Convert Live VA / Symbol to RVA & Raw File Offset

Kernel & Driver Audit:
  !de.drivers (drivers)             List loaded kernel drivers & device objects
  !de.irphooks (irphooks <drv>)     Scan driver IRP MajorFunction dispatch table for hooks

Binary Dumping:
  !de.dumpmod <module>              Dump selected module from memory (e.g. C:\temp\dump.exe)

Session Logger (Astro MDX):
  !de.startlog [file] [title]       Start DML-to-MDX session logger
  !de.stoplog                       Stop session logger and finalize .mdx file
```

---

## Operational & Setup Guides

- **[Real-World Case Study & Tool Usage Example](https://mnemonic-re.github.io/research-notebook/research/windbgx-mcp-ai-reverse-engineering-protocol/)**: Live benchmark demonstration of automated assembly reversing, keygen algorithm extraction, and visual stepping on `GigaApp.exe`.
- **[AI Provider Setup & Environment Guide](guides/AI_Provider_Setup_Guide.md)**: Detailed configuration for Google Gemini, OpenAI, Anthropic, Mistral, Groq, Cerebras, Ollama, LM Studio, and OpenRouter outside of IDEs (PowerShell, CMD, Bash) and inside MCP host JSONs.
- **[AI Operational & Reversing Guide](guides/AI_Guide.md)**: Workspace directory hygiene rules (`analysis/<TARGET>/`), token-efficient live reversing protocols, and command reference catalogs.
- **[WinDbg & DebugExt RE Command Reference](guides/RE_Commands.md)**: Complete command reference catalog for native WinDbg / CDB commands and DebugExt (`de.dll`) bang commands (`!de.*`).
- **[Advanced Usage & Multi-Session Guide](guides/Advanced_Usage_Guide.md)**: Full architecture guide for remote CDB servers, kernel debugging, and multi-client setups.
- **[Developer & Architecture Guide](guides/CLAUDE.md)**: Internal developer guide, environment setup, and design rules for WinDbgMCP contributors.
