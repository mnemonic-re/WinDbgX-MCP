# WinDbgMCP - Advanced Usage Guide

This comprehensive guide details the advanced capabilities of **WinDbgMCP**, covering crash dump triage, remote debugging, kernel-mode debugging, multi-session management, async execution control, Google Antigravity visual artifact generation, and multi-client environment adapters.

---

## 1. Live GUI Progress Watching (WinDbg GUI Server)

If you want to watch AI debugging progress live on your desktop inside the graphical **WinDbg GUI** (`WinDbgX` / `DbgX.Shell.exe`):

1. Launch **WinDbg GUI** on desktop and open/attach your target application.
2. In the WinDbg GUI command bar at the bottom, type:
   ```text
   .server tcp:port=5005
   ```
3. Connect WinDbgMCP remotely:
   ```python
   open_cdb_remote(connection_string="tcp:Port=5005,Server=localhost")
   ```
*The AI assistant will drive the debugging session remotely while every step executes live before your eyes in your WinDbg GUI window!*

---

## 2. Crash Dump Triage (`open_cdb_dump`)

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

## 3. Remote User-Mode Debugging (`open_cdb_remote`)

Attach a CDB debugger client to a remote user-mode debug server (`-remote`):

### A. Connect via TCP
```python
open_cdb_remote(connection_string="tcp:Port=5005,Server=<TARGET_IP_OR_LOCALHOST>")
```

### B. Connect via Named Pipe
```python
open_cdb_remote(connection_string="npipe:Pipe=WinDbgPipe,Server=<TARGET_HOSTNAME>")
```

---

## 4. Kernel-Mode Debugging (`open_kd_session`)

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

## 5. Multi-Session Orchestration

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

## 6. Async Execution Control & Resynchronization

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

## 7. Google Antigravity Visual Artifact Tools

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

## 8. Multi-Client Configuration Adapters (`configs/`)

WinDbgMCP supports all major AI client platforms via pre-configured JSON manifests in `configs/`:

- **Google Antigravity / Claude Code**: `configs/antigravity.mcp.json`
- **Claude Desktop**: `configs/claude_desktop.json`
- **Cursor**: `configs/cursor.mcp.json`
- **Codex**: `configs/codex.mcp.json`
- **Windsurf**: `configs/windsurf.mcp.json`
- **VS Code**: `configs/vscode_mcp.json`
- **OpenAI & OpenRouter**: `configs/openai_agents.json`
- **Local LLMs (Ollama / LM Studio)**: `configs/local_ollama_lmstudio.json`

---

## 9. Transport Modes (`stdio` vs `sse`)

- **Stdio Mode (IPC Default)**:
  ```bash
  python -m windbg_mcp
  ```
- **SSE HTTP Network Mode**:
  ```bash
  python -m windbg_mcp --sse --port 8000
  ```

---

## 10. Automated Bootstrap Installation

Automate environment discovery, symbol directory setup, and AI client registration with one command:

```bash
python scripts/install_mcp.py
```

---

## 11. Extended Reverse Engineering & Crash Triage Engines

WinDbgMCP includes 5 high-impact automation engines designed for memory forensics, crash analysis, and dynamic analysis:

### A. Memory Snapshot Diffing (`diff_memory_snapshots`)
Compare byte regions, protection flags, and pointer tables between two memory states:
```python
diff_memory_snapshots(
    snapshot_a_hex="48 89 5c 24 08 48 89 6c 24 10",
    snapshot_b_hex="e9 42 12 00 00 48 89 6c 24 10",
    base_address="0x7ff69b8c1000"
)
```

### B. Automated Crash Dump Root-Cause Analyzer (`triage_crash_report`)
Synthesizes `.lastevent`, `!analyze -v`, `kb`, and `.cxr` stack frames into an actionable Root-Cause Analysis (RCA) report:
```python
triage_crash_report(dump_file_path="C:\\Dumps\\crash.dmp")
```

### C. Struct & ReClass.NET Reconstructor (`reconstruct_struct`)
Infers field types, alignments, pointer references, and strings from raw memory bytes to generate C/C++ struct definitions:
```python
reconstruct_struct(
    address="0x021b0000",
    struct_name="PLAYER_OBJECT",
    size=64
)
```

