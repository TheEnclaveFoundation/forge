# --- FILE: foundry/apps/cli-tools/delta_forge/delta_forge.py ---
#!/usr/bin/env python3
#
# The Delta Forge (v13.0 - The Journeyman's Edition)
#
# This version incorporates major feature enhancements based on a critical review,
# focusing on safety, capability, and user experience.
#
# Changelog:
# v13.0
# - Implemented `--dry-run` mode to preview all changes without applying them.
# - Implemented `--strict` mode to treat parser warnings as fatal errors.
# - Added new actions:
#   - APPEND_TO_FILE
#   - PREPEND_TO_FILE
#   - INSERT_AFTER_BLOCK
#   - INSERT_BEFORE_BLOCK
#   - CREATE_DIRECTORY
# - Added validation to warn when a REPLACE_BLOCK target is ambiguous (found multiple times).
#   In --strict mode, this is a fatal error.
#

import sys
import json
import argparse

# Import modular components
from .config import Colors, UI_WIDTH, FOUNDATION_ROOT
from .parser import parse_manifest
from .validation import validate_all_operations
from .filesystem import apply_operations
from .diff import generate_diff_text
from .ui import eprint, clear_screen, print_banner

def run_dry_run(operations: list):
    """Executes a dry run, printing diffs for all operations without applying."""
    eprint(f"\n{Colors.PURPLE}{Colors.BOLD}Executing dry run... No changes will be made.{Colors.RESET}")
    for op in operations:
        eprint(f"\n{Colors.CYAN}{'═' * UI_WIDTH}{Colors.RESET}")
        review_title = f"Dry Run: Delta #{op.index} of {len(operations)}"
        eprint(f"{Colors.BOLD}{review_title}{Colors.RESET}")
        rel_path = op.path.replace(FOUNDATION_ROOT, '.') if op.path else "N/A"
        eprint(f"{Colors.GREY}{op.action} on {rel_path}{Colors.RESET}")
        eprint(f"{Colors.CYAN}{'-' * UI_WIDTH}{Colors.RESET}")
        
        diff_text = generate_diff_text(op)
        if not diff_text:
            eprint(f"{Colors.GREY}(No changes to display for this operation){Colors.RESET}")
        else:
            for line in diff_text:
                color = Colors.GREEN if line.startswith('+') else Colors.RED if line.startswith('-') else Colors.CYAN if line.startswith('@@') else Colors.GREY
                eprint(f"{color}{line.strip()}{Colors.RESET}")
    eprint(f"\n{Colors.PURPLE}{Colors.BOLD}Dry run complete.{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="The Delta Forge: Apply structured changes to the filesystem.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Perform a dry run. Validates the manifest and shows all diffs without applying changes."
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Enable strict mode. Parser warnings (e.g., unclassified lines) become fatal errors."
    )
    args = parser.parse_args()

    print_banner()

    manifest_text = sys.stdin.read()
    if not manifest_text.strip():
        eprint(f"\n{Colors.YELLOW}No input received from pipe. Exiting.{Colors.RESET}")
        return
    
    try:
        operations = parse_manifest(manifest_text, strict_mode=args.strict)
    except ValueError as e:
        eprint(f"\n{Colors.RED}{Colors.BOLD}Error parsing manifest in strict mode: {e}{Colors.RESET}")
        sys.exit(1)

    if not operations:
        eprint(f"\n{Colors.YELLOW}No valid Delta operations found in the manifest. Exiting.{Colors.RESET}")
        return

    validation_errors = validate_all_operations(operations, strict_mode=args.strict)

    if validation_errors:
        eprint(f"\n{Colors.RED}{Colors.BOLD}Validation failed. Aborting operation.{Colors.RESET}")
        if not sys.stdout.isatty():
            print(json.dumps(validation_errors, indent=2))
        else:
            eprint(f"\n{Colors.YELLOW}Recommended Action:{Colors.RESET}")
            eprint(f"{Colors.GREY}  To capture this error report, rerun the command and redirect stdout.{Colors.RESET}")
            eprint(f"{Colors.CYAN}  Example: {Colors.BOLD}xclip -o | delta > error_report.json{Colors.RESET}")
        sys.exit(1)

    if args.dry_run:
        run_dry_run(operations)
        return

    # --- Interactive Application ---
    approved_ops, apply_all = [], False
    try:
        with open('/dev/tty') as tty:
            for op in operations:
                clear_screen()
                review_title = f"Reviewing Delta #{op.index} of {len(operations)}"
                eprint(f"{Colors.BOLD}{review_title}{Colors.RESET}")
                rel_path = op.path.replace(FOUNDATION_ROOT, '.') if op.path else 'N/A'
                eprint(f"{Colors.GREY}{op.action} on {rel_path}{Colors.RESET}")
                eprint(f"{Colors.CYAN}{'═' * UI_WIDTH}{Colors.RESET}")

                for line in generate_diff_text(op):
                    color = Colors.GREEN if line.startswith('+') else Colors.RED if line.startswith('-') else Colors.CYAN if line.startswith('@@') else Colors.GREY
                    eprint(f"{color}{line.strip()}{Colors.RESET}")
                
                eprint(f"{Colors.CYAN}{'═' * UI_WIDTH}{Colors.RESET}")
                
                if apply_all:
                    eprint(f"{Colors.GREEN}Applying automatically...{Colors.RESET}")
                    approved_ops.append(op)
                    continue
                
                sys.stderr.write(f"{Colors.YELLOW}Apply this change? [y/n/a/q] (yes/no/all/quit) {Colors.RESET} ")
                sys.stderr.flush()
                confirm = tty.readline().strip().lower()
                
                if confirm == 'y': approved_ops.append(op)
                elif confirm == 'a': apply_all = True; approved_ops.append(op)
                elif confirm == 'q': eprint("Quitting review process."); break
                else: eprint(f"Skipping Delta #{op.index}.")
    except (KeyboardInterrupt, EOFError):
        eprint("\n\nOperation cancelled by user.")
    except OSError as e:
        eprint(f"\n{Colors.RED}Could not open controlling terminal. Cannot run interactively: {e}{Colors.RESET}")

    clear_screen()
    if approved_ops:
        apply_operations(approved_ops)
        eprint(f"\n{Colors.BOLD}{Colors.GREEN}✅ Delta Forge complete. {len(approved_ops)} changes applied.{Colors.RESET}")
    else:
        eprint(f"\n{Colors.YELLOW}No changes were approved or applied. Exiting.{Colors.RESET}")

if __name__ == "__main__":
    main()
