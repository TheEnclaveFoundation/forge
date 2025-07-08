# forge/apps/cli_tools/delta/__main__.py
#!/usr/bin/env python3
import sys
import json
import argparse
import os
import tempfile
import shutil
from typing import List

from .config import FOUNDATION_ROOT
from .parser import parse_manifest
from .validation import validate_all_operations
from .filesystem import apply_operations, stage_and_apply_transaction
from .diff import generate_diff_text
from forge.packages.common import ui as loom
from forge.packages.common.ui import Colors

def build_error_plan(error_message: str) -> List[dict]:
    """Builds a render plan for a simple error message."""
    return [
        {"type": "banner", "symbol": "∆", "color": "cyan"},
        {"type": "group", "title": "Error", "items": [
            {"key": "Message", "value": error_message}
        ]},
        {"type": "end", "text": "Operation aborted.", "color": "red"}
    ]

def run_dry_run(operations: list):
    """Executes a dry run, showing diffs without applying changes."""
    loom.render([{"type": "banner", "symbol": "∆", "color": "cyan"}])
    
    for op in operations:
        diff_text = "".join(generate_diff_text(op))
        render_plan = [
            {"type": "group", "title": f"Dry Run: Delta {op.index} of {len(operations)}", "items": [
                {"key": "Action", "value": op.action},
                {"key": "Path", "value": os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else 'N/A'}
            ]},
            {"type": "prose", "title": "Diff", "text": diff_text}
        ]
        if op.index < len(operations):
             render_plan.append({"type": "end", "text": "Press Enter to view next Delta..."})
        
        loom.render(render_plan)
        if op.index < len(operations):
            input()

    loom.render([{"type": "end", "text": "Dry Run Complete. No changes were made.", "color": "yellow"}])

def run_transaction(approved_ops: list):
    """
    Applies operations in a temporary directory, committing them only on full success.
    """
    temp_dir = tempfile.mkdtemp(prefix="delta_transaction_")
    results = []
    try:
        results = stage_and_apply_transaction(approved_ops, temp_dir)
    finally:
        shutil.rmtree(temp_dir)

    failure_count = sum(1 for r in results if r['status'] == 'failure')
    success_count = len(results) - failure_count
    
    summary_items = []
    if success_count > 0:
        summary_items.append({"key": "Committed", "value": str(success_count)})
    if failure_count > 0:
        summary_items.append({"key": "Failed", "value": str(failure_count)})

    title = "Transaction Successful"
    end_text = "All changes have been successfully committed."
    color = "green"

    if failure_count > 0:
        title = "Transaction Failed"
        end_text = "Transaction failed and was rolled back. No changes were made."
        color = "red"

    loom.render([
        {"type": "banner", "symbol": "∆", "color": "cyan"},
        {"type": "group", "title": title, "items": summary_items},
        {"type": "end", "text": end_text, "color": color}
    ])

def main():
    parser = argparse.ArgumentParser(description="The Delta tool applies structured changes to the filesystem.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--dry-run', action='store_true', help="Validate and show all diffs without applying changes.")
    parser.add_argument('--strict', action='store_true', help="Parser warnings and ambiguous blocks become fatal errors.")
    parser.add_argument('--transaction', action='store_true', help="Apply all approved changes as a single, atomic transaction.")
    args = parser.parse_args()

    manifest_text = sys.stdin.read()
    if not manifest_text.strip():
        loom.render(build_error_plan("No input received from stdin."))
        return
        
    try:
        operations = parse_manifest(manifest_text, strict_mode=args.strict)
    except ValueError as e:
        loom.render(build_error_plan(f"Error parsing manifest: {e}"))
        sys.exit(1)

    if not operations:
        loom.render([
            {"type": "banner", "symbol": "∆", "color": "cyan"},
            {"type": "end", "text": "No valid Delta operations found.", "color": "yellow"}
        ])
        return
    
    validation_errors = validate_all_operations(operations, strict_mode=args.strict)
    if validation_errors:
        error_items = [{"key": f"Delta {err['delta_index']}", "value": f"{err['path']} - {err['error']}"} for err in validation_errors]
        loom.render([
            {"type": "banner", "symbol": "∆", "color": "cyan"},
            {"type": "group", "title": "Validation Failed", "items": error_items},
            {"type": "end", "text": "Aborting.", "color": "red"}
        ])
        sys.exit(1)
    
    if args.dry_run:
        run_dry_run(operations)
        return

    # --- Interactive Approval Loop ---
    loom.render([{"type": "banner", "symbol": "∆", "color": "cyan"}])
    approved_ops, apply_all, skipped_count = [], False, 0
    try:
        with open('/dev/tty') as tty:
            for op in operations:
                diff_text = "".join(generate_diff_text(op))
                render_plan = [
                    {"type": "group", "title": f"Reviewing Delta {op.index} of {len(operations)}", "items": [
                        {"key": "Action", "value": op.action},
                        {"key": "Path", "value": os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else 'N/A'}
                    ]},
                    {"type": "prose", "title": "Diff", "text": diff_text}
                ]
                loom.render(render_plan)

                if apply_all:
                    loom.eprint(f"{Colors.GREY}├─┄╴{Colors.GREEN}Applying automatically...{Colors.RESET}")
                    approved_ops.append(op)
                    continue

                loom.eprint(f"{Colors.GREY}├─┄╴{Colors.YELLOW}Apply this change? [y/n/a/q] {Colors.RESET} ", end='')
                sys.stderr.flush()
                confirm = tty.readline().strip().lower()
                
                if confirm == 'y': approved_ops.append(op)
                elif confirm == 'a': apply_all = True; approved_ops.append(op)
                elif confirm == 'q': skipped_count = len(operations) - len(approved_ops); break
                else: skipped_count += 1
    except (KeyboardInterrupt, EOFError):
        loom.eprint("\n\nOperation cancelled by user.")
        skipped_count = len(operations) - len(approved_ops)
    except OSError:
         loom.render(build_error_plan("Could not open controlling terminal. Use --dry-run or pipe from a file."))

    # --- Final Application Step ---
    if approved_ops:
        if args.transaction:
            run_transaction(approved_ops)
            return

        results = apply_operations(approved_ops)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        failure_count = sum(1 for r in results if r['status'] == 'failure')
        
        summary_items = []
        if success_count > 0:
            summary_items.append({"key": "Applied", "value": str(success_count)})
        if failure_count > 0:
            summary_items.append({"key": "Failed", "value": str(failure_count)})
        if skipped_count > 0:
            summary_items.append({"key": "Skipped", "value": str(skipped_count)})
        
        if not summary_items:
            summary_items.append({"key": "Status", "value": "No changes were applied."})
        
        loom.render([
            {"type": "group", "title": "Summary", "items": summary_items},
            {"type": "end"}
        ])

if __name__ == "__main__":
    main()