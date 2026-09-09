import os
from pathlib import Path

wiki_dir = Path("C:/Users/DEV/source/repos/WinDbgX/WinDbgX_MCP/WinDbgMCP.wiki")
wiki_dir.mkdir(parents=True, exist_ok=True)

# 1. _Sidebar.md
sidebar = """### 📚 WinDbgX-MCP Wiki

* [[Home]]
* [[AI-Guide]]
* [[DebugExt-Command-Catalog]]
* [[Multi-Provider-Setup]]
* [[Advanced-Usage-&-Architecture]]

---
* 🔗 [GitHub Repository](https://github.com/mnemonic-re/WinDbgX-MCP)
* 📦 [PyPI Wheel](https://raw.githubusercontent.com/mnemonic-re/WinDbgX-MCP/main/WinDbgMCP/dist/windbg_mcp-0.1.0-py3-none-any.whl)
"""
(wiki_dir / "_Sidebar.md").write_text(sidebar, encoding="utf-8")

# 2. Home.md
home = """# Welcome to the WinDbgX-MCP Wiki

Welcome to the official documentation wiki for **WinDbgX-MCP** — an open-source Model Context Protocol (MCP) server designed to equip AI coding assistants (Google Antigravity, VS Code Cline, Cursor, Claude Desktop, Codex, Windsurf) with native **WinDbg** automation, **DebugExt** (`de.dll`) reverse-engineering tools, and real-time visual GUI stepping.

---

## ⚡ Quick Navigation

* 🚀 **[[AI-Guide]]**: Master operational directives, directory hygiene, and live visual stepping protocols.
* 🛠️ **[[DebugExt-Command-Catalog]]**: Full reference of native WinDbg and extended `DebugExt` (`!de.*`) bang commands.
* 🔑 **[[Multi-Provider-Setup]]**: Environment variable configuration for 17 AI providers (Gemini, Claude, OpenAI, DeepSeek, Groq, Ollama, LM Studio).
* ⚙️ **[[Advanced-Usage-&-Architecture]]**: Remote CDB attachment, kernel debugging (KDNET/Pipes), and multi-session orchestration.

---

## 📦 Zero-Config Installation

WinDbgX-MCP is packaged as a self-contained Python wheel bundling pre-compiled 64-bit and 32-bit `de.dll` binaries:

```bash
pip install https://raw.githubusercontent.com/mnemonic-re/WinDbgX-MCP/main/WinDbgMCP/dist/windbg_mcp-0.1.0-py3-none-any.whl
windbg-mcp --help
```

---

## 🖥️ Live WinDbg GUI Visual Stepping

When attached to a desktop **WinDbg GUI** (`WinDbgX` / `DbgX.Shell.exe`) server (`.server tcp:port=5005`), WinDbgX-MCP streams live intent banners (`=== [AI INTENT]: <reasoning> ===`), DML colorized milestone blocks, and moves the disassembly cursor in real-time inside your desktop debugger window!

---

## 📖 Real-World Case Study & Example

For a complete end-to-end demonstration of **WinDbgX-MCP** tool usage — including automated assembly disassembly, algorithm extraction, key calculation for `GigaApp.exe`, and live visual stepping — check out our published research case study:

👉 **[WinDbgX-MCP AI Reverse Engineering Protocol (GigaApp Case Study)](https://mnemonic-re.github.io/research-notebook/research/windbgx-mcp-ai-reverse-engineering-protocol/)**
"""
(wiki_dir / "Home.md").write_text(home, encoding="utf-8")

# 3. AI-Guide.md
ai_guide = """# AI Agent Operational Guide & Visual Stepping Protocol

This guide establishes the mandatory operational protocols and directory rules for AI agents interacting with **WinDbgMCP**.

---

## 1. Directory Hygiene & Target Workspace Architecture

For **EVERY** target binary analyzed, the AI agent **MUST** create:

```text
analysis/<TARGET_NAME>/
├── mds/
│   ├── scratchpad.md               # Mandatory live log for disassemblies, registers & traces
│   └── <TARGET_NAME>_Final_Report.md # Executive summary report upon task completion
└── scripts/                        # ALL custom solvers, AOB tools, and analysis scripts
```

---

## 2. Live WinDbg GUI (`WinDbgX`) Visual Stepping Protocol

When attached to a desktop **WinDbg GUI** remote server (`tcp:Port=5005`):

1. **Milestone Banners**: Execute `annotate_session(milestone="...")` before major stepping or analysis phases to stream DML-colorized block banners into the user's WinDbg GUI window.
2. **Live Disassembly Movement**: Issue `!de.disasm $ip L20` (or `u $ip L20`) after stepping (`p`, `t`, `gu`, `ret`, `so`) so the user can visually watch the disassembly cursor and register panel move live in their WinDbg GUI window.
3. **Intent Banners**: Pass the `reasoning` parameter on command execution tools so `=== [AI INTENT]: <reasoning> ===` streams live into the WinDbg GUI log.

---

## 📖 Live Example & Case Study

Check out a live example of an AI agent utilizing this operational protocol and toolset on a real target binary (`GigaApp.exe`):

👉 **[WinDbgX-MCP AI Reverse Engineering Protocol (GigaApp Case Study)](https://mnemonic-re.github.io/research-notebook/research/windbgx-mcp-ai-reverse-engineering-protocol/)**
"""
(wiki_dir / "AI-Guide.md").write_text(ai_guide, encoding="utf-8")

