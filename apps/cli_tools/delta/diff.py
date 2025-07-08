import os
import difflib
from typing import List, Dict, Any

from .models import DeltaOperation
from .config import FOUNDATION_ROOT
from .content_processor import process_content_for_output

def generate_diff_objects(op: DeltaOperation) -> List[Dict[str, Any]]:
    """
    Generates a structured list of diff objects, each with content and a color hint.
    """
    from_lines: List[str] = []
    to_lines: List[str] = []
    
    if op.action == 'MOVE_FILE':
        rel_source = os.path.relpath(op.source_path, FOUNDATION_ROOT)
        rel_dest = os.path.relpath(op.destination_path, FOUNDATION_ROOT)
        return [
            {"content": f"--- a/{rel_source}", "color": "yellow"},
            {"content": f"+++ b/{rel_dest}", "color": "yellow"}
        ]

    rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else "N/A"

    if op.action in ['CREATE_DIRECTORY']:
        return [
            {"content": f"--- a/dev/null", "color": "grey"},
            {"content": f"+++ b/{rel_path}", "color": "grey"},
            {"content": f"@@ -0,0 +1 @@", "color": "cyan"},
            {"content": f"+ [Create Directory] {rel_path}", "color": "green"},
        ]

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

    diff_lines = list(difflib.unified_diff(from_lines, to_lines, fromfile=f"a/{rel_path}", tofile=f"b/{rel_path}"))
    
    diff_objects = []
    for line in diff_lines:
        color = "white"
        if line.startswith('+') and not line.startswith('+++'):
            color = "green"
        elif line.startswith('-') and not line.startswith('---'):
            color = "red"
        elif line.startswith('@@'):
            color = "cyan"
        elif line.startswith('---') or line.startswith('+++'):
            color = "yellow"
        diff_objects.append({"content": line, "color": color})
        
    return diff_objects
