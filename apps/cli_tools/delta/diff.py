import os
import difflib
from typing import List

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from .content_processor import process_content_for_output

def generate_diff_text(op: DeltaOperation) -> List[str]:
    """
    Generates a unified diff for a given DeltaOperation.
    """
    from_lines: List[str] = []
    to_lines: List[str] = []
    
    # Handle MOVE_FILE separately
    if op.action == 'MOVE_FILE':
        rel_source = os.path.relpath(op.source_path, FOUNDATION_ROOT)
        rel_dest = os.path.relpath(op.destination_path, FOUNDATION_ROOT)
        return [f"--- a/{rel_source}\n", f"+++ b/{rel_dest}\n"]

    rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"

    if op.action in ['CREATE_DIRECTORY']:
        return [f"--- a/dev/null\n", f"+++ b/{rel_path}\n", f"@@ -0,0 +1 @@\n", f"+[Create Directory] {rel_path}\n"]

    if os.path.exists(op.path) and op.action != 'CREATE_FILE':
        with open(op.path, 'r', encoding='utf-8') as f:
            from_lines = f.readlines()
    
    current_content_str = "".join(from_lines)
    new_content_str = current_content_str

    processed_content = process_content_for_output(op.content)

    if op.action in ['CREATE_FILE', 'REPLACE_FILE']:
        new_content_str = processed_content
    elif op.action == 'APPEND_TO_FILE':
        new_content_str = current_content_str + processed_content
    elif op.action == 'PREPEND_TO_FILE':
        new_content_str = processed_content + current_content_str
    elif op.action == 'DELETE_FILE':
        new_content_str = ""

    if new_content_str and not new_content_str.endswith('\n'):
        new_content_str += '\n'
        
    to_lines = new_content_str.splitlines(keepends=True)

    if not from_lines and not to_lines:
        return []

    return list(difflib.unified_diff(from_lines, to_lines, fromfile=f"a/{rel_path}", tofile=f"b/{rel_path}"))
