import os
import sys

from .config import Colors

def eprint(*args, **kwargs):
    """Prints to stderr, respecting TTY color settings."""
    print(*args, file=sys.stderr, **kwargs)

def clear_screen():
    """Clears the terminal screen if stderr is a TTY."""
    if sys.stderr.isatty():
        os.system('clear > /dev/tty')

def print_banner():
    """Prints the new minimal delta banner."""
    clear_screen()
    eprint(f"\n{Colors.CYAN}--- ∆ ---{Colors.RESET}\n")

def print_review_header(op_index, total_ops, action, rel_path):
    """Prints the new vertical review header."""
    eprint(f"{Colors.CYAN}{Colors.BOLD}[∆] Delta {op_index} of {total_ops}{Colors.RESET}")
    eprint(f"{Colors.GREY}──────────────────────────────────{Colors.RESET}")
    eprint(f"{Colors.GREY}  ACTION   {Colors.CYAN}{action}{Colors.RESET}")
    eprint(f"{Colors.GREY}    PATH   {Colors.PURPLE}{rel_path}{Colors.RESET}")
    eprint(f"{Colors.GREY}──────────────────────────────────{Colors.RESET}")

def print_final_summary(applied_count, skipped_count):
    """Prints the new minimal final summary."""
    eprint(f"\n{Colors.GREEN}{Colors.BOLD}✨ Done.{Colors.RESET}")
    if applied_count > 0:
        eprint(f"  {Colors.GREY}- Applied: {Colors.GREEN}{applied_count}{Colors.RESET}")
    if skipped_count > 0:
        eprint(f"  {Colors.GREY}- Skipped: {Colors.YELLOW}{skipped_count}{Colors.RESET}")
    if applied_count == 0 and skipped_count == 0:
        eprint(f"  {Colors.YELLOW}No changes were approved or applied.{Colors.RESET}")


