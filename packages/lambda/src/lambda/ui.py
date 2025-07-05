# forge/packages/lambda/src/lambda/ui.py
import sys
from forge.packages.common.ui import eprint, clear_screen, Colors

def print_banner():
    """Prints the Lambda tool's startup banner."""
    # Screen clearing removed for cohesive output
    char = '┌' if sys.stdin.isatty() else '├'
    eprint(Colors.GREY + char + '─┄' + Colors.CYAN + 'Λ ' + Colors.RESET)
    eprint(Colors.GREY + '│' + Colors.RESET)

def print_header(text: str):
    """Prints a T-junction header for a report section."""
    eprint(Colors.GREY + '├─┄' + Colors.PURPLE + Colors.BOLD + text + Colors.RESET)

def print_line(text: str):
    """Prints a standard T-junction line for a report item."""
    eprint(Colors.GREY + '├─┄╴' + Colors.WHITE + text + Colors.RESET)

def print_separator():
    """Prints a vertical bar separator."""
    eprint(Colors.GREY + '│' + Colors.RESET)

def print_end_line(text: str):
    """Prints the final line for a block, choosing the correct end character."""
    is_last = sys.stdout.isatty()
    char = '└' if is_last else '├'
    eprint(Colors.GREY + char + '─┄╴' + Colors.WHITE + text + Colors.RESET)

def print_summary(violations_count: int):
    """Prints a final summary of the linter run."""
    is_last = sys.stdout.isatty()
    char = '└' if is_last else '├'
    print_separator()
    print_header("Done.")
    if violations_count > 0:
        print_end_line(f"Violations Found: {Colors.RED}{violations_count}{Colors.RESET}")
    else:
        print_end_line(f"Status: {Colors.GREEN}No violations found.{Colors.RESET}")