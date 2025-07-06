#!/usr/bin/env python3
import os
import sys
import argparse

from forge.packages.common.ui import eprint, Colors
from .snapshot import get_ignore_patterns, process_repo, write_snapshot_to_stdout
from .ui import print_banner, print_header, print_line, print_summary

def main():
    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))
    
    parser = argparse.ArgumentParser(description="The Sigma tool generates a context snapshot.", add_help=False)
    parser.add_argument('--prompt-file', type=str, help="Path to a file containing the system prompt to prepend to the snapshot.")
    parser.add_argument('--all', action='store_true', help="Scrape all repositories.")
    parser.add_argument('--foundation', action='store_true')
    parser.add_argument('--codex', action='store_true')
    parser.add_argument('--specs', action='store_true')
    parser.add_argument('--forge', action='store_true')
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    print_banner()
    
    system_prompt = None
    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            print_header("Error:")
            eprint(Colors.GREY + '└─┄╴' + Colors.RED + f"Prompt file not found: {args.prompt_file}" + Colors.RESET)
            return

    repos_to_scrape = []
    if args.all: repos_to_scrape = ['foundation', 'codex', 'specs', 'forge']
    else:
        if args.foundation: repos_to_scrape.append('foundation')
        if args.codex: repos_to_scrape.append('codex')
        if args.specs: repos_to_scrape.append('specs')
        if args.forge: repos_to_scrape.append('forge')

    if not repos_to_scrape:
        print_header("Error:")
        eprint(Colors.GREY + '└─┄╴' + Colors.YELLOW + "No repository specified. Use --all or see --help." + Colors.RESET)
        return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    ignore_file = os.path.join(script_dir, ".sigmaignore")
    ignore_patterns = get_ignore_patterns(ignore_file)
    all_files_to_process = []
    
    print_header("Scoping Repositories:")
    for repo_name in repos_to_scrape:
        repo_path = os.path.join(foundation_root, repo_name)
        repo_files = process_repo(repo_path, ignore_patterns)
        print_line(f"{repo_name}")
        all_files_to_process.extend(repo_files)

    is_piped = not sys.stdout.isatty()
    
    if is_piped:
        write_snapshot_to_stdout(all_files_to_process, foundation_root, system_prompt)
    
    print_summary(len(repos_to_scrape), len(all_files_to_process), is_piped)

if __name__ == "__main__":
    main()