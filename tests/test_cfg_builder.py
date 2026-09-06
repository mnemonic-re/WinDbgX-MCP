"""Unit tests for Control Flow Graph (CFG) builder."""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from windbg_mcp.cfg_builder import (
    build_cfg_mermaid,
    extract_jump_target,
    parse_disassembly,
)


SAMPLE_DISASM = """
00007ff6`9b8c10f0 4053            push    rbx
00007ff6`9b8c10f2 4883ec20        sub     rsp,20h
00007ff6`9b8c10f6 488d0d83110000  lea     rcx,[AdvancedTarget!`string' (00007ff6`9b8c2280)]
00007ff6`9b8c10fd e86effffff      call    AdvancedTarget!printf (00007ff6`9b8c1070)
00007ff6`9b8c1102 bafeca0000      mov     edx,0CAFEh
00007ff6`9b8c1107 488d0da2110000  lea     rcx,[AdvancedTarget!`string' (00007ff6`9b8c22b0)]
00007ff6`9b8c110e e8fdfeffff      call    AdvancedTarget!wprintf (00007ff6`9b8c1010)
00007ff6`9b8c1113 488d1566150000  lea     rdx,[AdvancedTarget!`string' (00007ff6`9b8c2680)]
00007ff6`9b8c111a 7407            je      00007ff6`9b8c1123
00007ff6`9b8c111c b801000000      mov     eax,1
00007ff6`9b8c1121 eb02            jmp     00007ff6`9b8c1125
00007ff6`9b8c1123 31c0            xor     eax,eax
00007ff6`9b8c1125 4883c420        add     rsp,20h
00007ff6`9b8c1129 5b              pop     rbx
00007ff6`9b8c112a c3              ret
"""


class TestCFGBuilder(unittest.TestCase):
    """Test suite for CFG parsing and Mermaid output generation."""

    def test_parse_disassembly(self):
        """Test parsing WinDbg disassembly output lines."""
        instructions = parse_disassembly(SAMPLE_DISASM)
        self.assertEqual(len(instructions), 15)
        self.assertEqual(instructions[0].mnemonic, "push")
        self.assertEqual(instructions[0].clean_address, 0x7FF69B8C10F0)

    def test_extract_jump_target(self):
        """Test extracting numeric jump target addresses."""
        target = extract_jump_target("00007ff6`9b8c1123")
        self.assertEqual(target, 0x7FF69B8C1123)

    def test_build_cfg_mermaid(self):
        """Test generating Mermaid flowchart TD syntax."""
        mermaid_out = build_cfg_mermaid(SAMPLE_DISASM, title="Test CFG")
        self.assertIn("```mermaid", mermaid_out)
        self.assertIn("graph TD", mermaid_out)
        self.assertIn("--- title: Test CFG ---", mermaid_out)
        self.assertIn("B_0x7FF69B8C10F0", mermaid_out)
        self.assertIn("-->", mermaid_out)


if __name__ == "__main__":
    unittest.main()
