# forge/apps/cli-tools/iota/ui.py
import sys
from forge.packages.common.ui import eprint, Colors

def print_banner():
    """Prints the Iota tool's startup banner."""
    char = '┌'
    eprint(Colors.GREY + char + '─┄' + Colors.CYAN + 'Ι ' + Colors.RESET)
    eprint(Colors.GREY + '│' + Colors.RESET)

def print_header(text: str):
    """Prints a T-junction header for a report section."""
    eprint(Colors.GREY + '├─┄' + Colors.PURPLE + Colors.BOLD + text + Colors.RESET)

def print_line(text: str):
    """Prints a standard T-junction line for a report item."""
    eprint(Colors.GREY + '├─┄╴' + Colors.WHITE + text + Colors.RESET)

def print_end_line(text: str):
    """Prints the final line for a block, choosing the correct end character."""
    is_last = sys.stdout.isatty()
    char = '└' if is_last else '├'
    eprint(Colors.GREY + char + '─┄╴' + Colors.WHITE + text + Colors.RESET)
    if not is_last:
        # Add a final separator for the next tool in a pipe
        eprint(Colors.GREY + '│' + Colors.RESET)
