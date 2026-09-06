---
name: windbg-doctor
description: Automated diagnostic procedures for resolving symbol path issues, debugging extension loading, and session recovery.
---

# WinDbg Doctor Skill

When troubleshooting debugger environment issues:

1. **Symbol Diagnostics**:
   Run `execute_raw_command(command="!sym noisy")` and `execute_raw_command(command=".reload")`.

2. **Extension Verification**:
   Run `execute_raw_command(command=".chain")`.
   Ensure `de.dll` is loaded. Reload if missing via `execute_raw_command(command=".load de")`.

3. **Session Recovery**:
   Issue `send_ctrl_break()` if CDB/KD process is unresponsive.
   Call `detach_session()` to cleanly close stuck debug target.
