---
name: kernel-debug
description: Instructions for kernel-mode debugging, KDNET session setup, driver object inspection, and IRP hook scanning.
---

# Kernel Debugging Skill

When instructed to perform Windows kernel debugging:

1. **Session Setup**:
   Call `open_kd_session(connection_type="kdnet", connection_params="port=50000,key=1.2.3.4")` or pipe/com equivalent.

2. **Driver Verification & Hook Scanning**:
   Call `scan_irp_hooks(driver_name="<driver_name>")` to audit IRP dispatch routines.
   Scan driver memory using `scan_hooks(module="<driver_module>")`.

3. **Process & Thread Traversal**:
   Execute `!process 0 7` or `!thread` via `execute_raw_command()`.
   Inspect PEB/TEB data via `get_peb()` and `get_teb()`.
