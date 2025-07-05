import sys
from forge.packages.common.ui import eprint, Colors

class BoxUI:
    """A class to render a tool's UI using box-drawing characters."""
    def __init__(self, title_char: str):
        self.is_first_in_pipe = sys.stdin.isatty()
        self.is_last_in_pipe = sys.stdout.isatty()
        self.title_char = title_char

    def start(self):
        """Prints the top-level banner for the tool."""
        char = '┌' if self.is_first_in_pipe else '├'
        eprint(f"{Colors.GREY}{char}─┄{Colors.CYAN}{self.title_char}{Colors.RESET}")
        self.separator()

    def separator(self):
        """Prints a vertical bar separator."""
        eprint(f"{Colors.GREY}│{Colors.RESET}")

    def header(self, text: str):
        """Prints a T-junction header."""
        eprint(f"{Colors.GREY}├─┄{Colors.PURPLE}{Colors.BOLD}{text}{Colors.RESET}")

    def line(self, text: str):
        """Prints a standard T-junction line."""
        eprint(f"{Colors.GREY}├─┄╴{Colors.WHITE}{text}{Colors.RESET}")

    def end_line(self, text: str):
        """Prints the final line for a block, choosing the correct end character."""
        char = '└' if self.is_last_in_pipe else '├'
        eprint(f"{Colors.GREY}{char}─┄╴{Colors.WHITE}{text}{Colors.RESET}")
