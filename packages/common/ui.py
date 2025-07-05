import os
import sys

class Colors:
    """
    A smart color class that uses a 256-color palette for consistency.
    It disables colors entirely if stderr is not a TTY.
    """
    IS_A_TTY = sys.stderr.isatty()
    _color = lambda code, is_tty=IS_A_TTY: f"\033[38;5;{code}m" if is_tty else ""
    RESET = "\033[0m" if IS_A_TTY else ""
    BOLD = "\033[1m" if IS_A_TTY else ""
    CYAN = _color(87)
    PURPLE = _color(171)
    GREEN = _color(47)
    RED = _color(196)
    YELLOW = _color(220)
    GREY = _color(242)

def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def clear_screen():
    """Clears the terminal screen if stderr is a TTY."""
    if sys.stderr.isatty():
        os.system('clear > /dev/tty')


