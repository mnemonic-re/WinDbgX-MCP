"""Unit tests for dual scratchpad and final report generation."""

import unittest
import os
import sys
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.server import update_scratchpad, generate_final_report, _get_analysis_dir


class TestReportingTools(unittest.TestCase):
    """Test suite for scratchpad.md and Final_Report.md report generation."""

    def setUp(self):
        self.target_name = "test_target_bin.exe"
        self.analysis_dir, self.clean_base = _get_analysis_dir(self.target_name)

    def tearDown(self):
        root_analysis = Path(os.getcwd()) / "analysis" / self.clean_base
        if root_analysis.exists():
            try:
                shutil.rmtree(root_analysis)
            except Exception:
                pass

    def test_update_scratchpad(self):
        """Test appending live notes to scratchpad.md."""
        res = update_scratchpad(
            target_name=self.target_name,
            section_title="Initial Inspection",
            content="Target routine hit at 0x401000",
        )
        self.assertIn("scratchpad.md", res)

        scratchpad_file = self.analysis_dir / "scratchpad.md"
        self.assertTrue(scratchpad_file.exists())
        text = scratchpad_file.read_text(encoding="utf-8")
        self.assertIn("[Initial Inspection]", text)
        self.assertIn("Target routine hit at 0x401000", text)

    def test_generate_final_report(self):
        """Test generating final report from scratchpad."""
        update_scratchpad(
            target_name=self.target_name,
            section_title="Phase 1",
            content="Analyzed main entry point.",
        )
        res = generate_final_report(
            target_name=self.target_name,
            executive_summary="Reverse engineering complete.",
            key_findings=["Secret value identified", "Anti-debug bypassed"],
        )
        self.assertIn("Final_Report.md", res)

        report_file = self.analysis_dir / "test_target_bin_Final_Report.md"
        self.assertTrue(report_file.exists())
        text = report_file.read_text(encoding="utf-8")
        self.assertIn("Executive Summary", text)
        self.assertIn("Reverse engineering complete.", text)
        self.assertIn("Secret value identified", text)
        self.assertIn("Analyzed main entry point.", text)


if __name__ == "__main__":
    unittest.main()
