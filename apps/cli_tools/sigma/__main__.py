#!/usr/bin/env python3
import os
import sys
import argparse
import json

from .snapshot import get_ignore_patterns, process_repo, write_snapshot_to_stdout, write_json_snapshot_to_stdout
from forge.packages.common import ui as loom

def main():
    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))
    
    parser = argparse.ArgumentParser(description="The Sigma tool generates a context snapshot.", add_help=False)
    parser.add_argument('--prompt-file', type=str, help="Path to a file containing the system prompt to prepend.")
    parser.add_argument('--all', action='store_true', help="Scrape all repositories.")
    parser.add_argument('--foundation', action='store_true', help="Scrape the 'foundation' repository.")
    parser.add_argument('--mycelium', action='store_true', help="Scrape the 'mycelium' repository.")
    parser.add_argument('--specs', action='store_true', help="Scrape the 'specs' repository.")
    parser.add_argument('--forge', action='store_true', help="Scrape the 'forge' repository.")
    parser.add_argument('--output-format', type=str, choices=['text', 'json'], default='text', help="The output format.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    render_plan = [{"type": "banner", "symbol": "Σ", "color": "cyan"}]
    is_piped = not sys.stdout.isatty()

    system_prompt = None
    if args.prompt_file:
        prompt_file_path = args.prompt_file
        if not os.path.isabs(prompt_file_path):
            prompt_file_path = os.path.join(foundation_root, prompt_file_path)
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            render_plan.append({"type": "group", "title": "Error", "items": [{"key": "Message", "value": f"Prompt file not found: {prompt_file_path}"}]})
            render_plan.append({"type": "end", "text": "Operation aborted.", "color": "red"})
            loom.render(render_plan)
            return

    repos_to_scrape = []
    if args.all: repos_to_scrape = ['foundation', 'mycelium', 'specs', 'forge']
    else:
        if args.foundation: repos_to_scrape.append('foundation')
        if args.mycelium: repos_to_scrape.append('mycelium')
        if args.specs: repos_to_scrape.append('specs')
        if args.forge: repos_to_scrape.append('forge')

    if not repos_to_scrape:
        render_plan.append({"type": "group", "title": "Error", "items": [{"key": "Message", "value": "No repository specified. Use --all or see --help."}]})
        render_plan.append({"type": "end", "text": "Operation aborted.", "color": "red"})
        loom.render(render_plan)
        return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    ignore_file = os.path.join(script_dir, ".sigmaignore")
    global_ignore_patterns = get_ignore_patterns(ignore_file)
    all_files_to_process = []
    
    repo_items = []
    for repo_name in repos_to_scrape:
        repo_path = os.path.join(foundation_root, repo_name)
        repo_files = process_repo(repo_path, global_ignore_patterns)
        repo_items.append({"key": repo_name, "value": f"({len(repo_files)} files)"})
        all_files_to_process.extend(repo_files)
    
    render_plan.append({"type": "group", "title": "Scoping Repositories", "items": repo_items})

    output_dest = args.output_format
    if not is_piped and args.output_format == 'text':
        output_dest = "terminal (suppressed)"
    elif is_piped:
         output_dest += " to pipe"

    summary_items = [
        {"key": "Repos Scraped", "value": str(len(repos_to_scrape))},
        {"key": "Files Forged", "value": str(len(all_files_to_process))},
        {"key": "Output Sent To", "value": output_dest}
    ]
    render_plan.append({"type": "group", "title": "Snapshot Summary", "items": summary_items})

    if not is_piped and args.output_format == 'text':
        render_plan.append({"type": "prose", "title": "Hint", "text": f"To save output, redirect to a file: sigma --all > snapshot.txt"})

    render_plan.append({"type": "end"})
    
    # --- Corrected Order of Operations ---
    # First, render all UI to stderr
    loom.render(render_plan)

    # Then, as the final step, write the data to stdout if needed
    if args.output_format == 'json':
        write_json_snapshot_to_stdout(all_files_to_process, foundation_root)
    elif is_piped:
        write_snapshot_to_stdout(all_files_to_process, foundation_root, system_prompt)

if __name__ == "__main__":
    main()
