import os
import re
import yaml
from forge.packages.common.ui import Colors
from .ui import print_header, print_line

def parse_codex_snapshot(snapshot_content: str) -> dict:
    """Parses the full codex snapshot into a dictionary of file paths and content."""
    print_header("Parsing Snapshot:")
    file_pattern = re.compile(r'^--- START OF FILE: (.*) ---$', re.MULTILINE)
    parts = file_pattern.split(snapshot_content)[1:]
    if not parts:
        raise ValueError("Snapshot appears to be empty or malformed.")
    codex_files = {parts[i]: parts[i+1].strip() for i in range(0, len(parts), 2)}
    print_line(f"Files found: {Colors.PURPLE}{len(codex_files)}{Colors.RESET}")
    return codex_files

def load_yaml_config(filepath: str) -> dict:
    """Loads a YAML file and returns its content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)