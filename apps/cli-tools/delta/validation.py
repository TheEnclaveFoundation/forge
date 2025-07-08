# forge/apps/cli-tools/delta/validation.py
import os
from typing import List

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from forge.packages.common.ui import eprint, Colors

def validate_all_operations(ops: List[DeltaOperation], strict_mode: bool = False) -> List[dict]:
    """
    Performs a full validation pass on all deltas, collecting all errors.
    This version is more idempotent: it warns on redundant operations but does not error.
    """
    errors = []
    
    for op in ops:
        rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"
        error = None
        
        file_exists = os.path.exists(op.path)
        dir_exists = os.path.isdir(op.path)
 
        if not op.path or not op.action:
            error = 'Missing PATH or ACTION.'
        elif op.action == 'CREATE_FILE':
            if dir_exists: error = f'Cannot create file; a directory already exists at this path.'
        elif op.action in ['REPLACE_FILE', 'APPEND_TO_FILE', 'PREPEND_TO_FILE']:
            if not file_exists: error = 'File not found.'
        elif op.action in ['REPLACE_BLOCK', 'INSERT_AFTER_BLOCK', 'INSERT_BEFORE_BLOCK']:
            if not file_exists:
                error = 'File not found for block operation.'
            else:
                with open(op.path, 'r', encoding='utf-8') as f: content = f.read()
                target_count = content.count(op.target_block)
                if target_count == 0:
                    error = 'TARGET_BLOCK not found.'
                elif target_count > 1:
                    warning_msg = f"Ambiguous TARGET_BLOCK: Found {target_count} occurrences."
                    if strict_mode:
                        error = warning_msg
                    else:
                        # Warnings are printed directly to stderr as they are not fatal.
                        eprint(f"  {Colors.CYAN}∆ {op.index}:{Colors.RESET} {Colors.YELLOW}[!] {warning_msg} (Will replace first instance){Colors.RESET}")
        
        if error:
            errors.append({'delta_index': op.index, 'path': rel_path, 'error': error})

    return errors