# --- FILE: foundry/apps/cli-tools/delta_forge/parser.py ---
import os
import re
from typing import List

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from .ui import eprint, Colors

def parse_manifest(text: str, strict_mode: bool = False) -> List[DeltaOperation]:
    """
    Parses the manifest text into a list of DeltaOperation objects.
    In strict mode, treats warnings as fatal errors.
    """
    operations = []
    current_op = None
    current_content_section = None
    in_example_block_content = False

    lines = text.splitlines(keepends=True)

    for line_num, line in enumerate(lines):
        stripped_line = line.strip()
        line_warning = None

        # Handle literal example block markers
        if stripped_line == '#! DELTA_EXAMPLE::START':
            if current_op and current_content_section in ['TARGET_BLOCK', 'REPLACEMENT_CONTENT', 'CONTENT']:
                in_example_block_content = True
                if current_content_section == 'TARGET_BLOCK': current_op.target_block += line
                elif current_content_section == 'REPLACEMENT_CONTENT': current_op.replacement_content += line
                elif current_content_section == 'CONTENT': current_op.content += line
            else:
                line_warning = f"`#! DELTA_EXAMPLE::START` found outside a valid content section at line {line_num + 1}."
            if line_warning:
                if strict_mode: raise ValueError(line_warning)
                else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")
            continue
        elif stripped_line == '#! DELTA_EXAMPLE::END':
            if not in_example_block_content:
                line_warning = f"`#! DELTA_EXAMPLE::END` found without a preceding `#! DELTA_EXAMPLE::START` at line {line_num + 1}."
                if strict_mode: raise ValueError(line_warning)
                else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")
            in_example_block_content = False
            if current_content_section == 'TARGET_BLOCK': current_op.target_block += line
            elif current_content_section == 'REPLACEMENT_CONTENT': current_op.replacement_content += line
            elif current_content_section == 'CONTENT': current_op.content += line
            continue

        if in_example_block_content:
            if current_content_section == 'TARGET_BLOCK': current_op.target_block += line
            elif current_content_section == 'REPLACEMENT_CONTENT': current_op.replacement_content += line
            elif current_content_section == 'CONTENT': current_op.content += line
            continue

        if stripped_line == '=== DELTA::START ===':
            if current_op: operations.append(current_op)
            current_op = DeltaOperation(len(operations) + 1)
            current_content_section = None
            continue

        if current_op is None:
            if stripped_line:
                line_warning = f"Ignoring line {line_num + 1} before first Delta START: '{stripped_line}'"
                if strict_mode: raise ValueError(line_warning)
                else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")
            continue

        header_match = re.match(r'^(PATH|ACTION):\s*(.*)$', stripped_line)
        if header_match:
            key, val = header_match.groups()
            if key == 'PATH':
                op_path = val.strip()
                current_op.path = os.path.normpath(os.path.join(FOUNDATION_ROOT, op_path.lstrip('/')))
            elif key == 'ACTION': current_op.action = val.strip()
            current_content_section = key
            continue

        content_section_match = re.match(r'^=== DELTA::(TARGET_BLOCK|REPLACEMENT_CONTENT|CONTENT) ===$', stripped_line)
        if content_section_match:
            current_content_section = content_section_match.groups()[0]
            if current_content_section == 'TARGET_BLOCK': current_op.target_block = ''
            elif current_content_section == 'REPLACEMENT_CONTENT': current_op.replacement_content = ''
            elif current_content_section == 'CONTENT': current_op.content = ''
            continue

        if current_content_section:
            if current_content_section in ['PATH', 'ACTION']:
                line_warning = f"Ignoring unexpected content after {current_content_section} at line {line_num + 1}: '{stripped_line}'"
                if strict_mode: raise ValueError(line_warning)
                else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")
                continue
            
            if current_content_section == 'TARGET_BLOCK': current_op.target_block += line
            elif current_content_section == 'REPLACEMENT_CONTENT': current_op.replacement_content += line
            elif current_content_section == 'CONTENT': current_op.content += line
        elif stripped_line:
            line_warning = f"Ignoring unclassified line {line_num + 1}: '{stripped_line}'"
            if strict_mode: raise ValueError(line_warning)
            else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")

    if current_op: operations.append(current_op)
    return operations
