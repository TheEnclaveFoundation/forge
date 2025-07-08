import os
import fnmatch
from typing import List
from forge.packages.common.ui import eprint, Colors
import pathspec

def get_ignore_patterns(ignore_file_path: str) -> List[str]:
    """Loads global ignore patterns from a .sigmaignore file."""
    if not os.path.exists(ignore_file_path):
        eprint(f"{Colors.YELLOW}Warning: .sigmaignore file not found at '{ignore_file_path}'{Colors.RESET}")
        return []
    with open(ignore_file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

def process_repo(repo_path: str, global_ignore_patterns: List[str]) -> List[str]:
    """Walks a repository path and returns a sorted list of file paths, respecting all ignore files."""
    if not os.path.isdir(repo_path):
        return []

    readme_files, other_files = [], []
    
    for root, dirs, files in os.walk(repo_path, topdown=True):
        # Combine global spec with any local .gitignore
        current_spec_lines = list(global_ignore_patterns)
        gitignore_path = os.path.join(root, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                current_spec_lines.extend(f.read().splitlines())
        
        spec = pathspec.PathSpec.from_lines('gitwildmatch', current_spec_lines)

        # Filter directories and files based on the combined spec
        paths_to_check_dirs = [os.path.join(os.path.relpath(root, repo_path), d) for d in dirs]
        ignored_dirs = set(os.path.basename(p) for p in spec.match_files(paths_to_check_dirs))
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        paths_to_check_files = [os.path.join(os.path.relpath(root, repo_path), f) for f in files]
        ignored_files = set(os.path.basename(p) for p in spec.match_files(paths_to_check_files))
        
        for file in files:
            if file in ignored_files:
                continue
            
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
        except Exception as e: 
            print(f"Error reading file: {e}")
        print(f"--- END OF FILE: ./{relative_path} ---\n")