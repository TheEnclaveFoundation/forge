import os
from typing import List

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from .ui import eprint, Colors

def validate_all_operations(ops: List[DeltaOperation], strict_mode: bool = False) -> List[dict]:
    """
    Performs a full validation pass on all deltas, collecting all errors.
    """
    eprint(f"{Colors.BOLD}{Colors.PURPLE}🔎 Validating...{Colors.RESET}")
    errors = []
    temp_file_states = {} # path -> content or 'IS_A_DIRECTORY'

    for op in ops:
        rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"
        error = None
        
        # Get current state for checks, including the simulation
        file_exists = os.path.exists(op.path) or op.path in temp_file_states
        dir_exists = os.path.isdir(op.path) or temp_file_states.get(op.path) == 'IS_A_DIRECTORY'

        if not op.path or not op.action:
            error = 'Missing PATH or ACTION.'
        elif op.action == 'CREATE_FILE':
            if file_exists: error = 'File already exists.'
        elif op.action in ['DELETE_FILE', 'REPLACE_FILE', 'REPLACE_BLOCK', 'APPEND_TO_FILE', 'PREPEND_TO_FILE', 'INSERT_AFTER_BLOCK', 'INSERT_BEFORE_BLOCK']:
            if not file_exists: error = 'File not found.'
        elif op.action == 'CREATE_DIRECTORY':
            if file_exists or dir_exists: error = 'Directory or file with that name already exists.'
        elif op.action == 'DELETE_DIRECTORY':
            if not dir_exists: error = 'Directory not found.'
        
        if not error and op.action in ['REPLACE_BLOCK', 'INSERT_AFTER_BLOCK', 'INSERT_BEFORE_BLOCK']:
            content = temp_file_states.get(op.path)
            if content is None:
                with open(op.path, 'r', encoding='utf-8') as f: content = f.read()
            
            target_count = content.count(op.target_block)
            if target_count == 0:
                error = 'TARGET_BLOCK not found.'
            elif target_count > 1:
                warning_msg = f"Ambiguous TARGET_BLOCK: Found {target_count} occurrences."
                if strict_mode:
                    error = warning_msg
                else:
                    eprint(f"  {Colors.CYAN}∆ {op.index}:{Colors.RESET} {Colors.YELLOW}[!] {warning_msg}{Colors.RESET}")
                    error = None 

        if error:
            errors.append({'delta_index': op.index, 'path': rel_path, 'error': error})
            eprint(f"  {Colors.CYAN}∆ {op.index}:{Colors.RESET} {Colors.RED}[✗] {error}{Colors.RESET}")
        else:
            current_content_for_warning = temp_file_states.get(op.path, open(op.path).read() if os.path.exists(op.path) and not os.path.isdir(op.path) else "")
            is_ambiguous_warning = op.action in ['REPLACE_BLOCK', 'INSERT_AFTER_BLOCK', 'INSERT_BEFORE_BLOCK'] and not strict_mode and current_content_for_warning.count(op.target_block) > 1
            if not is_ambiguous_warning:
                 eprint(f"  {Colors.CYAN}∆ {op.index}:{Colors.RESET} {Colors.GREEN}[✓]{Colors.RESET}")

            # Simulate the change for the next validation step
            if op.action in ['CREATE_FILE', 'REPLACE_FILE']:
                temp_file_states[op.path] = op.content
            elif op.action == 'REPLACE_BLOCK':
                content = temp_file_states.get(op.path, None) or open(op.path).read()
                temp_file_states[op.path] = content.replace(op.target_block, op.replacement_content)
            elif op.action == 'APPEND_TO_FILE':
                content = temp_file_states.get(op.path, None) or open(op.path).read()
                temp_file_states[op.path] = content + op.content
            elif op.action == 'PREPEND_TO_FILE':
                content = temp_file_states.get(op.path, None) or open(op.path).read()
                temp_file_states[op.path] = op.content + content
            elif op.action == 'INSERT_AFTER_BLOCK':
                content = temp_file_states.get(op.path, None) or open(op.path).read()
                temp_file_states[op.path] = content.replace(op.target_block, op.target_block + op.replacement_content)
            elif op.action == 'INSERT_BEFORE_BLOCK':
                content = temp_file_states.get(op.path, None) or open(op.path).read()
                temp_file_states[op.path] = content.replace(op.target_block, op.replacement_content + op.target_block)
            elif op.action == 'CREATE_DIRECTORY':
                temp_file_states[op.path] = 'IS_A_DIRECTORY'
            elif op.action in ['DELETE_FILE', 'DELETE_DIRECTORY']:
                if op.path in temp_file_states: del temp_file_states[op.path]

    return errors
