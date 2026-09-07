# SYSTEM PROMPT & MASTER DIRECTIVE DRIVER - WinDbgMCP

This document establishes the **Mandatory Operational Driver & Protocol Directive** for ALL AI agents (Google Antigravity, Claude Code, Cursor, Codex, Windsurf, Cline, VS Code, OpenAI Assistants) interacting with **WinDbgMCP**.

---

## 1. Directory Hygiene & Target Workspace Architecture
- **Zero Root Clutter Rule**: NEVER place scratch files, temporary byte dumps, or custom python solver scripts in the repository root.
- For **EVERY** target binary analyzed, the AI agent **MUST** immediately create:
  ```text
  analysis/<TARGET_NAME>/
  ├── mds/
  │   ├── scratchpad.md               # Mandatory live log for disassemblies, registers & traces
  │   └── <TARGET_NAME>_Final_Report.md # Mandatory executive summary report upon task completion
  └── scripts/                        # ALL custom keygen solvers, AOB tools, and analysis scripts
  ```

---

## 2. DebugExt (`de.dll`) Command Encouragement Directive
- **Simple Crackmes & User-Mode Targets**: Follow the surgical 3-step token-efficient protocol (`u main`, `bp cmp_addr`, read registers/stack).
- **Complex Executables, Kernel Drivers, Malware & Deep Reverse Engineering**: AI agents are **EXPECTED AND STRONGLY ENCOURAGED** to aggressively use **ALL** tools at their disposal — particularly **DebugExt (`de.dll`)** bang commands:
  - `!de.disasm`: Disassemble with DML syntax colorization and symbol annotations.
  - `!de.dq` / `!de.dd` / `!de.db`: DML QWord/DWord/Byte memory dumps + ASCII + string previews.
  - `!de.dp` (`tele`): Telescoping pointer chain dump (resolves nested pointers and origins).
  - `!de.strref`: Scan module code/data for ASCII and UTF-16 string references.
  - `!de.xrefs`: Locate code cross-references (`CALL`, `JMP`, `RIP`-rel) to target addresses.
  - `!de.args`: Inspect live fastcall/stdcall function parameters.
  - `!de.vtable`: Inspect virtual method tables and detour overrides.
  - `!de.hooks` / `!de.injections`: Audit inline detour hooks, IAT patches, shellcode, and unmapped code pages.
  - `!de.memmap`: Virtual memory protection map highlighting `RWX` pages.
  - `!de.peb` / `!de.teb` / `!de.pe`: Process/Thread environment blocks and PE security mitigations (ASLR, DEP, CFG).
  - Built-in Analysis Engines: `diff_memory_snapshots`, `triage_crash_report`, `reconstruct_struct`, `trace_api_calls`, `unpack_dynamic_pe`, `audit_kernel_integrity`, `scan_stack_spoofing`, `find_rop_gadgets`, `audit_heap_corruption`.

---

## 3. Mandatory Live Scratchpad Logging (`scratchpad.md`)
- As reverse engineering progresses, the AI agent **MUST** continuously record:
  - Key string references (`!de.strref`) and code cross-references (`!de.xrefs`).
  - Function disassembly snippets and comparison logic.
  - Live register states (`r`) and stack memory dumps (`dd`/`dq`).
  - Identified cryptographic algorithms, keygen loops, or vulnerability root causes.
- Store raw notes in `analysis/<TARGET_NAME>/mds/scratchpad.md`.

---

## 3.1 Live WinDbg GUI (`WinDbgX`) Visual Stepping Protocol
- **Live GUI Visibility**: When attached to a desktop **WinDbg GUI** (`WinDbgX` / `DbgX.Shell.exe`) remote server (`tcp:port=...`), AI agents **MUST** make execution flow and disassembly movement visually trackable inside the user's desktop window:
  - **Milestone Banners**: Execute `annotate_session(milestone="...")` before major stepping or analysis phases to stream DML-colorized block banners into the user's WinDbg GUI output window.
  - **Live Disassembly Movement**: Issue `!de.disasm $ip L20` (or `u $ip L20`) after stepping (`p`, `t`, `gu`, `ret`, `toaddr`) so the user can visually watch the disassembly cursor and register panel move live in their WinDbg GUI window without digging through logs.
  - **Intent Banners**: Pass the `reasoning` parameter on command execution tools so `=== [AI INTENT]: <reasoning> ===` streams live into the WinDbg GUI log before commands execute.

---

## 4. Mandatory Executive Final Report (`<TARGET_NAME>_Final_Report.md`)
- Before completing a task or disconnecting the debugger session, the AI agent **MUST** generate `analysis/<TARGET_NAME>/mds/<TARGET_NAME>_Final_Report.md` containing:
  1. **Executive Overview**: High-level target summary and problem resolution.
  2. **Target Specifications**: File bitness (x86 vs x64), base address, symbol status.
  3. **Technical Reverse Engineering Analysis**: Detailed breakdown of key functions, algorithms, or crash root causes.
  4. **Debugger Evidence**: Live memory byte dumps, register dumps, and disassembly logs.
  5. **Automated Solver / Artifacts**: Reference to custom Python solvers stored in `analysis/<TARGET_NAME>/scripts/`.

---

## 5. Reference Guide Navigation
- **`guides/RE_Commands.md`**: Complete WinDbg & DebugExt (`de.dll`) command catalog and `.load de` instructions.
- **`guides/AI_Guide.md`**: Full operational protocol and reversing guidelines.
- **`guides/AI_Provider_Setup_Guide.md`**: Environment variable setup for 17 AI providers (Gemini, OpenAI/Codex, Claude, DeepSeek, Groq, etc.).
- **`guides/Advanced_Usage_Guide.md`**: Remote CDB, kernel debugging, and multi-session architecture.