# 4. DebugExt-Command-Catalog.md
cmd_catalog = """# DebugExt (`de.dll`) Command Catalog

`DebugExt` (`de.dll`) brings x64dbg-style analysis, DML-colorized output, telescoping pointer analysis, and security auditing directly into WinDbg / CDB sessions.

---

## Extension Commands (`!de.*`)

| Command | Description |
| :--- | :--- |
| `!de.disasm $ip L20` | Disassemble with DML syntax colorization and symbol annotations. |
| `!de.strref` | Scan module code/data for ASCII and UTF-16 string references. |
| `!de.xrefs <addr>` | Locate code cross-references (`CALL`, `JMP`, `RIP`-relative) to target address. |
| `!de.peb` | Audit Process Environment Block, `BeingDebugged`, and `NtGlobalFlag` mitigations. |
| `!de.memmap` | Virtual memory protection map highlighting `RWX` regions. |
| `!de.hooks` | Audit inline detour hooks, IAT patches, dynamic code pages, and unmapped code. |
| `!de.regs` | Display colorized 64-bit register state grid. |
| `!de.dxhelp` | Display DebugExt built-in interactive help catalog. |

---

## Navigation & Stepping Shortcuts

| Command | Description |
| :--- | :--- |
| `si` | Step Into instruction. |
| `so` | Step Over instruction. |
| `su` / `ret` | Step Out / Run until current function returns. |
| `toaddr <address>` | Run execution until target address is hit. |
"""
(wiki_dir / "DebugExt-Command-Catalog.md").write_text(cmd_catalog, encoding="utf-8")

# 5. Multi-Provider-Setup.md
provider_setup = """# Multi-AI Provider Setup Guide

WinDbgMCP supports 17 AI provider configurations read at runtime from environment variables.

---

## Supported Providers & Environment Variables

| Provider Name | Required Environment Variable | Default Model |
| :--- | :--- | :--- |
| `gemini` | `GEMINI_API_KEY` | `gemini-3.5-flash` |
| `openai` | `OPENAI_API_KEY` | `gpt-5.6` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-5-opus` |
| `deepseek` | `DEEPSEEK_API_KEY` | `deepseek-reasoner` |
| `groq` | `GROQ_API_KEY` | `deepseek-r1-distill-llama-70b` |
| `openrouter` | `OPENROUTER_API_KEY` | `nvidia/nemotron-3-nano-30b-a3b:free` |
| `ollama_local` | `OLLAMA_LOCAL_BASE_URL` | `qwen2.5-coder:32b` |
| `lmstudio` | `LOCAL_LLM_BASE_URL` | `qwen2.5-coder-14b-instruct` |
"""
(wiki_dir / "Multi-Provider-Setup.md").write_text(provider_setup, encoding="utf-8")

# 6. Advanced-Usage-&-Architecture.md
adv_usage = """# Advanced Usage & Architecture

WinDbgX-MCP supports 4 primary connection modes:

1. **Crash Dump Triage (`open_cdb_dump`)**: Automated triage of `.dmp` crash files.
2. **User-Mode Remote Server (`open_cdb_remote`)**: Connect to live desktop WinDbg GUI servers (`tcp:Port=5005`).
3. **Kernel Debugging Target (`open_kd_session_tool`)**: Kernel debugging via KDNET, VM Pipe, or Serial.
4. **Live Local Process Attach (`attach_live_process`)**: Attach CDB by PID or process name.

---

## Multi-Session Orchestration

Inspect and switch between multiple user-mode and kernel debugging sessions concurrently:
- `list_sessions()`: View all active debug sessions.
- `switch_session(session_id="...")`: Switch default active session.
"""
(wiki_dir / "Advanced-Usage-&-Architecture.md").write_text(adv_usage, encoding="utf-8")

print("[+] All 6 Wiki pages created successfully!")
