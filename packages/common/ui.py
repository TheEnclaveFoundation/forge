# --- The Loom: A Data-Driven UI Renderer ---
import sys
import shutil
import textwrap
from typing import List, Dict, Any

# --- Color Management ---
class _ColorManager:
    """A dynamic class that generates ANSI color codes."""
    def __init__(self):
        self._color_map = {
            'PURPLE': "\033[95m", 'CYAN': "\033[96m", 'GREEN': "\033[92m",
            'RED': "\033[91m", 'YELLOW': "\033[93m", 'WHITE': "\033[97m",
            'GREY': "\033[1;30m"
        }
    def __getattr__(self, name: str) -> str:
        is_a_tty = sys.stderr.isatty()
        if not is_a_tty:
            return ""
        if name == 'RESET': return "\033[0m"
        if name == 'BOLD': return "\033[1m"
        if name in self._color_map: return self._color_map[name]
        raise AttributeError(f"'Colors' object has no attribute '{name}'")

Colors = _ColorManager()

def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)

# --- Renderer Core Logic ---

def _get_terminal_width() -> int:
    """Gets the current terminal width, with a sensible default."""
    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return 80 # Default width

def _draw_banner(block: Dict[str, Any]):
    symbol = block.get('symbol', '!')
    color = getattr(Colors, block.get('color', 'WHITE').upper(), Colors.WHITE)
    eprint(f"{Colors.GREY}┌─┄{color}{symbol} {Colors.RESET}")
    eprint(f"{Colors.GREY}│{Colors.RESET}")

def _draw_group(block: Dict[str, Any], width: int):
    title = block.get('title', 'Group')
    items = block.get('items', [])
    eprint(f"{Colors.GREY}├─┄{Colors.PURPLE}{Colors.BOLD}{title}{Colors.RESET}")

    # Calculate wrapping width for values
    # Prefix is "├─┄╴Key: "
    max_key_len = max(len(item.get('key', '')) for item in items) if items else 0
    prefix_len = 4 + max_key_len + 2 # "├─┄╴" + key + ": "
    wrap_width = width - prefix_len
    
    for item in items:
        key = item.get('key', '')
        value = str(item.get('value', ''))
        key_str = f"{key}:".ljust(max_key_len + 1)
        
        wrapped_lines = textwrap.wrap(value, width=wrap_width, subsequent_indent='  ')
        
        if not wrapped_lines: # Handle empty values
            eprint(f"{Colors.GREY}├─┄╴{Colors.WHITE}{key_str}{Colors.RESET}")
            continue

        # Print first line
        eprint(f"{Colors.GREY}├─┄╴{Colors.WHITE}{key_str} {Colors.CYAN}{wrapped_lines[0]}{Colors.RESET}")
        # Print subsequent wrapped lines
        for line in wrapped_lines[1:]:
            eprint(f"{Colors.GREY}│  {' ' * (max_key_len + 1)} {Colors.CYAN}{line}{Colors.RESET}")

def _draw_prose(block: Dict[str, Any], width: int):
    title = block.get('title', 'Content')
    text = block.get('text', '')
    eprint(f"{Colors.GREY}├─┄{Colors.PURPLE}{Colors.BOLD}{title}{Colors.RESET}")
    
    # Wrap text with indentation
    prefix = "│  "
    wrap_width = width - len(prefix)
    wrapped_lines = textwrap.wrap(text, width=wrap_width)
    
    for line in wrapped_lines:
        eprint(f"{Colors.GREY}{prefix}{Colors.WHITE}{line}{Colors.RESET}")

def _draw_end(block: Dict[str, Any]):
    text = block.get('text', 'Done.')
    color = getattr(Colors, block.get('color', 'WHITE').upper(), Colors.WHITE)
    eprint(f"{Colors.GREY}└─┄╴{color}{text}{Colors.RESET}")

# --- Public Render Function ---

def render(plan: List[Dict[str, Any]]):
    """
    Parses a render plan and draws the UI to stderr.
    """
    if not sys.stderr.isatty():
        return # Don't render UI if not in an interactive terminal

    width = _get_terminal_width()
    
    # A map from block 'type' to the function that draws it
    DRAW_MAP = {
        'banner': lambda block: _draw_banner(block),
        'group': lambda block: _draw_group(block, width),
        'prose': lambda block: _draw_prose(block, width),
        'end': lambda block: _draw_end(block)
    }

    for block in plan:
        draw_func = DRAW_MAP.get(block.get('type'))
        if draw_func:
            try:
                draw_func(block)
            except Exception as e:
                # Fail gracefully if a single block fails to render
                eprint(f"{Colors.RED}Error rendering UI block: {block}{Colors.RESET}")
                eprint(f"{Colors.RED}Details: {e}{Colors.RESET}")