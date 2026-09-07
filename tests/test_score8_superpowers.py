"""Unit tests for Score 8 Superpower engines (Kernel Integrity Auditor & Stack Spoofing Scanner)."""

import unittest
from windbg_mcp.re_superpowers import (
    audit_kernel_integrity_report,
    scan_stack_spoofing_report,
)


class TestScore8Superpowers(unittest.TestCase):

    def test_kernel_integrity_clean(self):
        raw_proc = "PROCESS ffffe00012345000 SessionId: 1 Cid: 04a0 Peb: 7ff60000 ParentCid: 0210 'notepad.exe'"
        report = audit_kernel_integrity_report(raw_proc)
        self.assertIn("CLEAN / NO DKOM HOOKS DETECTED", report)
        self.assertNotIn("Suspicious / Hidden Process Objects", report)

    def test_kernel_integrity_alerts(self):
        raw_proc = "PROCESS ffffe00012345000 SessionId: 1 Cid: 04a0 Peb: 00000000 ParentCid: 0000 'HIDDEN_PROCESS.EXE'"
        raw_ssdt = "nt!KiServiceTable+0x10: HOOKED BY malicious_driver.sys"
        raw_drv = "DriverObject \\Driver\\Disk: MajorFunction[0] UNBACKED HOOK at 0x90909090"

        report = audit_kernel_integrity_report(raw_proc, raw_ssdt, raw_drv)
        self.assertIn("ALERTS DETECTED", report)
        self.assertIn("Hidden / Unlinked Processes (DKOM)", report)
        self.assertIn("System Service Descriptor Table (SSDT) Hooks", report)
        self.assertIn("Driver Object Dispatch Table Detours", report)

    def test_stack_spoofing_clean(self):
        raw_stack = (
            "00000000`0012f580 00007ff6`9b8c1050 target!main+0x20\n"
            "00000000`0012f590 00007ff6`9b8c10f0 target!BaseThreadInitThunk+0x10"
        )
        report = scan_stack_spoofing_report(raw_stack)
        self.assertIn("CLEAN / VALID CALLSTACK", report)
        self.assertNotIn("Unbacked / Unmapped Memory Return Addresses", report)

    def test_stack_spoofing_alerts(self):
        raw_stack = (
            "00000000`0012f583 00000000`00000005 0x00000005 (Shellcode Return Address)\n"
            "00000000`0012f590 00007ff6`9b8c10f0 target!rop_gadget"
        )
        report = scan_stack_spoofing_report(raw_stack)
        self.assertIn("STACK SPOOFING / ANOMALIES DETECTED", report)
        self.assertIn("Unbacked Return Addresses", report)
        self.assertIn("Stack Alignment Anomalies", report)


if __name__ == "__main__":
    unittest.main()
