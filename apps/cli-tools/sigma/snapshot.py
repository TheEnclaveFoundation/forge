import os
import fnmatch
from typing import List
from forge.packages.common.ui import eprint, Colors

def get_ignore_patterns(ignore_file_path: str) -> List[str]:
    """Loads ignore patterns from a .sigmaignore file."""
    if not os.path.exists(ignore_file_path):
        eprint(f"{Colors.YELLOW}Warning: .sigmaignore file not found at '{ignore_file_path}'{Colors.RESET}")
        return []
    with open(ignore_file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

def process_repo(repo_path: str, ignore_patterns: List[str]) -> List[str]:
    """Walks a repository path and returns a sorted list of file paths, respecting ignore patterns."""
    if not os.path.isdir(repo_path):
        return []

    readme_files, other_files = [], []
    for root, dirs, files in os.walk(repo_path, topdown=True):
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in ignore_patterns)]
        for file in files:
            if any(fnmatch.fnmatch(file, p) for p in ignore_patterns): continue
            file_path = os.path.join(root, file)
            (readme_files if file.upper() == 'README.MD' else other_files).append(file_path)
    
    readme_files.sort()
    other_files.sort()
    return readme_files + other_files

def write_snapshot_to_stdout(all_files: List[str], foundation_root: str, system_prompt: str or None):
    """Writes the final snapshot content to standard output."""
    if system_prompt:
        print("=== SYSTEM PROMPT ===")
        print(system_prompt)
        print("=== END SYSTEM PROMPT ===\n")
        print("################################################################################")
        print("#                                CONTEXT SNAPSHOT START                              #")
        print("################################################################################\n")
    
    for file_path in all_files:
        relative_path = os.path.relpath(file_path, foundation_root)
        print(f"--- START OF FILE: ./{relative_path} ---")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                print(f_in.read(), end='')
            print("\n", end='')
        except Exception as e: print(f"Error reading file: {e}")
        print(f"--- END OF FILE: ./{relative_path} ---\n")