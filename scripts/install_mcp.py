#!/usr/bin/env python3
"""Installer script for WinDbgMCP - Auto-configures environment and registers server in AI client configurations."""

import os
import sys

# Ensure src/ is on pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.bootstrap import run_bootstrap

if __name__ == "__main__":
    run_bootstrap()
