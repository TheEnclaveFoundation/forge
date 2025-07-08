# forge/apps/cli_tools/delta/validation.py
import os
from typing import List, Dict, Any

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from forge.packages.common.ui import eprint, Colors

def validate_all_operations(ops: List[DeltaOperation], strict_mode: bool = False) -> List[Dict[str, Any]]:
    """
    Performs a full validation pass on all deltas, collecting all errors.
    """
    errors = []
    
    for op in ops:
        rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"
        error = None
        
        # Default path check
        if op.action not in ['MOVE_FILE']: # MOVE_FILE uses different path headers
             if not op.path: error = "Missing PATH header."
        
        if not op.action:
            error = 'Missing ACTION.'
        elif op.action == 'CREATE_FILE':
            if os.path.isdir(op.path): error = f'Cannot create file; a directory already exists at this path.'
        elif op.action in ['REPLACE_FILE', 'APPEND_TO_FILE', 'PREPEND_TO_FILE', 'DELETE_FILE']:
            if not os.path.exists(op.path) or os.path.isdir(op.path): error = 'File not found for this operation.'
        elif op.action == 'MOVE_FILE':
            if not op.source_path or not op.destination_path:
                error = "MOVE_FILE requires both SOURCE_PATH and DESTINATION_PATH headers."
            elif not os.path.exists(op.source_path):
                error = f"Source file for move operation not found: {op.source_path}"
        
        if error:
            errors.append({'delta_index': op.index, 'path': rel_path, 'error': error})

    return errors
