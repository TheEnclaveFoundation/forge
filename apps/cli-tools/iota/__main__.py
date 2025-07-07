#!/usr/bin/env python3
# --- Iota (Ι/ι) | The Link Harmonizer ---
import os
import sys
import argparse
from typing import List

from forge.packages.common.ui import eprint, Colors
from .ui import print_banner, print_header, print_line, print_end_line
from .indexer import build_lexicon_index
from .harmonizer import harmonize_content
from .manifest_generator import generate_manifest

def get_all_markdown_files(repo_paths: List[str]) -> List[str]:
    """Walks the repo paths and returns a list of all markdown files."""
    markdown_files = []
    for repo_path in repo_paths:
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
    return sorted(markdown_files)

def get_principles_list(lexicon: dict) -> List[str]:
    """Extracts a list of principle names from the full lexicon."""
    principles = []
    for display_text, link_target in lexicon.items():
        if link_target.startswith('Principles/'):
            principles.append(display_text)
    return principles


def main():
    """Main entry point for the Iota CLI tool."""
    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))

    parser = argparse.ArgumentParser(
        description="Iota (Ι/ι): The Link Harmonizer.",
        add_help=False # We add a custom help argument.
    )
    parser.add_argument(
        '--all', action='store_true', help="Harmonize all repositories."
    )
    parser.add_argument(
        '--mycelium', action='store_true', help="Harmonize the 'mycelium' repository."
    )
    parser.add_argument(
        '--specs', action='store_true', help="Harmonize the 'specs' repository."
    )
    parser.add_argument(
        '--forge', action='store_true', help="Harmonize the 'forge' repository."
    )
    parser.add_argument(
        '--check', action='store_true', help="Check for files that need harmonization without generating a manifest."
    )
    # Custom help argument
    parser.add_argument(
        '--help', action='help', help='Show this help message and exit'
    )
    args = parser.parse_args()

    print_banner()

    repos_to_scan_names = []
    if args.all:
        repos_to_scan_names = ['foundation', 'mycelium', 'specs', 'forge']
    else:
        if args.mycelium: repos_to_scan_names.append('mycelium')
        if args.specs: repos_to_scan_names.append('specs')
        if args.forge: repos_to_scan_names.append('forge')

    if not repos_to_scan_names:
        print_header("Error:")
        print_end_line(f"{Colors.YELLOW}No repository specified. Use --all or see --help.{Colors.RESET}")
        return

    print_header("Iota Harmonizer:")

    repo_paths = [os.path.join(foundation_root, name) for name in repos_to_scan_names]

    # 1. Build the Lexicon Index
    lexicon = build_lexicon_index(repo_paths)
    print_line(f"Lexicon Index built with {len(lexicon)} terms.")

    # 2. Extract the list of Principles for special handling
    principles = get_principles_list(lexicon)

    # 3. Gather all markdown files to process
    files_to_process = get_all_markdown_files(repo_paths)
    print_line(f"Found {len(files_to_process)} markdown files to scan.")

    # 4. Process each file and generate manifests if needed
    manifests_generated = 0
    for file_path in files_to_process:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        new_content = harmonize_content(original_content, lexicon, principles)

        if new_content != original_content:
            manifests_generated += 1
            if args.check:
                 eprint(f"{Colors.GREY}├─┄╴{Colors.YELLOW}[CHECK]{Colors.RESET} File needs harmonization: {os.path.relpath(file_path, foundation_root)}")
            else:
                # Print manifest to stdout for piping
                print(generate_manifest(file_path, new_content, foundation_root))


    # 5. Final Summary Report
    if args.check and manifests_generated > 0:
        print_line(f"Found {manifests_generated} files that need harmonization.")
    elif not args.check:
        print_line(f"Generated {manifests_generated} Delta Manifests.")

    print_end_line("Scan complete.")


if __name__ == "__main__":
    main()