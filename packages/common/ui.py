# --- The Loom: A Data-Driven UI Renderer ---
import sys
import shutil
import textwrap
import os
import yaml
from typing import List, Dict, Any

# --- Theme and Color Management ---

ANSI_CODES = {
    'PURPLE': "\033[95m",
    'CYAN':   "\033[96m",
    'GREEN':  "\033[92m",
    'RED':    "\033[91m",
    'YELLOW': "\033[93m",
    'WHITE':  "\033[97m",
    'GREY':   "\033[1;30m",
    'RESET':  "\033[0m",
    'BOLD':   "\033[1m"
}

# This class is for backward compatibility for modules that need direct color access.
class _ColorProxy:
    def __getattr__(self, name: str) -> str:
        if not sys.stderr.isatty(): return ""
        return ANSI_CODES.get(name.upper(), "")

Colors = _ColorProxy()

def _load_theme() -> Dict[str, Any]:
    """Loads the ui_theme.yaml file."""
    try:
        theme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'ui_theme.yaml')
        with open(theme_path, 'r') as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError):
        return {
            "characters": { 'vertical': '|', 't_junction': '|--', 'corner': '`--', 'ruler': '--', 'arrow': '>', 'top_corner': '|--' },
            "styles": { 'group': {'title_color': 'RED'}, 'prose': {'title_color': 'RED'}, 'end': {'default_color': 'RED'} }
        }

THEME = _load_theme()

def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def _get_color(name: str) -> str:
    """Gets an ANSI code from the internal map."""
    if not sys.stderr.isatty(): return ""
    return ANSI_CODES.get(name.upper(), "")

# --- Renderer Core Logic ---

def _get_terminal_width() -> int:
    """Gets the current terminal width, with a sensible default."""
    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return 80

def _draw_banner(block: Dict[str, Any]):
    char_map = THEME.get("characters", {})
    style = THEME.get("styles", {}).get("banner", {})
    
    symbol = block.get('symbol', '!')
    color_name = block.get('color', style.get("symbol_color", "CYAN"))
    
    # Corrected to use 'top_corner' instead of 't_junction'
    eprint(f"{_get_color('grey')}{char_map.get('top_corner')}{char_map.get('ruler')}{_get_color(color_name)}{symbol} {_get_color('reset')}")
    eprint(f"{_get_color('grey')}{char_map.get('vertical')}{_get_color('reset')}")

def _draw_group(block: Dict[str, Any], width: int):
    char_map = THEME.get("characters", {})
    style = THEME.get("styles", {}).get("group", {})
    title = block.get('title', 'Group')
    items = block.get('items', [])
    title_str = f"{_get_color(style.get('title_color', 'PURPLE'))}{_get_color('bold')}{title}{_get_color('reset')}"
    eprint(f"{_get_color('grey')}{char_map.get('t_junction')}{char_map.get('ruler')}{title_str}")
    if not items: return
    for item in items:
        key = item.get('key', '')
        value = str(item.get('value', ''))
        eprint(f"{_get_color('grey')}{char_map.get('t_junction')}{char_map.get('arrow')}{_get_color(style.get('key_color', 'WHITE'))}{key}:{_get_color('reset')}")
        prefix = f"{_get_color('grey')}{char_map.get('vertical')}    {_get_color('reset')}"
        wrap_width = width - 5
        wrapped_lines = textwrap.wrap(value, width=wrap_width)
        if not wrapped_lines:
            eprint(f"{_get_color('grey')}{char_map.get('vertical')}{_get_color('reset')}")
            continue
        for line in wrapped_lines:
            eprint(f"{prefix}{_get_color(style.get('value_color', 'CYAN'))}{line}{_get_color('reset')}")

def _draw_prose(block: Dict[str, Any], width: int):
    char_map = THEME.get("characters", {})
    style = THEME.get("styles", {}).get("prose", {})
    title = block.get('title', 'Content')
    title_str = f"{_get_color(style.get('title_color', 'PURPLE'))}{_get_color('bold')}{title}{_get_color('reset')}"
    eprint(f"{_get_color('grey')}{char_map.get('t_junction')}{char_map.get('ruler')}{title_str}")
    
    prefix = f"{_get_color('grey')}{char_map.get('vertical')}  {_get_color('reset')}"
    wrap_width = width - 3
    
    # NEW: Handle structured, colored lines for diffs
    if 'lines' in block:
        for line_obj in block.get('lines', []):
            content = line_obj.get('content', '').rstrip('\n')
            color_name = line_obj.get('color', style.get('text_color', 'WHITE'))
            eprint(f"{prefix}{_get_color(color_name)}{content}{_get_color('reset')}")
    # FALLBACK: Handle plain text for backward compatibility
    else:
        text = block.get('text', '')
        wrapped_lines = textwrap.wrap(text, width=wrap_width)
        for line in wrapped_lines:
            eprint(f"{prefix}{_get_color(style.get('text_color', 'WHITE'))}{line}{_get_color('reset')}")

def _draw_end(block: Dict[str, Any]):
    char_map = THEME.get("characters", {})
    style = THEME.get("styles", {}).get("end", {})
    text = block.get('text', 'Done.')
    color_name = block.get('color', style.get("default_color", "GREEN"))
    eprint(f"{_get_color('grey')}{char_map.get('corner')}{char_map.get('ruler')}{_get_color(color_name)}{text}{_get_color('reset')}")

def render(plan: List[Dict[str, Any]]):
    """
    Parses a render plan and draws the UI to stderr using the configured theme.
    """
    if not sys.stderr.isatty(): return
    width = _get_terminal_width()
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
                eprint(f"{_get_color('red')}Error rendering UI block: {block}{_get_color('reset')}")
                eprint(f"{_get_color('red')}Details: {e}{_get_color('reset')}")
