#!/usr/bin/env python3
import os
import sys
import argparse

from forge.packages.common.ui import eprint, Colors
from .snapshot import get_ignore_patterns, process_repo, write_snapshot_to_stdout
from .ui import print_banner, print_summary

def main():
    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))
    
    parser = argparse.ArgumentParser(description="Generates a context snapshot for LLM interaction.", add_help=False)
    parser.add_argument('system_prompt', nargs='?', default=None)
    parser.add_argument('--all', action='store_true', help="Scrape foundation, codex, specs, and forge.")
    parser.add_argument('--foundation', action='store_true')
    parser.add_argument('--codex', action='store_true')
    parser.add_argument('--specs', action='store_true')
    parser.add_argument('--forge', action='store_true')
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    print_banner()

    repos_to_scrape = []
    if args.all: repos_to_scrape = ['foundation', 'codex', 'specs', 'forge']
    else:
        if args.foundation: repos_to_scrape.append('foundation')
        if args.codex: repos_to_scrape.append('codex')
        if args.specs: repos_to_scrape.append('specs')
        if args.forge: repos_to_scrape.append('forge')

    if not repos_to_scrape:
        eprint(f"{Colors.YELLOW}Error: No repository specified. Use --all or see --help.{Colors.RESET}"); return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    ignore_file = os.path.join(script_dir, ".sigmaignore")
    ignore_patterns = get_ignore_patterns(ignore_file)
    all_files_to_process = []
    
    eprint(f"{Colors.PURPLE}{Colors.BOLD}🔎 Scoping repositories...{Colors.RESET}")
    for repo_name in repos_to_scrape:
        repo_path = os.path.join(foundation_root, repo_name)
        repo_files = process_repo(repo_path, repo_name, ignore_patterns)
        all_files_to_process.extend(repo_files)

    output_dest = "stdout"
    if sys.stdout.isatty():
        output_dest = "terminal (suppressed)"
    else:
        write_snapshot_to_stdout(all_files_to_process, foundation_root, args.system_prompt)

    print_summary(len(repos_to_scrape), len(all_files_to_process), output_dest)

    if sys.stdout.isatty():
        eprint(f"\n{Colors.YELLOW}Hint: To save output, redirect to a file:{Colors.RESET}")
        eprint(f"{Colors.GREY}$ sigma --all > snapshot.txt{Colors.RESET}")

if __name__ == "__main__":
    main()

