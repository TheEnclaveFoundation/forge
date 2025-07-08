import os
import re
import yaml

def parse_codex_snapshot(snapshot_content: str) -> dict:
    """Parses the full codex snapshot into a dictionary of file paths and content."""
    codex_files = {}
    # Split the entire snapshot by the 'START OF FILE' marker
    # The first item will be empty, so we skip it [1:].
    file_blocks = re.split(r'--- START OF FILE: (.*) ---', snapshot_content)[1:]
    
    if not file_blocks:
        raise ValueError("Snapshot appears to be empty or malformed.")

    # The file_blocks list is now [path1, content1, path2, content2, ...]
    file_paths = file_blocks[::2]
    file_contents = file_blocks[1::2]

    for i, path in enumerate(file_paths):
        # For each content block, split it by the 'END OF FILE' marker and take the first part
        content = file_contents[i].split('--- END OF FILE:')[0].strip()
        codex_files[path.strip()] = content
        
    return codex_files

def load_yaml_config(filepath: str) -> dict:
    """Loads a YAML file and returns its content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
