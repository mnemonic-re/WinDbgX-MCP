"""Control Flow Graph (CFG) generator for WinDbg disassembly output.

Parses assembly lines into basic blocks and outputs Mermaid flowchart syntax (graph TD)
specifically tailored for visual rendering in Google Antigravity artifacts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


# Regex to parse WinDbg disassembly lines
# Format: 00007ff6`9b8c10f0 4053            push    rbx
# Format: 0x7ff69b8c10f0 : 4883ec20        sub     rsp,20h
LINE_REGEX = re.compile(
    r"^(?:->\s*)?(?:0x)?([0-9a-fA-F]+(?:`[0-9a-fA-F]+)?)\s*(?::)?\s+([0-9a-fA-F]{2,})\s+(.+)$"
)

# Branch instructions
CONDITIONAL_JUMPS = {"je", "jne", "jz", "jnz", "ja", "jae", "jb", "jbe", "jg", "jge", "jl", "jle", "jc", "jnc", "js", "jns"}
UNCONDITIONAL_JUMPS = {"jmp"}
CALL_INSTRUCTIONS = {"call"}
RETURN_INSTRUCTIONS = {"ret", "retn"}


@dataclass
class Instruction:
    address: str
    clean_address: int
    raw_hex: str
    mnemonic: str
    operands: str
    raw_line: str


@dataclass
class BasicBlock:
    block_id: str
    start_address: int
    instructions: List[Instruction] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)  # Target block_ids


def normalize_address(addr_str: str) -> int:
    """Normalize hex address string (stripping backticks and prefixes)."""
    clean = addr_str.replace("`", "").replace("0x", "").strip()
    return int(clean, 16)


def parse_disassembly(raw_disassembly: str) -> List[Instruction]:
    """Parse raw WinDbg disassembly output into Instruction objects."""
    instructions: List[Instruction] = []

    for line in raw_disassembly.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("=") or line_clean.startswith("GO TO"):
            continue

        match = LINE_REGEX.match(line_clean)
        if match:
            addr_raw, raw_hex, instr_text = match.groups()
            clean_addr = normalize_address(addr_raw)

            parts = instr_text.strip().split(maxsplit=1)
            mnemonic = parts[0].lower()
            operands = parts[1] if len(parts) > 1 else ""

            instructions.append(
                Instruction(
                    address=addr_raw,
                    clean_address=clean_addr,
                    raw_hex=raw_hex,
                    mnemonic=mnemonic,
                    operands=operands,
                    raw_line=line_clean,
                )
            )

    return instructions


def extract_jump_target(operands: str) -> Optional[int]:
    """Extract numeric target address from jump operand."""
    # Look for hex pattern like 00007ff6`9b8c1070 or 0x7ff69b8c1070 or 7ff69b8c1070
    match = re.search(r"(?:0x)?([0-9a-fA-F]{4,}(?:`[0-9a-fA-F]{4,})?)", operands)
    if match:
        try:
            return normalize_address(match.group(1))
        except ValueError:
            pass
    return None


def build_cfg_mermaid(raw_disassembly: str, title: str = "Control Flow Graph") -> str:
    """Build a Mermaid flowchart (graph TD) from raw WinDbg disassembly."""
    instructions = parse_disassembly(raw_disassembly)
    if not instructions:
        return "```mermaid\ngraph TD\n    Empty[\"No valid instructions parsed\"]\n```"

    # Identify block entry points (leaders)
    entry_points: Set[int] = {instructions[0].clean_address}
    addr_to_instr: Dict[int, Instruction] = {i.clean_address: i for i in instructions}

    for idx, instr in enumerate(instructions):
        mnem = instr.mnemonic
        target_addr = extract_jump_target(instr.operands)

        if mnem in CONDITIONAL_JUMPS or mnem in UNCONDITIONAL_JUMPS:
            if target_addr and target_addr in addr_to_instr:
                entry_points.add(target_addr)
            if idx + 1 < len(instructions):
                entry_points.add(instructions[idx + 1].clean_address)

        elif mnem in RETURN_INSTRUCTIONS:
            if idx + 1 < len(instructions):
                entry_points.add(instructions[idx + 1].clean_address)

    # Partition instructions into basic blocks
    blocks: List[BasicBlock] = []
    current_block: Optional[BasicBlock] = None

    for instr in instructions:
        if instr.clean_address in entry_points:
            if current_block and current_block.instructions:
                blocks.append(current_block)

            block_id = f"B_0x{instr.clean_address:X}"
            current_block = BasicBlock(block_id=block_id, start_address=instr.clean_address)

        if current_block:
            current_block.instructions.append(instr)

    if current_block and current_block.instructions:
        blocks.append(current_block)

    # Connect edges between blocks
    block_map: Dict[int, BasicBlock] = {b.start_address: b for b in blocks}

    for b_idx, block in enumerate(blocks):
        last_instr = block.instructions[-1]
        mnem = last_instr.mnemonic
        target_addr = extract_jump_target(last_instr.operands)

        if mnem in CONDITIONAL_JUMPS:
            # Branch target edge
            if target_addr in block_map:
                block.successors.append(block_map[target_addr].block_id)
            # Fallthrough edge
            if b_idx + 1 < len(blocks):
                block.successors.append(blocks[b_idx + 1].block_id)

        elif mnem in UNCONDITIONAL_JUMPS:
            if target_addr in block_map:
                block.successors.append(block_map[target_addr].block_id)

        elif mnem not in RETURN_INSTRUCTIONS:
            # Normal fallthrough to next block if not a return
            if b_idx + 1 < len(blocks):
                block.successors.append(blocks[b_idx + 1].block_id)

    # Render Mermaid graph text
    mermaid_lines = ["```mermaid", f"--- title: {title} ---", "graph TD"]

    for block in blocks:
        # Format block label with instructions
        instr_text_lines = []
        for i in block.instructions:
            ops = f" {i.operands}" if i.operands else ""
            instr_text_lines.append(f"0x{i.clean_address:X}: {i.mnemonic}{ops}")

        label_content = "<br/>".join(instr_text_lines)
        mermaid_lines.append(f'    {block.block_id}["{label_content}"]')

    # Add edges
    for block in blocks:
        for succ in block.successors:
            mermaid_lines.append(f"    {block.block_id} --> {succ}")

    mermaid_lines.append("```")
    return "\n".join(mermaid_lines)
