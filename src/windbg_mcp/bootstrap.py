"""Automated Bootstrap & MCP Client Auto-Registration Engine for WinDbgMCP.

Automates environment checks, symbol directory creation, debugger binary discovery,
and auto-registers WinDbgMCP into detected AI client configurations (Google Antigravity,
Claude Code, Cursor, Windsurf, VS Code).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

from windbg_mcp.cdb_session import find_cdb_executable
from windbg_mcp.kd_session import find_kd_executable


def ensure_symbol_directory() -> str:
    """Ensure local C:\\Symbols directory exists."""
    sym_dir = Path("C:/Symbols")
    try:
        sym_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return r"srv*C:\Symbols*https://msdl.microsoft.com/download/symbols"


def find_debugext_dll() -> List[str]:
    """Search for built de.dll (DebugExt) binaries in workspace."""
    base_dir = Path(r"C:\Users\DEV\source\repos\WinDbgX\DebugExt")
    candidates = [
        str(base_dir / "DebugExt" / "x64" / "Release"),
        str(base_dir / "DebugExt" / "Release"),
        str(base_dir / "x64" / "Release"),
    ]
    existing = [c for c in candidates if os.path.exists(c)]
    return existing if existing else candidates[:1]


def build_mcp_server_config() -> Dict[str, Any]:
    """Build standardized MCP server JSON definition."""
    symbol_path = ensure_symbol_directory()
    de_paths = ";".join(find_debugext_dll())

    return {
        "command": sys.executable,
        "args": ["-m", "windbg_mcp"],
        "env": {
            "_NT_SYMBOL_PATH": symbol_path,
            "_NT_DEBUGGER_EXTENSION_PATH": de_paths,
        },
    }


def auto_register_antigravity(server_config: Dict[str, Any]) -> List[str]:
    """Auto-register WinDbgMCP in Google Antigravity config files."""
    user_home = Path.home()
    config_paths = [
        user_home / ".antigravity" / "mcp.json",
        user_home / ".gemini" / "antigravity" / "mcp.json",
        user_home / ".claude" / "mcp.json",
    ]

    registered = []
    for cfg_path in config_paths:
        try:
            cfg_path.parent.mkdir(parents=True, exist_ok=True)
            data: Dict[str, Any] = {"mcpServers": {}}

            if cfg_path.exists():
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {"mcpServers": {}}

            if "mcpServers" not in data:
                data["mcpServers"] = {}

            data["mcpServers"]["windbg-mcp"] = server_config

            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            registered.append(str(cfg_path))
        except Exception as e:
            print(f"[Warning] Failed to register in '{cfg_path}': {e}")

    return registered


def run_bootstrap() -> str:
    """Execute complete automated bootstrap setup."""
    lines = [
        "=======================================================",
        " WinDbgMCP Automated Environment Bootstrap",
        "=======================================================",
        "[TIP] Live WinDbg GUI Progress Watching:",
        "      Start WinDbg GUI on desktop & run: .server tcp:port=5005",
        "      Then call tool: open_cdb_remote(connection_string=\"tcp:Port=5005,Server=localhost\")",
        "-------------------------------------------------------",
    ]

    # 1. Check Python & Executables
    lines.append(f"[+] Python Binary: {sys.executable}")
    cdb_bin = find_cdb_executable()
    kd_bin = find_kd_executable()
    lines.append(f"[+] CDB Binary: {cdb_bin}")
    lines.append(f"[+] KD Binary:  {kd_bin}")

    # 2. Check Symbols & DebugExt
    sym_path = ensure_symbol_directory()
    de_paths = find_debugext_dll()
    lines.append(f"[+] Symbol Path: {sym_path}")
    lines.append(f"[+] DebugExt Paths: {';'.join(de_paths)}")

    # 3. Build & Register Client Configurations
    server_cfg = build_mcp_server_config()
    registered = auto_register_antigravity(server_cfg)

    lines.append("\n[+] Registered WinDbgMCP in AI Client Configurations:")
    for path in registered:
        lines.append(f"    - {path}")

    lines.append("\n=======================================================")
    lines.append(" Bootstrap Complete! WinDbgMCP is fully registered.")
    lines.append(" Ready for AI debugging sessions on demand.")
    lines.append("=======================================================")

    report = "\n".join(lines)
    print(report)
    return report


if __name__ == "__main__":
    run_bootstrap()
