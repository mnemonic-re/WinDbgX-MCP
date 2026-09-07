"""Unit tests for dynamic custom filter script loader."""

import unittest
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.custom_hook import load_custom_hook as load_filter_script, get_active_custom_hook as get_active_filter_script
from windbg_mcp.filter import sanitize_debug_output


class TestFilterScript(unittest.TestCase):
    """Test suite for user-defined Python filter script callbacks."""

    def test_load_and_apply_custom_filter(self):
        """Test loading custom filter script and applying process_output callback."""
        script_content = """
def process_output(text, context):
    return text.replace("SECRET_TOKEN", "[CUSTOM_SCRUBBED_TOKEN]")
"""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write(script_content)
            temp_path = f.name

        try:
            filter_obj = load_filter_script(temp_path)
            self.assertIsNotNone(filter_obj)
            self.assertEqual(get_active_filter_script(), filter_obj)

            raw = "Debugger output with SECRET_TOKEN inside"
            sanitized = sanitize_debug_output(raw)
            self.assertIn("[CUSTOM_SCRUBBED_TOKEN]", sanitized)
            self.assertNotIn("SECRET_TOKEN", sanitized)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
