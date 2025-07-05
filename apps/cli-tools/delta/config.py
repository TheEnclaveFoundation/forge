import os
import sys

# --- Aesthetics & Configuration ---

# The root directory for The Enclave Foundation projects.
# Can be overridden by the ENCLAVE_FOUNDATION_ROOT environment variable.
FOUNDATION_ROOT = os.environ.get(
    "ENCLAVE_FOUNDATION_ROOT",
    os.path.expanduser("~/softrecursion/TheEnclaveFoundation")
)

class Colors:
    """
    A smart color class that uses a 256-color palette for consistency.
    It disables colors entirely if stderr is not a TTY.
    """
    IS_A_TTY = sys.stderr.isatty()

    # Helper to generate 256-color codes.
    # A lambda with a default argument is used to capture the value of IS_A_TTY
    # at definition time, avoiding the NameError during class creation.
    _color = lambda code, is_tty=IS_A_TTY: f"\033[38;5;{code}m" if is_tty else ""

    RESET = "\033[0m" if IS_A_TTY else ""
    BOLD = "\033[1m" if IS_A_TTY else ""

    # --- Blueprint Theme (xterm 256-color codes) ---
    CYAN = _color(87)      # A vibrant cyan for actions
    PURPLE = _color(171)     # A distinct purple for paths/data
    GREEN = _color(47)       # A bright green for success
    RED = _color(196)        # A strong red for failure
    YELLOW = _color(220)     # A warm yellow for prompts/warnings
    GREY = _color(242)       # A subtle grey for de-emphasis