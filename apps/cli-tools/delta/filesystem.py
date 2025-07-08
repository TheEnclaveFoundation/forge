# forge/apps/cli-tools/delta/filesystem.py
import os
import shutil
from typing import List, Dict, Any

from .models import DeltaOperation
from .content_processor import process_content_for_output

def apply_single_operation(op: DeltaOperation):
    """Applies a single delta operation to the filesystem, raising an error on failure."""
    if op.action not in ['CREATE_DIRECTORY', 'DELETE_DIRECTORY']:
        os.makedirs(os.path.dirname(op.path), exist_ok=True)

    processed_content = process_content_for_output(op.content)
    processed_replacement = process_content_for_output(op.replacement_content)

    if op.action in ['CREATE_FILE', 'REPLACE_FILE']:
        with open(op.path, 'w', encoding='utf-8') as f: f.write(processed_content)
    elif op.action == 'DELETE_FILE':
        if os.path.exists(op.path) and not os.path.isdir(op.path): os.remove(op.path)
    elif op.action == 'CREATE_DIRECTORY':
        os.makedirs(op.path, exist_ok=True)
    elif op.action == 'DELETE_DIRECTORY':
        if os.path.isdir(op.path): shutil.rmtree(op.path)
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
            raise ValueError(f"Target block not found in file: {op.path}.")

        if op.action == 'REPLACE_BLOCK':
            new_content = content.replace(op.target_block, processed_replacement)
        elif op.action == 'INSERT_AFTER_BLOCK':
            new_content = content.replace(op.target_block, op.target_block + processed_replacement)
        elif op.action == 'INSERT_BEFORE_BLOCK':
            new_content = content.replace(op.target_block, processed_replacement + op.target_block)
        
        with open(op.path, 'w', encoding='utf-8') as f: f.write(new_content)

def apply_operations(ops: List[DeltaOperation]) -> List[Dict[str, Any]]:
    """
    Applies a list of approved delta operations to the filesystem.
    Returns a list of result dictionaries.
    """
    results = []
    for op in ops:
        try:
            apply_single_operation(op)
            results.append({"op": op, "status": "success", "error": None})
        except Exception as e:
            results.append({"op": op, "status": "failure", "error": str(e)})
    return results