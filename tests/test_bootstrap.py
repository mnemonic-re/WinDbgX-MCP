"""Unit tests for bootstrap environment engine."""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.bootstrap import (
    ensure_symbol_directory,
    find_debugext_dll,
    build_mcp_server_config,
)


class TestBootstrapEngine(unittest.TestCase):
    """Test suite for automated setup & registration."""

    def test_ensure_symbol_directory(self):
        """Test symbol directory format generation."""
        sym_str = ensure_symbol_directory()
        self.assertIn("srv*C:\\Symbols*", sym_str)

    def test_build_mcp_server_config(self):
        """Test building server JSON configuration dictionary."""
        cfg = build_mcp_server_config()
        self.assertIn("command", cfg)
        self.assertIn("args", cfg)
        self.assertIn("env", cfg)
        self.assertIn("_NT_SYMBOL_PATH", cfg["env"])
        self.assertIn("_NT_DEBUGGER_EXTENSION_PATH", cfg["env"])


if __name__ == "__main__":
    unittest.main()
