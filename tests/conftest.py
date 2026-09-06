"""
Pytest fixtures and configuration for WinDbgMCP test suite.
"""

import os
import sys
import pytest

# Add src/ to sys.path so tests can import windbg_mcp without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.filter import RedactionFilter


@pytest.fixture
def filter_instance():
    """Provides a fresh RedactionFilter instance for testing."""
    return RedactionFilter()
