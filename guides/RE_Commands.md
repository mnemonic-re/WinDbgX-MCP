# WinDbg & DebugExt (`de.dll`) Reverse Engineering Command Reference

A comprehensive reference catalog of standard native WinDbg / CDB commands and extended `DebugExt` (`de.dll`) commands for reverse engineering, dynamic debugging, memory analysis, kernel auditing, and vulnerability triage.

---

## Table of Contents
1. [Standard Native WinDbg / CDB Commands](#1-standard-native-windbg--cdb-commands)
2. [DebugExt (`de.dll`) Bang Commands (`!de.*`)](#2-debugext-dedll-bang-commands-de)
3. [Navigation & Stepping Shortcuts](#3-navigation--stepping-shortcuts)
4. [Recommended Workflows by Reversing Scenario](#4-recommended-workflows-by-reversing-scenario)

---

## 1. Standard Native WinDbg / CDB Commands

### Execution & Process Control
| Command | Description |
| :--- | :--- |
| `g` | Continue process execution (Go) until break, exception, or exit. |
| `p` / `p <count>` | Step Over instruction(s). |
| `t` / `t <count>` | Step Into instruction(s). |
| `gu` | Step Out / Go Up (continue execution until current function returns). |
| `pa <address>` | Step to target address. |
| `ta <address>` | Trace to target address. |
| `wt` | Watch and trace execution flow, gathering call statistics and branch targets. |

### Breakpoints & Hardware Registers
| Command | Description |
| :--- | :--- |
| `bp <address> ["command"]` | Set software breakpoint (INT 3) with optional execute command. |
| `bu <symbol>` | Set unresolved breakpoint on symbol name (evaluated when module loads). |
| `bl` | List all active breakpoints with IDs, status, and hit counts. |
| `bc <id>` / `bc *` | Clear specified breakpoint ID or clear all breakpoints. |
| `bd <id>` / `be <id>` | Disable / enable specified breakpoint. |
| `ba r|w|e <size> <address>` | Set hardware breakpoint on Read (`r`), Write (`w`), or Execute (`e`) using debug registers (`DR0`-`DR3`). |

### Register & Memory Operations
| Command | Description |
| :--- | :--- |
| `r` | Display all general-purpose registers and flags. |
| `r <reg>=<val>` | Modify target register value (e.g. `r eax=1`). |
| `d[a|u|b|w|d|q] <addr> [L<len>]` | Display memory as ASCII (`da`), Unicode (`du`), Bytes (`db`), Words (`dw`), DWords (`dd`), or QWords (`dq`). |
| `e[b|w|d|q] <addr> <values>` | Edit memory bytes/words/dwords at target address. |
| `s -[b|w|d|q|a|u] <range> <pat>` | Search memory range for byte pattern, ASCII, or Unicode string. |
| `u <address> [L<count>]` | Unassemble / disassemble instructions starting at address. |

### Call Stack & Symbol Inspection
| Command | Description |
| :--- | :--- |
| `k` / `kb` / `kp` / `kn` / `kv` | Display call stack (`kb` includes parameters, `kp` includes typed args, `kn` adds frame numbers, `kv` includes FPO info). |
| `dt [mod!]struct [address]` | Display structure field offsets, types, and live values. |
| `x <mod!pattern>` | Examine symbols matching glob pattern (e.g. `x ntdll!NtCreate*`). |
| `lm` / `lmD` / `lm v m <name>` | List loaded modules and header details (`lmD` colorizes image boundaries). |

### Process, Thread & Environment
| Command | Description |
| :--- | :--- |
| `~` | Enumerate all process threads and active thread ID. |
| `~<id>s` | Switch active execution thread context. |
| `!peb` | Display Process Environment Block (command line, image path, DLL search path, heap pointers). |
| `!teb` | Display Thread Environment Block (stack base/limit, LastError, TLS array). |
| `!heap -p -a <addr>` | Inspect Pageheap allocation chunk header & allocation stack trace. |
| `!address <addr>` | Query virtual memory region allocation, state, memory type, and protection flags. |

---

## 2. DebugExt (`de.dll`) Bang Commands (`!de.*`)

`DebugExt` (`de.dll`) brings x64dbg-style analysis, DML-colorized output, telescoping pointer analysis, and security auditing directly into WinDbg / CDB sessions.

### Navigation & Execution Control
| Command | Alias | Description |
| :--- | :--- | :--- |
| `si` | `si` | DML Step Into shortcut. |
| `so` | `so` | DML Step Over shortcut. |
| `su` | `su` | DML Step Out shortcut. |
| `ret` | `ret` | Run execution until current function returns (`RET`). |
| `toaddr <address>` | `toaddr` | Run execution until target address is hit. |
| `tobranch` | `tobranch` | Run execution until next conditional/unconditional branch (`JMP`, `JZ`, `JNZ`, `CALL`). |
| `tocall` | `tocall` | Run execution until next `CALL` instruction. |

### Core & Navigation Utilities
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.regs` | `regs` | Display colorized register layout with flags and execution state. |
| `!de.disasm` | `dis`, `disasm` | Disassemble code with DML syntax colorization and symbol annotations. |
| `!de.lmod` | `lmod` | List loaded executable modules with base addresses, sizes, and symbol status. |
| `!de.dxhelp` | `dxhelp` | Display DebugExt built-in interactive help catalog. |

### Memory Inspection (x64dbg Style)
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.dq` | `dqx <addr> [L-20]` | DML QWord memory dump + ASCII representation + symbol/string resolution. |
| `!de.dd` | `ddx <addr> [L-20]` | DML DWord memory dump + ASCII representation + symbol/string resolution. |
| `!de.db` | `dbx <addr> [L-20]` | DML Byte memory dump + ASCII representation + dimmed null bytes. |
| `!de.dp` | `dpx`, `tele <addr>` | Telescoping pointer chain dump (dereferences nested pointers and identifies module/string origins). |
| `!de.dumpmem` | `dxx <addr> [L-20]` | Smart architecture-aware memory dump tailored to active target bitness (x86 vs x64). |

### Function & Call Graph Analysis
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.function` | `function` | Inspect target function boundaries, frame size, prologue/epilogue, and disassembly range. |
| `!de.bt` | `bt`, `callstack` | Enhanced DML callstack retriever with inline parameter previews. |
| `!de.callees` | `callees` | List all functions called (`CALL`) by current or target function. |
| `!de.callers` | `callers` | List all functions in module that call (`CALL`) current or target function. |

### Hook & Security Auditing
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.vtable` | `vtable <ptr>` | Inspect virtual method table (VMT) pointers, detecting overridden methods and detours. |
| `!de.hooks` | `hooks [module]` | Scan target module or process memory for inline detour hooks (`JMP`/`PUSH-RET`) and IAT patches. |
| `!de.injections` | `injections` | Scan process memory for unmapped executable code pages, injected shellcode, and reflective DLLs. |
| `!de.codecaves` | `codecaves [mod]`| Scan module PE alignment gaps for code caves suitable for shellcode placement. |

### Windows Internals & PE Analysis
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.peb` | `peb` | Audit Process Environment Block (PEB) for anti-debugging flags (`BeingDebugged`, `NtGlobalFlag`, `ProcessHeap`). |
| `!de.teb` | `teb` | Inspect Thread Environment Block (TEB) including stack base/limit, TEB-based TLS, and thread ID. |
| `!de.pe` | `pe [<mod>|<addr>]`| Audit PE file headers, section characteristics, security mitigations (ASLR, DEP, SafeSEH, CFG), and import/export tables. |

### Advanced Reversing & Offsets (x64dbg Style)
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.args` | `args`, `params` | Inspect live function calling convention parameters (`rcx`, `rdx`, `r8`, `r9` or stack args) with symbol/string resolution. |
| `!de.strref` | `strref`, `strings` | Scan module code and data sections for ASCII and UTF-16 string references. |
| `!de.xrefs` | `xrefs`, `xref` | Find all code cross-references (`CALL`, `JMP`, `RIP`-relative loads) referencing target address. |
| `!de.memmap` | `memmap`, `pages` | Generate virtual memory protection map highlighting executable and Read-Write-Execute (`RWX`) pages. |
| `!de.gooffset` | `gooffset`, `rva` | Jump directly to RVA offset in module and disassemble target code. |
| `!de.fo2va` | `fo2va`, `fo` | Convert Raw Disk File Offset (e.g. from HxD or Ghidra) to live Virtual Address. |
| `!de.va2fo` | `va2fo`, `va` | Convert live Virtual Address or symbol to Relative Virtual Address (RVA) and Raw Disk File Offset. |

### Kernel Mode & Driver Auditing
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.drivers` | `drivers` | List loaded kernel drivers, driver objects, and device objects. |
| `!de.irphooks` | `irphooks <drv>` | Scan driver `MajorFunction` IRP dispatch table for hooked handlers and rootkit detours. |

### Memory Dumping & Session Logging
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!de.dumpmod` | `dumpmod` | Dump unpacked module or decrypted binary payload directly from live memory to disk. |
| `!de.startlog` | `startlog` | Start DML-to-MDX session logger to record debug sessions into formatted markdown. |
| `!de.stoplog` | `stoplog` | Finalize session logger and save active MDX file. |

---

## 3. Navigation & Stepping Shortcuts

DebugExt registers intuitive stepping shortcuts directly into the command prompt:

```text
  si               - Step Into
  so               - Step Over
  su               - Step Out
  ret              - Run to RET instruction
  toaddr <addr>    - Run to target address
  tobranch         - Run to next branch instruction (JMP/JZ/JNZ/CALL)
  tocall           - Run to next CALL instruction
```

---

## 4. Recommended Workflows by Reversing Scenario

### Scenario A: Simple User-Mode Binaries & Crackmes
Follow the **Token-Efficient Live Reversing Protocol**:
1. Disassemble target `main`: `u <module>!main L40`.
2. Set conditional breakpoint at comparison: `bp <cmp_addr> ".echo === [SECRET] ===; dd ebp-X L1; r"`.
3. Run target (`g`), trigger user input, and read secret directly from registers or stack.

### Scenario B: Complex Executables, Malware Unpacking & Reverse Engineering
1. **Memory Map Audit**: Execute `!de.memmap` (or `audit_memory_regions`) to locate executable and `RWX` pages.
2. **Injections & Shellcode**: Run `!de.injections` (or `scan_hooks_and_injections`) to scan for unmapped executable code pages or reflective DLLs.
3. **String & Code XREFs**: Use `!de.strref` (or `scan_string_references`) and `!de.xrefs` (or `find_code_xrefs`) to pinpoint cryptographic routines, key checks, or C2 communication logic.
4. **Parameter Inspection**: Use `!de.args` (or `inspect_function_args`) when stopping at suspicious WinAPI functions (`VirtualAlloc`, `WriteProcessMemory`, `CreateRemoteThread`).
5. **Payload Extraction**: Dump unpacked modules from memory using `!de.dumpmod` (or `dump_rwx_payload`).

### Scenario C: Kernel Drivers & Rootkit Triage
1. **Driver Enumeration**: Run `!de.drivers` to enumerate active kernel drivers.
2. **IRP Hook Scan**: Run `!de.irphooks <driver>` to inspect `MajorFunction` dispatch routines for hooked entrypoints.
3. **Kernel Integrity**: Run `audit_kernel_integrity` to scan `EPROCESS` lists, SSDT tables, and driver dispatch tables.
4. **Stack Spoofing**: Run `scan_stack_spoofing` to audit active threads for unbacked return addresses or stack frame manipulation.
