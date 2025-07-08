#!/usr/bin/env python3
# --- Iota (Ι/ι) | The Link Harmonizer ---
import os
import sys
import argparse
from typing import List
from dotenv import load_dotenv

from .indexer import build_lexicon_index
from .harmonizer import harmonize_content
from .manifest_generator import generate_manifest
from forge.packages.common import ui as loom
from forge.packages.psi import config # Import config for root path
from .formats.obsidian import ObsidianFormatProvider

# --- Format Provider Dispatcher ---
FORMAT_PROVIDER_MAP = {
    'obsidian': ObsidianFormatProvider,
}

def get_all_markdown_files(repo_paths: List[str]) -> List[str]:
    """Walks the repo paths and returns a list of all markdown files."""
    markdown_files = []
    for repo_path in repo_paths:
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
    return sorted(markdown_files)

def main():
    """Main entry point for the Iota CLI tool."""
    # Load environment variables from .env file at the project root.
    load_dotenv(dotenv_path=os.path.join(config.FOUNDATION_ROOT, '.env'))

    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))

    parser = argparse.ArgumentParser(
        description="Iota (Ι/ι): The Link Harmonizer.",
        add_help=False
    )
    parser.add_argument('--all', action='store_true', help="Harmonize all repositories.")
    parser.add_argument('--mycelium', action='store_true', help="Harmonize the 'mycelium' repository.")
    parser.add_argument('--specs', action='store_true', help="Harmonize the 'specs' repository.")
    parser.add_argument('--forge', action='store_true', help="Harmonize the 'forge' repository.")
    parser.add_argument('--check', action='store_true', help="Check for files that need harmonization without generating a manifest.")
    parser.add_argument('--format', type=str, default='obsidian', choices=['obsidian'], help="The knowledge graph link format to use.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    render_plan = [{"type": "banner", "symbol": "Ι", "color": "cyan"}]
    
    # --- Instantiate the correct format provider ---
    provider_class = FORMAT_PROVIDER_MAP.get(args.format)
    if not provider_class:
        # This case should be prevented by argparse `choices`, but is good practice
        # ... error handling ...
        return
    provider = provider_class()

    repos_to_scan_names = []
    if args.all:
        repos_to_scan_names = ['foundation', 'mycelium', 'specs', 'forge']
    else:
        if args.mycelium: repos_to_scan_names.append('mycelium')
        if args.specs: repos_to_scan_names.append('specs')
        if args.forge: repos_to_scan_names.append('forge')

    if not repos_to_scan_names:
        # ... error handling ...
        return

    repo_paths = [os.path.join(foundation_root, name) for name in repos_to_scan_names]

    lexicon = build_lexicon_index(repo_paths)
    files_to_process = get_all_markdown_files(repo_paths)
    
    setup_items = [
        {"key": "Repos to Scan", "value": ", ".join(repos_to_scan_names)},
        {"key": "Link Format", "value": args.format},
        {"key": "Lexicon Terms", "value": str(len(lexicon))},
        {"key": "Markdown Files", "value": str(len(files_to_process))}
    ]
    render_plan.append({"type": "group", "title": "Iota Harmonizer", "items": setup_items})
    loom.render(render_plan) # Render setup info before starting long process

    manifests_generated = 0
    files_to_fix = []
    for file_path in files_to_process:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        new_content = harmonize_content(original_content, lexicon, provider)

        if new_content != original_content:
            manifests_generated += 1
            if args.check:
                files_to_fix.append({"key": "File", "value": os.path.relpath(file_path, foundation_root)})
            else:
                print(generate_manifest(file_path, new_content, foundation_root))

    final_render_plan = []
    if args.check and files_to_fix:
        final_render_plan.append({"type": "group", "title": "Files to Harmonize", "items": files_to_fix})

    summary_message = f"Found {manifests_generated} files that need harmonization." if args.check else f"Generated {manifests_generated} Delta Manifests for piping."
    final_render_plan.append({"type": "end", "text": summary_message})
    loom.render(final_render_plan)

if __name__ == "__main__":
    main()