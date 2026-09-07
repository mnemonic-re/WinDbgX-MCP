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

---

## 5. Standard Native WinDbg & CDB Command Reference

Below is the complete reference of built-in native WinDbg / CDB commands frequently used during dynamic debugging and reverse engineering.

```text
============================================================
 Native WinDbg / CDB Command Reference
============================================================

Execution Control:
  g                          Continue execution (Go)
  p                          Step Over (single instruction)
  t                          Step Into (single instruction)
  gu                         Step Out / Go Up (run until current function returns)
  pa <address>               Step to address
  ta <address>               Trace to address
  wt                         Watch and trace execution flow

Breakpoints:
  bp <address>               Set breakpoint at address / symbol
  bp <addr> ".echo msg; r"   Set breakpoint with conditional / automatic command execution
  bu <symbol>                Set unresolved breakpoint (evaluates when module loads)
  bm <module!pattern>        Set breakpoint on matching symbol names
  ba <r|w|e> <size> <addr>   Set hardware breakpoint (read/write/execute, size=1|2|4|8)
  bl                         List all breakpoints
  bc <id|*>                  Clear breakpoint(s)
  bd <id|*>                  Disable breakpoint(s)
  be <id|*>                  Enable breakpoint(s)

Registers & Context:
  r                          Display all general-purpose registers
  r <reg>                    Display specific register (e.g. r eax, r rip)
  r <reg>=<value>            Modify register value (e.g. r eax=1, r eip=0x00401168)
  @eip / @rip                Pseudo-register for Instruction Pointer
  @esp / @rsp                Pseudo-register for Stack Pointer
  @ebp / @rbp                Pseudo-register for Base Pointer

Disassembly:
  u <address>                Disassemble instructions starting at address
  u <address> L<count>       Disassemble N instructions (e.g. u 0x00401000 L20)
  uf <function>              Disassemble entire function block

Memory Inspection & Editing:
  db <address> [L<count>]    Display Byte values + ASCII
  dw <address> [L<count>]    Display Word (16-bit) values
  dd <address> [L<count>]    Display DWord (32-bit) values
  dq <address> [L<count>]    Display QWord (64-bit) values
  da <address>               Display null-terminated ASCII string
  du <address>               Display null-terminated Unicode (UTF-16) string
  eb <address> <bytes>       Edit memory bytes (e.g. eb 0x00401000 90 90 90)
  ed <address> <dwords>      Edit memory dwords
  s -b <start> <end> <pat>   Search memory byte pattern (e.g. s -b 0x400000 0x405000 55 8b ec)
  s -a <start> <end> <str>   Search memory for ASCII string
  s -u <start> <end> <str>   Search memory for Unicode string

Call Stack & Threads:
  k                          Display call stack backtrace
  kp                         Display call stack with full parameters
  kv                         Display call stack with frame pointer & calling convention details
  kn                         Display call stack with frame numbers
  ~                          List all threads in current process
  ~*k                        Display call stack for all threads
  ~<thread>s                 Switch to specific thread context (e.g. ~0s)

Modules & Symbols:
  lm                         List loaded modules
  lm m <pattern>             List loaded modules matching pattern (e.g. lm m guess*)
  x <module>!<pattern>       Examine symbols matching pattern (e.g. x GuessMe!main*)
  .sympath                   Display or set symbol search path
  .symfix                    Automatically set symbol path to Microsoft Public Symbol Server
  .reload                    Reload module symbols

Meta & Session Commands:
  .load <path_to_dll>        Load debugger extension (e.g. .load de)
  .chain                     List all loaded extension DLLs
  .server tcp:port=<port>    Start WinDbg remote debugging server
  .echo <string>             Echo string to output console
  .detach                    Detach debugger from process without terminating it
  q                          Quit and terminate debugger session
```

---

## 6. DebugExt (`de.dll`) - Complete Command & Helper Reference

> [!NOTE]
> `DebugExt` (`de.dll`) is the helper extension providing ported x64dbg/Cheat Engine style reverse-engineering bang commands. Use these helper commands after `.load de` when conducting advanced analysis.

