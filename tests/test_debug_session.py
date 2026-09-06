"""
Unit tests for sanitize_debug_output and DebugSession infrastructure.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.filter import sanitize_debug_output
from windbg_mcp.debug_session import DebugSession


class TestSanitizeDebugOutput(unittest.TestCase):
    """Test suite for PII and sensitive data redaction."""

    def test_sanitize_sensitive_data(self):
        """Test redacting tokens, keys, and PII."""
        raw_text = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 and IP 192.168.1.100 target"
        filtered = sanitize_debug_output(raw_text)
        self.assertIn("[REDACTED_TOKEN]", filtered)
        self.assertIn("[REDACTED_IP]", filtered)

    def test_sanitize_paths(self):
        """Test redacting sensitive user directory paths while keeping standard paths."""
        user_path = r"C:\Users\JohnDoe\AppData\Local\Temp\secret.txt"
        filtered = sanitize_debug_output(user_path)
        self.assertIn(r"C:\Users\[REDACTED_USER]", filtered)


class TestDebugSession(unittest.TestCase):
    """Test suite for DebugSession marker generation and command checks."""

    def test_debug_session_marker_generation(self):
        """Test that DebugSession generates unique incrementing markers."""
        session = DebugSession(session_id="test-1", debugger_type="cdb")
        m1 = session._build_marker_command()
        m2 = session._build_marker_command()

        self.assertIn("COMMAND_COMPLETED_MARKER_1", m1)
        self.assertIn("COMMAND_COMPLETED_MARKER_2", m2)
        self.assertEqual(session._seq, 2)

    def test_debug_session_resume_command_check(self):
        """Test detection of execution resume commands."""
        session = DebugSession(session_id="test-2", debugger_type="cdb")
        self.assertTrue(session._is_resume_command("g"))
        self.assertTrue(session._is_resume_command("  gh  "))
        self.assertTrue(session._is_resume_command("gn"))
        self.assertTrue(session._is_resume_command("gc"))
        self.assertTrue(session._is_resume_command("gu"))
        self.assertFalse(session._is_resume_command("k"))
        self.assertFalse(session._is_resume_command("r"))


if __name__ == "__main__":
    unittest.main()