### D. WinAPI Call Tracing (`trace_api_calls`)
Generates breakpoint sets and parameter logging payloads for critical WinAPI entry points (`CreateFileW`, `VirtualAllocEx`, etc.):
```python
trace_api_calls(api_names=["CreateFileW", "VirtualAllocEx", "WriteProcessMemory"])
```

### E. Dynamic PE Header Scanner & Payload Unpacker (`unpack_dynamic_pe`)
Scans dynamic memory for DOS/NT headers (`MZ` / `PE`), validates section tables, and extracts payloads:
```python
unpack_dynamic_pe(
    target_address="0x0000021b00000000",
    dump_to_disk=True,
    output_path="unpacked_module.exe"
)
```

---

## 12. ⚡ Score 8: Advanced Reverse Engineering & Integrity Checks

### 6. DKOM & Kernel Driver Integrity Auditor (`audit_kernel_integrity`)
- **Category**: Kernel Mode & Rootkit Analysis
- **Rationale**: Detecting kernel-level rootkits, DKOM process hiding, and driver hooks.
- **Functionality**: Traverses active `EPROCESS` doubly-linked lists to find hidden processes, audits System Service Descriptor Tables (SSDT), and inspects driver `DRIVER_OBJECT` MajorFunction dispatch arrays for unbacked hook pointers.
```python
audit_kernel_integrity(
    process_list_cmd="!process 0 0",
    ssdt_dump_cmd="dps nt!KiServiceTable L100",
    drivers_dump_cmd="!drvobj \\Driver\\Disk 2"
)
```

### 7. Thread Callstack Anomaly & Stack Spoofing Scanner (`scan_stack_spoofing`)
- **Category**: Exploit Analysis & Detection Evasion
- **Rationale**: Modern malware uses call stack spoofing and ROP chains to bypass security products.
- **Functionality**: Inspects thread stack frames for unbacked return addresses (addresses pointing to unmapped or RWX memory), stack alignment anomalies, and fake stack frames.
```python
scan_stack_spoofing(
    stack_cmd="kb 20",
    memory_map_cmd="!de.memmap"
)
```

---

## 13. 🎯 Score 7: High Utility Debugging Tools

### 8. Automated ROP Chain & Gadget Finder (`find_rop_gadgets`)
- **Category**: Vulnerability Analysis & Exploitation
- **Rationale**: Finding ROP gadgets manually in disassembled modules is time-consuming.
- **Functionality**: Scans loaded executable modules for useful Return-Oriented Programming (ROP) gadgets (e.g. `pop rcx; ret`, `mov [rax], rbx; ret`, `xchg rax, rsp`), filtering and categorizing them by register operation.
```python
find_rop_gadgets(
    disassemble_cmd="u 0x00401000 L100",
    target_module="target.exe"
)
```

### 9. Heuristic Heap Corruption & UAF Detector (`audit_heap_corruption`)
- **Category**: Memory Safety & Vulnerability Triage
- **Rationale**: Heap corruption, double free, and use-after-free (UAF) bugs are notoriously hard to debug.
- **Functionality**: Automates WinDbg `!heap -p -a` and Pageheap diagnostic flags to pinpoint corrupted chunk headers, freed allocation stack traces, and invalid free addresses.
```python
audit_heap_corruption(
    heap_cmd="!heap -p -a 0x021b0000",
    pageheap_cmd="!heap -flt s 0x20"
)

---

## 14. DebugExt (`de.dll`) Extension Loading

WinDbgMCP automatically configures `_NT_DEBUGGER_EXTENSION_PATH` to point to `binaries/extensions/x64` and `x86`.

### Extension Load Commands:
- **Automatic Load**: `.load de` (or `.load de.dll`)
- **Explicit 64-bit Target Load**: `.load binaries\extensions\x64\de.dll`
- **Explicit 32-bit Target Load**: `.load binaries\extensions\x86\de.dll`
- **Unload Extension**: `.unload de`
- **Interactive Help Catalog**: `!de.dxhelp`
```



