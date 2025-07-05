# forge/apps/cli-tools/delta/__main__.py
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
from forge.packages.common.ui import eprint, Colors
from .ui import print_banner, print_review_header, print_final_summary, print_separator, print_line, print_header

def run_dry_run(operations: list):
    """Executes a dry run, showing diffs without applying changes."""
    for op in operations:
        print_separator()
        print_review_header(op.index, len(operations), op.action, os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else 'N/A')
        for line in generate_diff_text(op):
            color = Colors.GREEN if line.startswith('+') else Colors.RED if line.startswith('-') else Colors.CYAN if line.startswith('@@') else Colors.GREY
            eprint(f"{Colors.GREY}│{Colors.RESET} {color}{line.strip()}{Colors.RESET}")
        
        if op.index < len(operations):
            print_separator()
            input(f"{Colors.GREY}├─┄╴{Colors.YELLOW}Press Enter to view next Delta...{Colors.RESET}")
    
    print_separator()
    print_header("Dry Run Complete")
    print_line(f"{Colors.PURPLE}No changes were made to the filesystem.{Colors.RESET}", prefix="└─┄╴")


def main():
    parser = argparse.ArgumentParser(description="The Delta tool applies structured changes to the filesystem.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--dry-run', action='store_true', help="Validate and show all diffs without applying changes.")
    parser.add_argument('--strict', action='store_true', help="Parser warnings and ambiguous blocks become fatal errors.")
    args = parser.parse_args()

    # Print the one and only banner for the program's execution
    print_banner()

    manifest_text = sys.stdin.read()
    if not manifest_text.strip():
        print_header("Error")
        print_line(f"{Colors.YELLOW}No input received. Exiting.{Colors.RESET}", prefix="└─┄╴")
        return
        
    try:
        operations = parse_manifest(manifest_text, strict_mode=args.strict)
    except ValueError as e:
        print_header("Error")
        print_line(f"{Colors.RED}Error parsing manifest: {e}{Colors.RESET}", prefix="└─┄╴")
        sys.exit(1)

    if not operations:
        print_header("Info")
        print_line(f"{Colors.YELLOW}No valid Delta operations found.{Colors.RESET}", prefix="└─┄╴")
        return
    
    validation_errors = validate_all_operations(operations, strict_mode=args.strict)
    if validation_errors:
        print_separator()
        print_line(f"{Colors.RED}{Colors.BOLD}Validation failed. Aborting.{Colors.RESET}", prefix="└─┄╴")
        if not sys.stdout.isatty(): print(json.dumps(validation_errors, indent=2))
        sys.exit(1)
    
    if args.dry_run:
        run_dry_run(operations); return

    approved_ops, apply_all, skipped_count = [], False, 0
    try:
        with open('/dev/tty') as tty:
            for op in operations:
                print_separator()
                print_review_header(op.index, len(operations), op.action, os.path.relpath(op.path, FOUNDATION_ROOT) if op.path else 'N/A')
                
                for line in generate_diff_text(op):
                    color = Colors.GREEN if line.startswith('+') else Colors.RED if line.startswith('-') else Colors.CYAN if line.startswith('@@') else Colors.GREY
                    eprint(f"{Colors.GREY}│{Colors.RESET} {color}{line.strip()}{Colors.RESET}")
                
                print_separator()

                if apply_all:
                    print_line(f"{Colors.GREEN}Applying automatically...{Colors.RESET}")
                    approved_ops.append(op)
                    continue

                sys.stderr.write(f"{Colors.GREY}├─┄╴{Colors.YELLOW}Apply this change? [y/n/a/q] {Colors.RESET} ")
                sys.stderr.flush()
                confirm = tty.readline().strip().lower()
                
                if confirm == 'y': approved_ops.append(op)
                elif confirm == 'a': apply_all = True; approved_ops.append(op)
                elif confirm == 'q': skipped_count = len(operations) - len(approved_ops); break
                else: skipped_count += 1
    except (KeyboardInterrupt, EOFError):
        eprint("\n\nOperation cancelled by user.")
        skipped_count = len(operations) - len(approved_ops)
    except OSError as e:
        print_header("Error")
        print_line(f"{Colors.RED}Could not open controlling terminal: {e}{Colors.RESET}", prefix="└─┄╴")

    if approved_ops:
        print_separator()
        apply_operations(approved_ops)
    
    print_final_summary(len(approved_ops), skipped_count)


if __name__ == "__main__":
    main()