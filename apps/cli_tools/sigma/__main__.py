#!/usr/bin/env python3
import os
import sys
import argparse

from .snapshot import get_ignore_patterns, process_repo, write_snapshot_to_stdout
from forge.packages.common import ui as loom

def main():
    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))
    
    parser = argparse.ArgumentParser(description="The Sigma tool generates a context snapshot.", add_help=False)
    parser.add_argument('--prompt-file', type=str, help="Path to a file containing the system prompt to prepend to the snapshot.")
    parser.add_argument('--all', action='store_true', help="Scrape all repositories.")
    parser.add_argument('--foundation', action='store_true', help="Scrape the 'foundation' repository.")
    parser.add_argument('--mycelium', action='store_true', help="Scrape the 'mycelium' repository.")
    parser.add_argument('--specs', action='store_true', help="Scrape the 'specs' repository.")
    parser.add_argument('--forge', action='store_true', help="Scrape the 'forge' repository.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    # --- Start building the render plan ---
    render_plan = [
        {"type": "banner", "symbol": "Σ", "color": "cyan"}
    ]

    system_prompt = None
    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            render_plan.append({"type": "group", "title": "Error", "items": [{"key": "Message", "value": f"Prompt file not found: {args.prompt_file}"}]})
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
    ignore_patterns = get_ignore_patterns(ignore_file)
    all_files_to_process = []
    
    repo_items = []
    for repo_name in repos_to_scrape:
        repo_path = os.path.join(foundation_root, repo_name)
        repo_files = process_repo(repo_path, ignore_patterns)
        repo_items.append({"key": repo_name, "value": f"({len(repo_files)} files)"})
        all_files_to_process.extend(repo_files)
    
    render_plan.append({"type": "group", "title": "Scoping Repositories", "items": repo_items})

    is_piped = not sys.stdout.isatty()
    
    if is_piped:
        write_snapshot_to_stdout(all_files_to_process, foundation_root, system_prompt)
    
    # --- Final Summary ---
    output_dest = "pipe" if is_piped else "terminal (suppressed)"
    summary_items = [
        {"key": "Repos Scraped", "value": str(len(repos_to_scrape))},
        {"key": "Files Forged", "value": str(len(all_files_to_process))},
        {"key": "Output Sent To", "value": output_dest}
    ]
    render_plan.append({"type": "group", "title": "Snapshot Summary", "items": summary_items})

    if not is_piped:
        render_plan.append({"type": "prose", "title": "Hint", "text": "To save output, redirect to a file: sigma --all > snapshot.txt"})

    render_plan.append({"type": "end"})
    
    loom.render(render_plan)

if __name__ == "__main__":
    main()