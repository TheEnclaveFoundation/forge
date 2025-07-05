#!/usr/bin/env python3
#
# context (v11.0 - The Forge Edition)
#
# An intelligent script that architects and generates a context snapshot from
# The Enclave Foundation's ecosystem for high-fidelity LLM interaction.
#
# Changelog:
# v11.0 - Updated to operate within the 'forge' repository structure.
#       - Renamed from 'forge-context' to 'context'.
# v10.0 - Updated FOUNDATION_ROOT to be configurable via environment variable.
#

import os
import sys
import argparse
import fnmatch
from typing import List

# --- Configuration & Smart Aesthetics ---

class Colors:
    """A smart color class that disables colors if stderr is not a TTY."""
    IS_A_TTY = sys.stderr.isatty()
    RESET = "\033[0m" if IS_A_TTY else ""
    BOLD = "\033[1m" if IS_A_TTY else ""
    CYAN = "\033[96m" if IS_A_TTY else ""
    GREEN = "\033[92m" if IS_A_TTY else ""
    YELLOW = "\033[93m" if IS_A_TTY else ""
    PURPLE = "\033[95m" if IS_A_TTY else ""
    GREY = "\033[90m" if IS_A_TTY else ""

FOUNDATION_ROOT = os.environ.get(
    "ENCLAVE_FOUNDATION_ROOT",
    os.path.expanduser("~/softrecursion/TheEnclaveFoundation")
)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
IGNORE_FILE = os.path.join(SCRIPT_DIR, ".contextignore")

# --- Core Functions ---

def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def get_ignore_patterns() -> List[str]:
    """Loads patterns from the .contextignore file."""
    if not os.path.exists(IGNORE_FILE):
        eprint(f"{Colors.YELLOW}Warning: .contextignore file not found at '{IGNORE_FILE}'{Colors.RESET}")
        return []
    with open(IGNORE_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

def process_repo(repo_name: str, ignore_patterns: List[str]) -> List[str]:
    """Scrapes a repository, returning a sorted list of file paths with READMEs first."""
    repo_path = os.path.join(FOUNDATION_ROOT, repo_name)
    if not os.path.isdir(repo_path):
        eprint(f"  {Colors.YELLOW}└── ⚠️ Repository '{repo_name}' not found. Skipping.{Colors.RESET}")
        return []

    readme_files, other_files = [], []
    for root, dirs, files in os.walk(repo_path, topdown=True):
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in ignore_patterns)]
        for file in files:
            if any(fnmatch.fnmatch(file, p) for p in ignore_patterns): continue
            file_path = os.path.join(root, file)
            (readme_files if file.upper() == 'README.MD' else other_files).append(file_path)

    readme_files.sort(); other_files.sort()
    all_files = readme_files + other_files
    if all_files:
        eprint(f"  {Colors.GREY}└── Found {len(all_files)} relevant files.{Colors.RESET}")
    return all_files

def write_snapshot_to_stdout(all_files: List[str], system_prompt: str or None):
    """Writes the collected files and system prompt to standard output."""
    eprint(f"\n{Colors.BOLD}{Colors.PURPLE}Writing snapshot to stdout...{Colors.RESET}")
    if system_prompt:
        eprint(f"  {Colors.GREY}└── Injecting system prompt.{Colors.RESET}")
        print("=== SYSTEM PROMPT ===")
        print(system_prompt)
        print("=== END SYSTEM PROMPT ===\n")
        print("################################################################################")
        print("#                          CONTEXT SNAPSHOT START                              #")
        print("################################################################################\n")
    
    for file_path in all_files:
        relative_path = os.path.relpath(file_path, FOUNDATION_ROOT)
        print(f"--- START OF FILE: ./{relative_path} ---")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                print(f_in.read(), end='')
            print("\n", end='')
        except Exception as e: print(f"Error reading file: {e}")
        print(f"--- END OF FILE: ./{relative_path} ---\n")

