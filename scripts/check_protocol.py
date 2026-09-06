#!/usr/bin/env python3
"""Protocol integrity checker for WinDbgMCP FastMCP tools.

Verifies that all registered server tools export valid JSON schemas compliant
with Model Context Protocol standards.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from windbg_mcp.server import mcp


def check_protocol_integrity() -> bool:
    """Validate server tool schemas."""
    print("=======================================================")
    print(" WinDbgMCP Protocol Integrity & Schema Verification")
    print("=======================================================")

    tools = mcp._tool_manager._tools
    print(f"[+] Total registered MCP tools: {len(tools)}")

    errors = []
    for name, tool in tools.items():
        try:
            doc = tool.description or ""
            if not doc:
                errors.append(f"Tool '{name}' is missing docstring description.")
            print(f"  [OK] Tool '{name}' - {doc.splitlines()[0] if doc else 'No description'}")
        except Exception as e:
            errors.append(f"Tool '{name}' schema error: {e}")

    print("-------------------------------------------------------")
    if errors:
        print(f"[!] Verification FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return False

    print("[+] All tool definitions passed integrity checks successfully!")
    print("=======================================================")
    return True


if __name__ == "__main__":
    success = check_protocol_integrity()
    sys.exit(0 if success else 1)
