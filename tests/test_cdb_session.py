"""
Unit tests for CDBSession and KDSession high-level session management.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.cdb_session import find_cdb_executable, open_cdb_dump_session
from windbg_mcp.kd_session import find_kd_executable, open_kd_session
from windbg_mcp.debug_session import DebuggerError


class TestCDBSession(unittest.TestCase):
    """Test suite for user-mode CDB session utilities."""

    def test_find_cdb_executable(self):
        """Test finding cdb.exe binary."""
        executable = find_cdb_executable()
        self.assertTrue(isinstance(executable, str))
        self.assertTrue(len(executable) > 0)

    def test_open_cdb_dump_session_nonexistent_file(self):
        """Test that opening a non-existent dump file raises DebuggerError."""
        with self.assertRaises(DebuggerError):
            open_cdb_dump_session(dump_path="C:\\non_existent_path_12345.dmp")


class TestKDSession(unittest.TestCase):
    """Test suite for kernel-mode KD session utilities."""

    def test_find_kd_executable(self):
        """Test finding kd.exe binary."""
        executable = find_kd_executable()
        self.assertTrue(isinstance(executable, str))
        self.assertTrue(len(executable) > 0)


if __name__ == "__main__":
    unittest.main()