```text
============================================================
 DebugExt - Analysis / Navigation Commands
============================================================

Navigation:
  si                         Step Into
  so                         Step Over
  su                         Step Out
  ret                        Run to RET
  toaddr <address>           Run to address
  tobranch                   Run to branch
  tocall                     Run to CALL

Utilities:
  !de.regs                          Display registers
  !de.disasm (dis/disasm)           Disassemble with DML colorization
  !de.lmod                          List loaded modules
  !de.dxhelp                        Display this help

Memory Inspection (x64dbg style):
  !de.dq (dqx <addr> [L-20])        DML QWord dump + ASCII + symbols/strings
  !de.dd (ddx <addr> [L-20])        DML DWord dump + ASCII + symbols/strings
  !de.db (dbx <addr> [L-20])        DML Byte dump + ASCII + dimmed nulls
  !de.dp (dpx/tele <addr> [L-20])   Telescoping pointer chain dump
  !de.dumpmem (dxx <addr> [L-20])   Smart architecture-aware dump

Function Analysis:
  !de.function                       Current function
  !de.function <address>             Function containing address
  !de.function <function>            Resolve function by name

Call Graph & Stack:
  !de.bt (bt / callstack)            DML Callstack & parameter retriever
  !de.callees                        Callees of current function
  !de.callees <address>              Callees of function at address
  !de.callees <function>             Callees of named function

  !de.callers                        Callers of current function
  !de.callers <address>              Callers of function at address
  !de.callers <function>             Callers of named function

Hook & Security Scanner:
  !de.vtable (vtable <ptr> [cnt])    Inspect virtual method table & detours
  !de.hooks (hooks [module])         Scan module for inline/IAT detour hooks
  !de.injections (injections)        Scan unmapped executable pages / reflective DLLs
  !de.codecaves (codecaves [mod])    Scan module PE alignment gaps for code caves

PE & Windows Internals:
  !de.peb (peb)                      PEB anti-debug audit & process params
  !de.teb (teb)                      Thread Environment Block & stack limits
  !de.pe (pe <mod/addr>)             PE header & security mitigations audit (ASLR/DEP/RWX)

Advanced Reversing & Inspection (x64dbg style):
  !de.args (args / params)            Inspect live function calling convention parameters
  !de.strref (strref / strings) [mod] Scan module for ASCII & UTF-16 string references
  !de.xrefs (xrefs / xref) <target>   Find code cross-references (CALL/JMP/RIP-rel) to target
  !de.memmap (memmap / pages)         Virtual memory protection & commit map + RWX alert

Offsets & Address Translations:
  !de.gooffset (gooffset / rva) [mod] <off>   Go to RVA offset in module & disassemble
  !de.fo2va (fo2va / fileoffset / fo) <off>   Convert Raw Disk File Offset to live Virtual Address
  !de.va2fo (va2fo / offsetof / rvaof) <addr> Convert Live VA / Symbol to RVA & Raw File Offset

Kernel & Driver Audit:
  !de.drivers (drivers)              List loaded kernel drivers & device objects
  !de.irphooks (irphooks <drv>)      Scan driver IRP MajorFunction dispatch table for hooks

Binary Dumping:
  !de.dumpmod <module>              Dump selected module from memory
                                     Dump Loc: C:\temp\moduleName_dump.exe

Session Logger (Astro MDX):
  !de.startlog [file] [title]        Start DML-to-MDX session logger
                                     Captures rich DML colors into Astro <WinDbg> block
  !de.stoplog                        Stop session logger and finalize .mdx file

Examples:
  function 772B1B66
  function ntdll!LdrpDoDebuggerBreak
  callees ntdll!LdrpDoDebuggerBreak
  callers ntdll!NtQueryInformationThread
  makesig 772B1B66
  makesig 772B1B66 48
  findsig ntdll 64 89 0D 00 00 00 00
  findstr guessme "don't guess"
  dumpmod guessme
  lookup IoCreateDevice
  gotoeip guessme
  disasm L20
  dqx 0x00401000 L-20
  ddx esp L10
  dbx 77141b62 L16
  tele esp L16
  bt
  vtable 0x00402000 16
  hooks guessme
  injections
  codecaves guessme 16
  peb
  teb
  pe guessme
  drivers
  irphooks 0x859a1030
  args
  strref AdvancedTarget
  xrefs AdvancedTarget!InternalCryptoHelper
  memmap
  load32
  load64
  startlog C:\test\trace.mdx "Target Analysis"
  -- Offsets
  rva 10f0
  gooffset AdvancedTarget 10f0
  va2fo AdvancedTarget!TestComplexApi
  fo2va 4F0
  fileoffset AdvancedTarget 4F0
```

