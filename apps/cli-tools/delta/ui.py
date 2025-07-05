# forge/apps/cli-tools/delta/ui.py
import sys
from forge.packages.common.ui import Colors, eprint

def print_banner():
    """Prints the Delta tool's startup banner in the new box style."""
    # This now always uses the top-left corner character.
    char = '┌'
    eprint(f"{Colors.GREY}{char}─┄{Colors.CYAN}∆{Colors.RESET}")
    print_separator()

def print_header(text: str):
    """Prints a T-junction header with a colon."""
    eprint(f"{Colors.GREY}├─┄{Colors.PURPLE}{Colors.BOLD}{text}:{Colors.RESET}")

def print_line(text: str, prefix: str = "├─┄╴"):
    """Prints a standard T-junction line."""
    eprint(f"{Colors.GREY}{prefix}{Colors.WHITE}{text}{Colors.RESET}")

def print_separator():
    """Prints a vertical bar separator."""
    eprint(f"{Colors.GREY}│{Colors.RESET}")

def print_review_header(op_index, total_ops, action, rel_path):
    """Prints the review header in the new box style."""
    print_header(f"Reviewing Delta {op_index} of {total_ops}")
    print_line(f"Action: {Colors.CYAN}{action}{Colors.RESET}")
    print_line(f"Path:   {Colors.PURPLE}{rel_path}{Colors.RESET}")
    print_separator()
    eprint(f"{Colors.GREY}├─┄╴{Colors.BOLD}Diff:{Colors.RESET}")

def print_final_summary(applied_count, skipped_count):
    """Prints the final summary report for Delta in the new box style."""
    # This now always uses the bottom-left corner character for the final line.
    end_char = '└'

    print_separator()
    print_header("Summary")

    summary_lines = []
    if applied_count > 0:
        summary_lines.append(f"Applied: {Colors.GREEN}{applied_count}{Colors.RESET}")
    if skipped_count > 0:
        summary_lines.append(f"Skipped: {Colors.YELLOW}{skipped_count}{Colors.RESET}")
    if not summary_lines:
        summary_lines.append(f"{Colors.YELLOW}No changes were applied or skipped.{Colors.RESET}")

    for i, line in enumerate(summary_lines):
        is_last_line = (i == len(summary_lines) - 1)
        prefix = f"{end_char}─┄╴" if is_last_line else "├─┄╴"
        print_line(line, prefix=prefix)