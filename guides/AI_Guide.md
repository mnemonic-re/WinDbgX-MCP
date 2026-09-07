# WinDbgMCP - AI Agent Operational & Reversing Guide

This guide establishes mandatory operational protocols for AI agents (Google Antigravity, Claude Code, Cursor, Windsurf, OpenAI Assistants) conducting reverse-engineering, crash dump triage, and dynamic debugging using **WinDbgMCP**.

---

## 1. Directory Hygiene & Workspace Architecture

To prevent polluting the repository root or creating workspace clutter ("junk in the brain"), **ALL** project-specific analysis artifacts, scripts, and logs **MUST** strictly reside within `analysis/<TARGET_NAME>/`.

```text
WinDbgMCP/
├── analysis/
│   └── <TARGET_NAME>/
│       ├── mds/
│       │   ├── scratchpad.md            # Live raw notes, disassemblies, register dumps
│       │   └── <TARGET_NAME>_Final_Report.md # Formal executive report
│       └── scripts/                     # ALL custom analysis scripts, solvers, AOB tools
├── guides/
│   ├── AI_Guide.md                      # Operational & Reversing Guide (this file)
│   └── Advanced_Usage_Guide.md          # Multi-session & transport reference
└── src/
    └── windbg_mcp/                      # Core FastMCP server implementation
```

> [!IMPORTANT]
> **Zero Root Clutter Rule**: NEVER place one-off Python scripts, byte dumps, or scratch files in the repository root or generic top-level directories. For target analysis requiring custom scripts (e.g. keygen algorithms, solver scripts, memory parsers), always save them in `analysis/<TARGET_NAME>/scripts/`.

---

## 2. Token-Efficient Live Reversing Protocol (The Golden Rule)

> [!TIP]
> **DO NOT SPEND 50K TOKENS ON SIMPLE CRACKMES & BINARIES!**

Follow this exact 3-step surgical workflow for simple user-mode targets:

1. **Step 1: Locate Comparison & Stack Frame (Disassemble `main`)**:
   - Run `u <module>!main L40` or `u 0x00401000 L40`.
   - Identify the secret generator (`rand()`, `xor`, keygen loop) and the comparison instruction (`cmp reg, dword ptr [ebp-X]`).

2. **Step 2: Read Live Register / Stack Memory Context**:
   - Set a breakpoint right at the comparison:
     ```text
     bp <cmp_address> ".echo === [SECRET] ===; dd ebp-X L1; r"
     ```
   - If the target is running (`g`), prompt the user or execute `g` so the target hits `cmp_address` when user input is submitted.
   - Instantly read `[ebp-X]` or the comparison register (`EAX`/`ECX`/`EDX`).

3. **Step 3: Document & Synthesize**:
   - Log raw outputs to `analysis/<TARGET_NAME>/mds/scratchpad.md`.
   - Write the executive report to `analysis/<TARGET_NAME>/mds/<TARGET_NAME>_Final_Report.md`.

---

## 3. Remote WinDbg GUI Connection Hygiene (`.server tcp:port=...`)

When attaching to a desktop **WinDbg GUI** (`WinDbgX`) remote server:

### A. Single Active Connection Rule
- **NEVER** launch multiple concurrent `cdb.exe` client instances against the same TCP port (`tcp:Port=5005,Server=localhost`).
- Multiple client processes hitting a single `dbsrv` port cause IPC pipe deadlocks, buffer exhaustion, and command timeouts.
- Always reuse the active `session_id` or close the previous session explicitly before opening a new connection.

### B. Execution State Management (`g` vs Halted)
- If the target is running (`g`), standard commands (`r`, `lm`, `u`) will block until the target breaks or hits a breakpoint.
- To set a live breakpoint on a running target, issue `bp <address>`, or issue `g` to resume execution when waiting for user input.
- Always check execution state before issuing long sequences of commands.

---

## 4. Summary Checklist for AI Agents

- [ ] Is `analysis/<TARGET_NAME>/` created for the current target?
- [ ] Are all custom solver/analysis scripts stored in `analysis/<TARGET_NAME>/scripts/`?
- [ ] Is there only **ONE** active debugger client connected to the TCP port?
- [ ] Has the secret/logic been solved live and logged to `scratchpad.md`?
- [ ] Has `<TARGET_NAME>_Final_Report.md` been generated upon completion?
