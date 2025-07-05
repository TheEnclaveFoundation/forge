import os
import shutil
from typing import List

from .models import DeltaOperation
from .content_processor import process_content_for_output
from .ui import eprint, Colors
from .config import FOUNDATION_ROOT

def apply_single_operation(op: DeltaOperation):
    """Applies a single delta operation to the filesystem, including new actions."""
    # Ensure parent directory exists for any file-writing operation
    if op.action not in ['CREATE_DIRECTORY', 'DELETE_DIRECTORY']:
        os.makedirs(os.path.dirname(op.path), exist_ok=True)

    # Process content just before writing
    processed_content = process_content_for_output(op.content)
    processed_replacement = process_content_for_output(op.replacement_content)

    if op.action in ['CREATE_FILE', 'REPLACE_FILE']:
        with open(op.path, 'w', encoding='utf-8') as f: f.write(processed_content)
    elif op.action == 'DELETE_FILE':
        if os.path.exists(op.path) and not os.path.isdir(op.path): os.remove(op.path)
    elif op.action == 'CREATE_DIRECTORY':
        os.makedirs(op.path, exist_ok=True)
    elif op.action == 'DELETE_DIRECTORY':
        if os.path.isdir(op.path):
            shutil.rmtree(op.path) # Use shutil.rmtree for robustly deleting non-empty directories
    elif op.action == 'APPEND_TO_FILE':
        with open(op.path, 'a', encoding='utf-8') as f: f.write(processed_content)
    elif op.action == 'PREPEND_TO_FILE':
        with open(op.path, 'r+', encoding='utf-8') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(processed_content + content)
    else: # Block-based operations
        with open(op.path, 'r', encoding='utf-8') as f: content = f.read()
        
        if op.target_block not in content:
            raise ValueError(f"Target block not found in file: {op.path}. This should have been caught by validation.")

        if op.action == 'REPLACE_BLOCK':
            new_content = content.replace(op.target_block, processed_replacement)
        elif op.action == 'INSERT_AFTER_BLOCK':
            new_content = content.replace(op.target_block, op.target_block + processed_replacement)
        elif op.action == 'INSERT_BEFORE_BLOCK':
            new_content = content.replace(op.target_block, processed_replacement + op.target_block)
        
        with open(op.path, 'w', encoding='utf-8') as f: f.write(new_content)

def apply_operations(ops: List[DeltaOperation]):
    """Applies a list of approved delta operations to the filesystem."""
    eprint(f"\n{Colors.PURPLE}{Colors.BOLD}Applying {len(ops)} approved changes...{Colors.RESET}\n")
    for op in ops:
        rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"
        try:
            apply_single_operation(op)
            status_symbol = f"{Colors.GREEN}[✓]{Colors.RESET}"
            error_msg = ""
        except Exception as e:
            status_symbol = f"{Colors.RED}[✗]{Colors.RESET}"
            error_msg = f" {Colors.RED}({e}){Colors.RESET}"

        eprint(f"  {Colors.CYAN}[∆] {op.index}:{Colors.RESET} {Colors.CYAN}{op.action or 'N/A'}{Colors.RESET} ... {status_symbol}{error_msg}")
        eprint(f"      {Colors.GREY}↳ {Colors.PURPLE}{rel_path}{Colors.RESET}")

