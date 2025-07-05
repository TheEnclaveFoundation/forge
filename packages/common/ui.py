import os
import sys

class _ColorManager:
    """
    A dynamic class that generates color codes on attribute access.
    This version uses basic, high-compatibility ANSI color codes.
    """
    def __init__(self):
        self._color_map = {
            'PURPLE': "\033[95m", # Bright Magenta
            'CYAN':   "\033[96m", # Bright Cyan
            'GREEN':  "\033[92m", # Bright Green
            'RED':    "\033[91m", # Bright Red
            'YELLOW': "\033[93m", # Bright Yellow
            'WHITE':  "\033[97m", # Bright White
            'GREY':   "\033[1;30m" # Bold Black (looks like grey on dark backgrounds)
        }

    def __getattr__(self, name: str) -> str:
        force_color = os.environ.get("FORGE_FORCE_COLOR") == "1"
        is_a_tty = sys.stderr.isatty() or force_color

        if not is_a_tty:
            return ""

        if name == 'RESET':
            return "\033[0m"
        if name == 'BOLD':
            return "\033[1m"
        
        if name in self._color_map:
            return self._color_map[name]
        
        raise AttributeError(f"'Colors' object has no attribute '{name}'")

Colors = _ColorManager()

def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def clear_screen():
    """Clears the terminal screen if stderr is a TTY."""
    if sys.stderr.isatty():
        os.system('clear > /dev/tty')