# WinDbgMCP - Advanced Usage Guide

This comprehensive guide details the advanced capabilities of **WinDbgMCP**, covering crash dump triage, remote debugging, kernel-mode debugging, multi-session management, async execution control, Google Antigravity visual artifact generation, and multi-client environment adapters.

---

## 1. Crash Dump Triage (`open_cdb_dump`)

WinDbgMCP automates initial crash dump triage for `.dmp`, `.mdmp`, and `.hdmp` files.

### A. List Local Dumps
Enumerate `.dmp` files in a target directory:
```python
list_dumps(directory_path="C:\\CrashDumps", recursive=True)
```

### B. Open Crash Dump & Run Automated Analysis
Open a crash dump file. WinDbgMCP automatically executes `.lastevent`, `!analyze -v`, `kb`, `lm`, and `~`:
```python
open_cdb_dump(
    dump_path="C:\\CrashDumps\\memory.dmp",
    symbols_path="srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols",
    include_stack=True,
    include_modules=True
)
```

---

## 2. Remote User-Mode Debugging (`open_cdb_remote`)

Attach a CDB debugger client to a remote user-mode debug server (`-remote`):

### A. Connect via TCP
```python
open_cdb_remote(connection_string="tcp:Port=5005,Server=192.168.1.50")
```

### B. Connect via Named Pipe
```python
open_cdb_remote(connection_string="npipe:Pipe=WinDbgPipe,Server=DESKTOP-ABC")
```

---

## 3. Kernel-Mode Debugging (`open_kd_session`)

WinDbgMCP connects directly to Windows kernel targets over KDNET, VM named pipes, or serial COM ports using `kd.exe`.

### A. Connect over KDNET
```python
open_kd_session_tool(
    connection_string="net:port=50000,key=1.2.3.4",
    symbols_path="srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
)
```

### B. Connect over VM Named Pipe (Hyper-V / VirtualBox / VMware)
```python
open_kd_session_tool(connection_string="com:pipe,port=\\\\.\\pipe\\vm_kdpipe,resets=0,reconnect")
```

### C. Execute Kernel Commands
```python
run_kd_command(command="!process 0 0") # List all active kernel processes
run_kd_command(command="!thread")      # Inspect current ETHREAD context
run_kd_command(command="vertarget")    # Display kernel OS version banner
```

---

## 4. Multi-Session Orchestration

Debug multiple user-mode applications and kernel drivers simultaneously within a single server instance.

### A. List Active Sessions
```python
list_sessions()
```
*Returns active sessions, indicating debugger type (`CDB` or `KD`) and the active default session.*

### B. Switch Active Default Session
```python
switch_session(session_id="kd-net-50000")
```

---

## 5. Async Execution Control & Resynchronization

When a target is running (`g`), WinDbgMCP provides non-blocking controls to resynchronize or await stop events.

### A. Interrupt a Running Target (CTRL+BREAK)
If a live process or kernel target enters an infinite loop or hangs, force a break:
```python
send_ctrl_break()
```

### B. Wait for Target Break Event
Block asynchronously until a running target hits a breakpoint or exception:
```python
wait_for_break(timeout_seconds=120.0)
```

---

## 6. Google Antigravity Visual Artifact Tools

Generate native visual markdown diagrams and memory table artifacts for **Google Antigravity**.

### A. Render Mermaid Control-Flow Graph (`render_control_flow_graph`)
Disassembles a routine into basic blocks, parses jump/branch targets, and outputs a native **Mermaid flowchart (`graph TD`)**:
```python
render_control_flow_graph(target_address_or_symbol="main", instruction_count=50)
```

### B. Display Formatted Memory Grid (`dump_memory_visual`)
Renders formatted memory bytes with hex, ASCII, and symbol label previews:
```python
dump_memory_visual(address="0x00007ff69b8c1000", length=256)
```

### C. Dump Memory Buffer to Disk (`dump_rwx_payload`)
Dumps raw memory buffers (unpacked code, dynamic buffers) to local files:
```python
dump_rwx_payload(address="0x0000021b00000000", length=4096, output_filename="unpacked_payload.bin")
```

---

## 7. Multi-Client Configuration Adapters (`configs/`)

WinDbgMCP supports all major AI client platforms via pre-configured JSON manifests in `configs/`:

- **Google Antigravity / Claude Code**: `configs/antigravity.mcp.json`
- **Claude Desktop**: `configs/claude_desktop.json`
- **Cursor**: `configs/cursor.mcp.json`
- **Windsurf**: `configs/windsurf.mcp.json`
- **VS Code**: `configs/vscode_mcp.json`
- **OpenAI & OpenRouter**: `configs/openai_agents.json`
- **Local LLMs (Ollama / LM Studio)**: `configs/local_ollama_lmstudio.json`

---

## 8. Automated Bootstrap Installation

Automate environment discovery, symbol directory setup, and AI client registration with one command:

```bash
python scripts/install_mcp.py
```
