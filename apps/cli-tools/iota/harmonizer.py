# --- Iota: Harmonizer ---
# This module contains the logic for Component 2: Link Harmonization Engine.
# It uses a "clean slate" approach to enforce the "one concept, one primary link"
# standard, by first stripping all previous formatting and then re-applying it
# according to the rules.

import re
from typing import Dict, Set

def _strip_formatting(content: str) -> str:
    """
    Strips all existing wikilinks and single backticks to create a "clean slate".
    """
    # First, strip wikilinks, preserving their display text.
    # This handles both [[Target]] and [[Target|Display Text]] formats.
    def wikilink_replacer(match):
        return match.group(2) if match.group(2) else match.group(1)
    content = re.sub(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', wikilink_replacer, content)

    # Then, strip any remaining single-backtick emphasis.
    content = re.sub(r'`([^`\n]+)`', r'\1', content)
    return content

def harmonize_content(original_content: str, lexicon: Dict[str, str]) -> str:
    """
    Applies the "one concept, one primary link" rule to a string of document content.
    This is the primary function that orchestrates the new, robust algorithm.

    Args:
        original_content: The raw text of the document.
        lexicon: A dictionary mapping search terms to their canonical link targets.

    Returns:
        The harmonized document content as a string.
    """
    # Step 1: Normalization ("Clean Slate")
    clean_content = _strip_formatting(original_content)

    lines = clean_content.splitlines()
    new_lines = []
    seen_in_file: Set[str] = set()

    # Prepare a case-sensitive regex for ONLY capitalized lexicon keys.
    # This is the user's directive to prevent linking common nouns (e.g., "path").
    capitalized_keys = [k for k in lexicon if k and k[0].isupper()]
    if not capitalized_keys:
        # If there are no capitalized terms in the lexicon, no changes are possible.
        return original_content

    # Sort keys by length, descending, to match longer phrases first.
    # e.g., "The Great Songs" before "The Great"
    sorted_keys = sorted(capitalized_keys, key=len, reverse=True)
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted_keys) + r')\b')

    # Steps 2 & 3: Protection and Harmonization (Line by Line)
    for line in lines:
        stripped_line = line.strip()
        # Protect headings and the 'Type:' line from any changes.
        if stripped_line.startswith('#') or stripped_line.startswith('Type:'):
            new_lines.append(line)
            continue

        # Use a replacer function to handle state (the 'seen_in_file' set).
        def replacer(match):
            term = match.group(1)
            link_target = lexicon.get(term) # Safe get, though key should exist

            if not link_target:
                return term # Should not happen with this regex, but as a safeguard

            if link_target not in seen_in_file:
                # First mention: Add to set and create a wikilink.
                seen_in_file.add(link_target)
                # Handle cases where display text might differ from target filename.
                if term.replace(' ', '-') == link_target:
                    return f'[[{link_target}]]'
                else:
                    return f'[[{link_target}|{term}]]'
            else:
                # Subsequent mention: Stylize with single backticks.
                return f'`{term}`'

        new_line = pattern.sub(replacer, line)
        new_lines.append(new_line)

    # Step 4: Reconstruction
    return '\n'.join(new_lines)