---

## 7. WinDbgMCP FastMCP Tool Catalog Reference (32 Available Tools)

| Category | FastMCP Tool Name | Description |
| :--- | :--- | :--- |
| **Session Management** | `connect_debugger` | Attach to target process, dump file, or remote WinDbg server. |
| | `disconnect_debugger` | Detach/close session safely. |
| | `get_session_status` | Return current session status, architecture, PID, and target path. |
| | `list_sessions` | List active WinDbg MCP sessions. |
| **Execution Control** | `execute_command` | Execute raw WinDbg command string and capture console stdout. |
| | `step_into` | Execute `t` command. |
| | `step_over` | Execute `p` command. |
| | `step_out` | Execute `gu` command. |
| | `continue_execution` | Execute `g` command. |
| **Breakpoints** | `set_breakpoint` | Set software or execution breakpoint (`bp`). |
| | `clear_breakpoint` | Clear specific breakpoint (`bc`). |
| | `list_breakpoints` | Retrieve active breakpoints (`bl`). |
| **Registers & Context** | `get_registers` | Get CPU registers formatted as key-value pairs (`r`). |
| | `get_call_stack` | Retrieve current thread call stack (`k`). |
| **Disassembly & Memory** | `disassemble` | Disassemble memory range into assembly instructions (`u`). |
| | `read_memory` | Dump raw byte/dword memory (`db`, `dd`, `dq`). |
| | `write_memory` | Edit memory contents (`eb`, `ed`). |
| | `search_memory` | Pattern match byte array or ASCII/Unicode strings (`s`). |
| **Modules & Symbols** | `list_modules` | List loaded PE modules and base addresses (`lm`). |
| | `evaluate_expression` | Evaluate C/C++ or MASM numerical expression (`?`). |
| **Analysis Superpowers** | `diff_memory_snapshots` | Compare process memory state across execution points to identify dynamic modifications. |
| | `triage_crash_report` | Automated crash dump triage analyzing exception codes, faulting instruction, and stack context. |
| | `reconstruct_struct` | Parse pointer offsets and memory layouts into clean C/C++ struct definitions. |
| | `trace_api_calls` | Monitor API calls and parameters dynamically during process execution. |
| | `unpack_dynamic_pe` | Detect, unpack, and dump dynamically loaded/decrypted PE payloads from process memory. |
| | `audit_kernel_integrity` | Audit kernel EPROCESS lists, SSDT tables, and driver dispatch arrays for DKOM & rootkits. |
| | `scan_stack_spoofing` | Inspect thread stack frames for unbacked return addresses (pointing to unmapped/RWX memory), alignment anomalies, and fake stack frames. |
| | `find_rop_gadgets` | Scan loaded executable modules for useful ROP gadgets (e.g. pop rcx; ret, mov [rax], rbx; ret, xchg rax, rsp) categorized by operation. |
| | `audit_heap_corruption` | Automate !heap -p -a & Pageheap diagnostics to pinpoint corrupted chunk headers, freed allocation traces, and UAF bugs. |
| **Auxiliary & Extensions** | `load_extension` | Load external WinDbg extensions (`.load`). |
| | `execute_script` | Run debugger engine scripts. |
| | `search_symbols` | Search module symbol tables (`x`). |
| | `get_thread_context` | Inspect specific thread register states (`~`). |
| | `switch_thread` | Change execution focus to a different thread (`~s`). |
| | `get_process_info` | Fetch process PEB and environmental metadata. |
| | `export_session_log` | Save session history and commands to log file. |

