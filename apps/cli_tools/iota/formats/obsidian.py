# --- Iota: Obsidian Format Provider ---
import re
from collections import namedtuple

# A simple data structure to hold information about a found link
FoundLink = namedtuple('FoundLink', ['full_match', 'link_target', 'display_text'])

class ObsidianFormatProvider:
    """
    Handles the logic for creating and parsing Obsidian-style wikilinks.
    """
    def create_link(self, link_target: str, display_text: str) -> str:
        """
        Creates an Obsidian-style wikilink.
        """
        if link_target == display_text:
            return f"[[{link_target}]]"
        else:
            return f"[[{link_target}|{display_text}]]"

    def strip_formatting(self, text: str) -> str:
        """
        Strips wikilinks and backticked code from a string.
        """
        # Strip wikilinks, keeping the display text or target
        def replacer(match):
            return match.group(2) if match.group(2) else match.group(1)
        text = re.sub(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', replacer, text)
        
        # Strip backticks
        text = re.sub(r'`([^`\n]+)`', r'\1', text)
        return text

    def find_links(self, text: str):
        """
        Finds all wikilinks in a string and yields FoundLink objects.
        """
        # This regex captures the link target and optional display text
        wikilink_pattern = re.compile(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]')
        
        for match in wikilink_pattern.finditer(text):
            full_match = match.group(0)
            link_target = match.group(1)
            # If display text isn't present, it defaults to the link target
            display_text = match.group(2) if match.group(2) else link_target
            
            yield FoundLink(full_match, link_target, display_text)