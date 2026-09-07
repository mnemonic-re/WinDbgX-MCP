"""Unit tests for Score 7 Superpower engines (Automated ROP Gadget Finder & Heap Corruption Detector)."""

import unittest
from windbg_mcp.re_superpowers import (
    find_rop_gadgets_report,
    audit_heap_corruption_report,
)


class TestScore7Superpowers(unittest.TestCase):

    def test_rop_gadgets_clean(self):
        raw_disasm = "0x00401000: add eax, 1; ret"
        report = find_rop_gadgets_report(raw_disasm, target_module="test.dll")
        self.assertIn("Automated ROP Gadget Catalog", report)
        self.assertIn("Found **1** potential ROP gadget", report)
        self.assertIn("Arithmetic & Logic Gadgets", report)

    def test_rop_gadgets_categorization(self):
        raw_disasm = (
            "0x00401010: pop rcx; ret\n"
            "0x00401020: mov dword ptr [rax], rbx; ret\n"
            "0x00401030: xchg rax, rsp; ret\n"
            "0x00401040: add rax, 0x10; ret\n"
        )
        report = find_rop_gadgets_report(raw_disasm, target_module="test_exploit.exe")
        self.assertIn("POP / Register Loader Gadgets", report)
        self.assertIn("Write-What-Where (MOV [reg], reg) Gadgets", report)
        self.assertIn("Stack Pivoting Gadgets", report)
        self.assertIn("Arithmetic & Logic Gadgets", report)

    def test_heap_corruption_clean(self):
        raw_heap = "Index Address Name Debugging options\n1: 00210000 Default Heap"
        report = audit_heap_corruption_report(raw_heap)
        self.assertIn("CLEAN HEAP STATE / NO HEAP ERRORS", report)

    def test_heap_corruption_alerts(self):
        raw_heap = (
            "HEAP ENTRY CORRUPTED at 00214050\n"
            "USE-AFTER-FREE detected in freed chunk 00215000\n"
            "DOUBLE FREE: block 00216000 freed twice\n"
            "FREED BY allocation callstack:"
        )
        report = audit_heap_corruption_report(raw_heap)
        self.assertIn("HEAP CORRUPTION / UAF DETECTED", report)
        self.assertIn("Corrupted Heap Chunk Headers", report)
        self.assertIn("Use-After-Free (UAF) & Invalid Access Alerts", report)
        self.assertIn("Double Free Heap Violations", report)


if __name__ == "__main__":
    unittest.main()