def print_summary(repos_scraped_count, files_forged_count, is_interactive):
    """Prints the final, beautifully formatted summary box to stderr."""
    BOX_WIDTH = 54
    line1 = "✅ Context Forged ✅"
    line2 = f"Repos Scraped: {repos_scraped_count}"
    line3 = f"Files Forged:  {files_forged_count}"
    line4 = "Output sent to stdout." if not is_interactive else "No output written to terminal."
    
    eprint(f"\n{Colors.GREEN}╔{'═' * (BOX_WIDTH-2)}╗{Colors.RESET}")
    eprint(f"{Colors.GREEN}║{line1.center(BOX_WIDTH-2)}║{Colors.RESET}")
    eprint(f"{Colors.GREEN}╟{'─' * (BOX_WIDTH-2)}╢{Colors.RESET}")
    eprint(f"{Colors.GREEN}║ {Colors.BOLD}{line2:<{BOX_WIDTH-4}} {Colors.RESET}{Colors.GREEN}║{Colors.RESET}")
    eprint(f"{Colors.GREEN}║ {Colors.BOLD}{line3:<{BOX_WIDTH-4}} {Colors.RESET}{Colors.GREEN}║{Colors.RESET}")
    eprint(f"{Colors.GREEN}║ {Colors.GREY}{line4:<{BOX_WIDTH-4}} {Colors.RESET}{Colors.GREEN}║{Colors.RESET}")
    eprint(f"{Colors.GREEN}╚{'═' * (BOX_WIDTH-2)}╝{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description="context: Generates a context snapshot for LLM interaction.", add_help=False)
    parser.add_argument('system_prompt', nargs='?', default=None)
    parser.add_argument('--all', action='store_true', help="Scrape foundation, codex, specs, and forge.")
    parser.add_argument('--foundation', action='store_true')
    parser.add_argument('--codex', action='store_true')
    parser.add_argument('--specs', action='store_true')
    parser.add_argument('--forge', action='store_true') # Changed from 'foundry'
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    IS_INTERACTIVE = sys.stdout.isatty()

    eprint(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════╗
║{Colors.BOLD}            ~-~-~ context ~-~-~                 {Colors.RESET}{Colors.CYAN}║
╚══════════════════════════════════════════════════╝{Colors.RESET}
    """)

    repos_to_scrape = []
    # Updated the default list for --all
    if args.all: repos_to_scrape = ['foundation', 'codex', 'specs', 'forge']
    else:
        if args.foundation: repos_to_scrape.append('foundation')
        if args.codex: repos_to_scrape.append('codex')
        if args.specs: repos_to_scrape.append('specs')
        if args.forge: repos_to_scrape.append('forge') # Changed from 'foundry'

    if not repos_to_scrape:
        eprint(f"{Colors.YELLOW}Error: No repository specified. Use --all or see --help.{Colors.RESET}")
        return

    eprint(f"{Colors.BOLD}{Colors.PURPLE}Initializing...{Colors.RESET}")
    ignore_patterns = get_ignore_patterns()
    all_files_to_process = []
    
    eprint(f"{Colors.BOLD}{Colors.PURPLE}Traversing repositories...{Colors.RESET}")
    for repo in repos_to_scrape:
        eprint(f"{Colors.CYAN}🌿 {repo}{Colors.RESET}")
        repo_files = process_repo(repo, ignore_patterns)
        all_files_to_process.extend(repo_files)

    if not IS_INTERACTIVE:
        write_snapshot_to_stdout(all_files_to_process, args.system_prompt)

    print_summary(len(repos_to_scrape), len(all_files_to_process), IS_INTERACTIVE)

    if IS_INTERACTIVE:
        eprint(f"\n{Colors.YELLOW}Hint: To save output, redirect to a file:{Colors.RESET}")
        eprint(f"{Colors.GREY}$ context --all > snapshot.txt{Colors.RESET}")

if __name__ == "__main__":
    main()