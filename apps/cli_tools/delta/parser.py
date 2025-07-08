import os
import re
from typing import List

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from forge.packages.common.ui import eprint, Colors

def parse_manifest(text: str, strict_mode: bool = False) -> List[DeltaOperation]:
    """
    Parses the manifest text into a list of DeltaOperation objects.
    """
    operations = []
    current_op = None
    current_content_section = None
    in_example_block_content = False

    lines = text.splitlines(keepends=True)

    for line_num, line in enumerate(lines):
        stripped_line = line.strip()
        line_warning = None

        if stripped_line == '#! DELTA_EXAMPLE::START':
            if current_op and current_content_section == 'CONTENT':
                in_example_block_content = True
                current_op.content += line
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
            current_op.content += line
            continue

        if in_example_block_content:
            current_op.content += line
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

        header_match = re.match(r'^(PATH|ACTION|SOURCE_PATH|DESTINATION_PATH):\s*(.*)$', stripped_line)
        if header_match:
            key, val = header_match.groups()
            stripped_val = val.strip()
            if key == 'PATH':
                current_op.path = os.path.normpath(os.path.join(FOUNDATION_ROOT, stripped_val.lstrip('/')))
            elif key == 'ACTION': 
                current_op.action = stripped_val
            elif key == 'SOURCE_PATH':
                current_op.source_path = os.path.normpath(os.path.join(FOUNDATION_ROOT, stripped_val.lstrip('/')))
            elif key == 'DESTINATION_PATH':
                current_op.destination_path = os.path.normpath(os.path.join(FOUNDATION_ROOT, stripped_val.lstrip('/')))
            
            current_content_section = key
            continue

        content_section_match = re.match(r'^=== DELTA::CONTENT ===$', stripped_line)
        if content_section_match:
            current_content_section = 'CONTENT'
            current_op.content = ''
            continue

        if current_content_section:
            if current_content_section != 'CONTENT':
                line_warning = f"Ignoring unexpected content after {current_content_section} at line {line_num + 1}: '{stripped_line}'"
                if strict_mode: raise ValueError(line_warning)
                else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")
                continue
            
            current_op.content += line
        elif stripped_line:
            line_warning = f"Ignoring unclassified line {line_num + 1}: '{stripped_line}'"
            if strict_mode: raise ValueError(line_warning)
            else: eprint(f"  {Colors.YELLOW}Warning: {line_warning}{Colors.RESET}")

    if current_op: operations.append(current_op)
    return operations
