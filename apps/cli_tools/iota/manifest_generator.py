# --- Iota: Manifest Generator ---
# This module contains the logic for Component 3: Delta Manifest Generation.
# It will take modified file content and produce a valid REPLACE_FILE Delta Manifest
# string, ready to be printed to stdout.

def generate_manifest(file_path: str, new_content: str, foundation_root: str) -> str:
    """
    Generates a single, complete REPLACE_FILE Delta Manifest as a string.
    """
    import os

    relative_path = os.path.relpath(file_path, foundation_root)
    # Ensure consistent path format
    relative_path = './' + relative_path.replace('\\', '/')

    manifest = [
        "=== DELTA::START ===",
        f"PATH: {relative_path}",
        "ACTION: REPLACE_FILE",
        "=== DELTA::CONTENT ===",
        new_content
    ]
    return "\n".join(manifest)
