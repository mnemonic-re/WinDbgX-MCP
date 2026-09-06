---
name: analyze-dump
description: Complete instructions for triaging user-mode and kernel-mode crash dumps using WinDbgMCP tools and DebugExt.
---

# Dump Analysis Skill

When asked to analyze a Windows crash dump (`.dmp`, `.mdmp`, `.hdmp`):

1. **Launch Session**:
   Call `open_cdb_dump(dump_path="<absolute_path_to_dump>")`.

2. **Automated Crash Triage**:
   Call `get_crash_summary()`.
   Review output for exception code, faulting IP, stack trace, and module list.

3. **Disassemble & Memory Inspection**:
   Call `disassemble_at(target="RIP", count=20)`.
   Call `get_memory_map(address="<faulting_address>")`.

4. **Deep Structural Analysis**:
   Call `get_peb()` and `get_teb()` to inspect process/thread context.
   Inspect target functions using `get_function_args(address="<func_addr>", num_args=4)`.

5. **Generate Summary**:
   Summarize exception code, faulting module, call stack, root cause analysis, and remediation steps.
