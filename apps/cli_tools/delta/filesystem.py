# forge/apps/cli_tools/delta/filesystem.py
import os
import shutil
from typing import List, Dict, Any
from copy import deepcopy

from .models import DeltaOperation
from .content_processor import process_content_for_output
from .config import FOUNDATION_ROOT

def apply_single_operation(op: DeltaOperation):
    """Applies a single delta operation to the filesystem, raising an error on failure."""
    if op.action == 'MOVE_FILE':
        os.makedirs(os.path.dirname(op.destination_path), exist_ok=True)
        os.rename(op.source_path, op.destination_path)
        return

    if op.action not in ['CREATE_DIRECTORY', 'DELETE_DIRECTORY', 'DELETE_FILE']:
        os.makedirs(os.path.dirname(op.path), exist_ok=True)

    processed_content = process_content_for_output(op.content)

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

def apply_operations(ops: List[DeltaOperation]) -> List[Dict[str, Any]]:
    """Applies a list of approved delta operations directly."""
    results = []
    for op in ops:
        try:
            apply_single_operation(op)
            results.append({"op": op, "status": "success", "error": None})
        except Exception as e:
            results.append({"op": op, "status": "failure", "error": str(e)})
    return results

def stage_and_apply_transaction(ops: List[DeltaOperation], temp_dir: str) -> List[Dict[str, Any]]:
    """
    Stages files for a transaction, applies operations, and commits back on success.
    """
    staged_ops = []
    affected_files = set()

    for op in ops:
        new_op = deepcopy(op)
        source_file = op.source_path if op.action == 'MOVE_FILE' else op.path
        if source_file and os.path.exists(source_file) and not os.path.isdir(source_file):
            affected_files.add(source_file)
        
        if new_op.path:
            new_op.path = os.path.join(temp_dir, os.path.relpath(new_op.path, FOUNDATION_ROOT))
        if new_op.source_path:
            new_op.source_path = os.path.join(temp_dir, os.path.relpath(new_op.source_path, FOUNDATION_ROOT))
        if new_op.destination_path:
            new_op.destination_path = os.path.join(temp_dir, os.path.relpath(new_op.destination_path, FOUNDATION_ROOT))
        
        staged_ops.append(new_op)

    for file_path in affected_files:
        staged_path = os.path.join(temp_dir, os.path.relpath(file_path, FOUNDATION_ROOT))
        os.makedirs(os.path.dirname(staged_path), exist_ok=True)
        shutil.copy2(file_path, staged_path)

    results = apply_operations(staged_ops)
    
    failures = [res for res in results if res['status'] == 'failure']
    if failures:
        return failures

    # --- Commit Phase ---
    # First, handle deletions and moves in the actual directory
    for op in ops:
        if op.action == 'DELETE_FILE' and os.path.exists(op.path):
            os.remove(op.path)
        elif op.action == 'MOVE_FILE' and os.path.exists(op.source_path):
            os.remove(op.source_path)

    # Then, copy the new/modified files from the staging area back to the project.
    shutil.copytree(temp_dir, FOUNDATION_ROOT, dirs_exist_ok=True)
    
    return results
