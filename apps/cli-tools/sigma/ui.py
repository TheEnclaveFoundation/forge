# forge/apps/cli-tools/sigma/ui.py
import sys
from forge.packages.common.ui import eprint, clear_screen, Colors

def print_banner():
    """Prints the Sigma tool's startup banner."""
    # Screen clearing removed for cohesive output
    char = '┌'
    eprint(Colors.GREY + char + '─┄' + Colors.CYAN + 'Σ ' + Colors.RESET)
    eprint(Colors.GREY + '│' + Colors.RESET)

def print_header(text: str):
    """Prints a T-junction header for a report section."""
    eprint(Colors.GREY + '├─┄' + Colors.PURPLE + Colors.BOLD + text + Colors.RESET)

def print_line(text: str):
    """Prints a standard T-junction line for a report item."""
    eprint(Colors.GREY + '├─┄╴' + Colors.WHITE + text + Colors.RESET)

def print_summary(repos_scraped_count: int, files_forged_count: int, is_piped: bool):
    """Prints the final summary report for Sigma."""
    char = '└' if not is_piped else '├'
    output_dest = "pipe" if is_piped else "terminal (suppressed)"

    eprint(Colors.GREY + '│' + Colors.RESET)
    print_header("Snapshot Summary:")
    print_line(f"Repos: {Colors.PURPLE}{repos_scraped_count}{Colors.RESET}")
    print_line(f"Files: {Colors.PURPLE}{files_forged_count}{Colors.RESET}")
    
    if not is_piped:
        print_line(f"Output Destination: {Colors.CYAN}{output_dest}{Colors.RESET}")
        eprint(Colors.GREY + '│' + Colors.RESET)
        print_header("Hint:")
        eprint(Colors.GREY + char + '─┄╴' + Colors.WHITE + f"To save output, redirect to a file: {Colors.GREY}$ sigma --all > snapshot.txt{Colors.RESET}")
    else: # pipe
        eprint(Colors.GREY + char + '─┄╴' + Colors.WHITE + f"Output Destination: {Colors.CYAN}{output_dest}{Colors.RESET}")
        # Add the final separator for the next tool in the pipe
        eprint(Colors.GREY + '│' + Colors.RESET)