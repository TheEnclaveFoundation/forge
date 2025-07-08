# --- Lambda: Auto-fix Manifest Generator ---
from typing import List, Dict

def generate_fix_manifests(violations: List[Dict], codex_files: Dict[str, str]):
    """
    Iterates through violations and prints a Delta Manifest to stdout for auto-fixable rules.
    """
    manifest_count = 0
    for v in violations:
        # For now, we only know how to auto-fix the "Tool-Making Fallacy Check"
        if v.get("rule_name") == "Tool-Making Fallacy Check" and v.get("error_type") == "contains_text":
            file_path = v.get("file_path")
            details = v.get("details", {})
            forbidden_word = details.get("forbidden_word")
            suggestion = details.get("suggestion")

            if not all([file_path, forbidden_word, suggestion]):
                continue

            original_content = codex_files.get(file_path)
            if not original_content:
                continue
            
            # Perform the replacement
            fixed_content = original_content.replace(forbidden_word, suggestion)

            # To handle multiple fixes in the same file, we must update our
            # in-memory version of the file for the next iteration.
            codex_files[file_path] = fixed_content
            manifest_count += 1
    
    # After all replacements are calculated, generate one manifest per changed file.
    for file_path, content in codex_files.items():
        # A simple way to check if content was changed is needed.
        # This part of the logic needs to be more robust, but for now we'll
        # assume any file with a fixable violation was changed.
        # A better approach would be to compare with the original snapshot.
        is_fixed = any(v.get("file_path") == file_path and v.get("rule_name") == "Tool-Making Fallacy Check" for v in violations)

        if is_fixed:
            print("=== DELTA::START ===")
            print(f"PATH: {file_path}")
            print("ACTION: REPLACE_FILE")
            print("=== DELTA::CONTENT ===")
            print(content) # Changed from end='' to include a newline
