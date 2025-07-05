#!/usr/bin/env python3
import sys
import json
import argparse
import os

from .config import FOUNDATION_ROOT
from .parser import parse_manifest
from .validation import validate_all_operations
from .filesystem import apply_operations
from .diff import generate_diff_text
from forge.packages.common.ui import eprint, clear_screen, Colors
from .ui import print_banner, print_review_header, print_final_summary

def run_dry_run(operations: list):
    eprint(f"\n{Colors.PURPLE}{Colors.BOLD}Executing dry run... No changes will be made.{Colors.RESET}")
    for op in operations:
        clear_screen()
        print_banner()
        rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else 'N/A'
        print_review_header(op.index, len(operations), op.action, rel_path)
        for line in generate_diff_text(op):
            color = Colors.GREEN if line.startswith('+') else Colors.RED if line.startswith('-') else Colors.CYAN if line.startswith('@@') else Colors.GREY
            eprint(f"{color}{line.strip()}{Colors.RESET}")
        eprint(f"{Colors.GREY}──────────────────────────────────{Colors.RESET}")
        if op.index < len(operations):
             input(f"{Colors.YELLOW}Press Enter to view next Delta...{Colors.RESET}")
    eprint(f"\n{Colors.PURPLE}{Colors.BOLD}Dry run complete.{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description="Applies structured changes to the filesystem.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--dry-run', action='store_true', help="Validate and show all diffs without applying changes.")
    parser.add_argument('--strict', action='store_true', help="Parser warnings and ambiguous blocks become fatal errors.")
    args = parser.parse_args()
    print_banner()
    manifest_text = sys.stdin.read()
    if not manifest_text.strip():
        eprint(f"{Colors.YELLOW}No input received. Exiting.{Colors.RESET}"); return
    try:
        operations = parse_manifest(manifest_text, strict_mode=args.strict)
    except ValueError as e:
        eprint(f"\n{Colors.RED}{Colors.BOLD}Error parsing manifest: {e}{Colors.RESET}"); sys.exit(1)
    if not operations:
        eprint(f"\n{Colors.YELLOW}No valid Delta operations found.{Colors.RESET}"); return
    validation_errors = validate_all_operations(operations, strict_mode=args.strict)
    if validation_errors:
        eprint(f"\n{Colors.RED}{Colors.BOLD}Validation failed. Aborting.{Colors.RESET}")
        if not sys.stdout.isatty(): print(json.dumps(validation_errors, indent=2))
        sys.exit(1)
    if args.dry_run:
        run_dry_run(operations); return
    approved_ops, apply_all, skipped_count = [], False, 0
    try:
        with open('/dev/tty') as tty:
            for op in operations:
                clear_screen(); print_banner()
                rel_path = os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else 'N/A'
                print_review_header(op.index, len(operations), op.action, rel_path)
                for line in generate_diff_text(op):
                    color = Colors.GREEN if line.startswith('+') else Colors.RED if line.startswith('-') else Colors.CYAN if line.startswith('@@') else Colors.GREY
                    eprint(f"{color}{line.strip()}{Colors.RESET}")
                eprint(f"{Colors.GREY}──────────────────────────────────{Colors.RESET}")
                if apply_all:
                    eprint(f"{Colors.GREEN}Applying automatically...{Colors.RESET}"); approved_ops.append(op); continue
                sys.stderr.write(f"{Colors.YELLOW}Apply this change? [y/n/a/q] {Colors.RESET} "); sys.stderr.flush()
                confirm = tty.readline().strip().lower()
                if confirm == 'y': approved_ops.append(op)
                elif confirm == 'a': apply_all = True; approved_ops.append(op)
                elif confirm == 'q': skipped_count = len(operations) - len(approved_ops); eprint("Quitting."); break
                else: skipped_count += 1; eprint(f"Skipping Delta #{op.index}.")
    except (KeyboardInterrupt, EOFError):
        eprint("\n\nOperation cancelled by user."); skipped_count = len(operations) - len(approved_ops)
    except OSError as e:
        eprint(f"\n{Colors.RED}Could not open controlling terminal: {e}{Colors.RESET}")
    clear_screen()
    if approved_ops: apply_operations(approved_ops)
    print_final_summary(len(approved_ops), skipped_count)

if __name__ == "__main__":
    main()

