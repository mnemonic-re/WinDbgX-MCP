# WinDbgMCP - Quick Usage Guide (User-Mode Debugging)

This guide provides a straightforward, step-by-step walkthrough for using **WinDbgMCP** to attach to and debug local user-mode Windows applications (`.exe`) with AI coding assistants.

---

## 1. Fast Setup & Transport Modes

Before starting, ensure `WinDbgMCP` is registered in your AI client configuration (`mcp.json`). Automate environment setup and registration by running:

```bash
python scripts/install_mcp.py
```

### Transport Options:
- **Stdio Mode (Default)**: Spawns automatically via stdin/stdout for local AI apps (Antigravity, Claude, Cursor):
  ```bash
  python -m windbg_mcp
  ```
- **SSE Network Mode**: Runs an HTTP server on port 8000 for web/remote AI apps:
  ```bash
  python -m windbg_mcp --sse --port 8000
  ```

---

## 2. Attaching to a Live User-Mode Target

You can attach to any running Windows process using either its **Process ID (PID)** or its **executable name**.

### A. Attach by Process Name
```python
attach_live_process(target="notepad.exe")
```

### B. Attach by Process ID (PID)
```python
attach_live_process(target="4128")
```

*Upon execution, `cdb.exe` attaches to the target process, halts execution, and returns a unique `session_id` (e.g. `cdb-attach-a1b2c3d4`).*

---

## 3. Running Basic User-Mode Commands

Execute standard WinDbg commands on your open user-mode session using `run_cdb_command`:

### A. Inspect Register State
```python
run_cdb_command(command="r")
```

### B. Inspect Call Stack
```python
run_cdb_command(command="k")  # Display basic call stack
run_cdb_command(command="kp") # Display stack with parameter types
```

### C. Disassemble Code
```python
run_cdb_command(command="u RIP L20")  # Disassemble 20 instructions at RIP
run_cdb_command(command="u main L15") # Disassemble 15 instructions at symbol 'main'
```

### D. Dump Memory
```python
run_cdb_command(command="db RSP L64") # Display bytes & ASCII at stack pointer
run_cdb_command(command="dc RSP L64") # Display dwords & symbol previews
```

---

## 4. Setting Breakpoints & Execution Control

### A. Set a Software Breakpoint
```python
run_cdb_command(command="bp main") # Break at symbol 'main'
run_cdb_command(command="bp 0x00007ff69b8c10f0") # Break at specific virtual address
```

### B. List & Clear Breakpoints
```python
run_cdb_command(command="bl") # List active breakpoints
run_cdb_command(command="bc *") # Clear all breakpoints
```

### C. Resume Target Execution
```python
run_cdb_command(command="g") # Resume target execution immediately
```

---

## 5. Closing the Session

When debugging is complete, release the process handles and detach CDB:

```python
close_session()
```
