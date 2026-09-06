---
name: debug-remote
description: Instructions for connecting to remote CDB debugging servers and live process targets using WinDbgMCP.
---

# Remote & Live Process Debugging Skill

When instructed to connect to a live process or remote debugging server:

1. **Remote CDB Connection**:
   Call `open_cdb_remote(server_connection_string="<tcp_or_pipe_conn_string>")`.

2. **Live Process Attach**:
   Call `attach_live_process(pid=<target_pid>)` or `attach_live_process(process_name="<process.exe>")`.

3. **Breakpoints & Step Control**:
   Execute raw commands for breakpoints (`execute_raw_command(command="bp <symbol_or_address>")`).
   Resume execution (`resume_execution(command="g")`).
   Wait for break event (`wait_for_break(timeout_seconds=30)`).

4. **Emergency Stop**:
   Call `send_ctrl_break()` if the process enters non-responsive loops or target fails to break.
