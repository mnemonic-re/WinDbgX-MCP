"""Unit tests for multi-session management tools in server.py."""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.server import (
    SESSIONS,
    list_sessions,
    switch_session,
    close_session,
    get_session,
)
from windbg_mcp.debug_session import DebugSession, DebuggerError


class TestMultiSessionManager(unittest.TestCase):
    """Test suite for server-level multi-session tracking and switching."""

    def setUp(self):
        """Reset global SESSIONS state before each test."""
        SESSIONS.clear()
        import windbg_mcp.server as srv
        srv.ACTIVE_SESSION_ID = None

    def test_list_sessions_empty(self):
        """Test list_sessions when no sessions exist."""
        output = list_sessions()
        self.assertIn("No open debugging sessions", output)

    def test_multi_session_tracking_and_switch(self):
        """Test adding sessions, listing, and switching active target."""
        s1 = DebugSession("session-1", debugger_type="cdb")
        s2 = DebugSession("session-2", debugger_type="kd")

        SESSIONS["session-1"] = s1
        SESSIONS["session-2"] = s2

        # Test listing
        output = list_sessions()
        self.assertIn("session-1", output)
        self.assertIn("session-2", output)

        # Test switching
        switch_res = switch_session("session-2")
        self.assertIn("Switched default active session to 'session-2'", switch_res)

        # Verify get_session returns active default
        active_sess = get_session()
        self.assertEqual(active_sess.session_id, "session-2")

    def test_close_session_cleanup(self):
        """Test closing specific session removes it from registry."""
        s1 = DebugSession("session-1", debugger_type="cdb")
        SESSIONS["session-1"] = s1

        res = close_session("session-1")
        self.assertNotIn("session-1", SESSIONS)
        self.assertIn("closed successfully", res)


if __name__ == "__main__":
    unittest.main()
