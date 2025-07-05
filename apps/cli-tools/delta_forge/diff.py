# --- FILE: foundry/apps/cli-tools/delta_forge/diff.py ---
import os
import difflib
from typing import List

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from .content_processor import process_content_for_output

def generate_diff_text(op: DeltaOperation) -> List[str]:
    """
    Generates a unified diff for a given DeltaOperation, including new actions.
    """
    from_lines: List[str] = []
    to_lines: List[str] = []
    rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"

    # No diff for directory operations
    if op.action in ['CREATE_DIRECTORY']:
        return [f"--- a/dev/null\n", f"+++ b/{rel_path}\n", f"@@ -0,0 +1 @@\n", f"+[Create Directory] {rel_path}\n"]

    # Get original content if file exists
    if os.path.exists(op.path) and op.action != 'CREATE_FILE':
        with open(op.path, 'r', encoding='utf-8') as f:
            from_lines = f.readlines()
    
    current_content_str = "".join(from_lines)
    new_content_str = current_content_str # Default to old content

    # Process content for diff generation to reflect final output
    processed_content = process_content_for_output(op.content)
    processed_replacement = process_content_for_output(op.replacement_content)

    if op.action == 'REPLACE_BLOCK':
        new_content_str = current_content_str.replace(op.target_block, processed_replacement)
    elif op.action == 'INSERT_AFTER_BLOCK':
        new_content_str = current_content_str.replace(op.target_block, op.target_block + processed_replacement)
    elif op.action == 'INSERT_BEFORE_BLOCK':
        new_content_str = current_content_str.replace(op.target_block, processed_replacement + op.target_block)
    elif op.action in ['CREATE_FILE', 'REPLACE_FILE']:
        new_content_str = processed_content
    elif op.action == 'APPEND_TO_FILE':
        new_content_str = current_content_str + processed_content
    elif op.action == 'PREPEND_TO_FILE':
        new_content_str = processed_content + current_content_str
    elif op.action == 'DELETE_FILE':
        new_content_str = ""

    # Ensure content ends with a newline for consistent diff output
    if new_content_str and not new_content_str.endswith('\n'):
        new_content_str += '\n'
        
    to_lines = new_content_str.splitlines(keepends=True)

    if not from_lines and not to_lines:
        return [] # No changes to show

    return list(difflib.unified_diff(from_lines, to_lines, fromfile=f"a/{rel_path}", tofile=f"b/{rel_path}"))
