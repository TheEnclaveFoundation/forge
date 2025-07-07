# --- Iota: Harmonizer ---
# This module contains the logic for Component 2: Link Harmonization Engine.
# It uses a "clean slate" approach to enforce the "one concept, one primary link"
# standard, by first stripping all previous formatting and then re-applying it
# according to the rules.

import re
import os
from typing import Dict, Set, List

def _strip_formatting(content: str) -> str:
    """
    Strips all existing wikilinks and single backticks to create a "clean slate".
    """
    def wikilink_replacer(match):
        return match.group(2) if match.group(2) else match.group(1)
    content = re.sub(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', wikilink_replacer, content)
    content = re.sub(r'`([^`\n]+)`', r'\1', content)
    return content

def harmonize_content(original_content: str, lexicon: Dict[str, str], principles: List[str]) -> str:
    """
    Applies the "one concept, one primary link" rule to a string of document content.
    """
    had_trailing_newline = original_content.endswith('\n')
    clean_content = _strip_formatting(original_content)
    lines = clean_content.splitlines()
    new_lines = []
    seen_in_file: Set[str] = set()

    # Sort all lexicon keys by length, descending, to match longest phrases first.
    all_concepts_sorted = sorted(lexicon.keys(), key=len, reverse=True)
    
    # Create a single, powerful regex pattern from the sorted list of all concepts.
    # We will handle case-sensitivity in the replacement logic.
    master_pattern_str = r'\b(' + '|'.join(re.escape(k) for k in all_concepts_sorted) + r')\b'
    master_pattern = re.compile(master_pattern_str, re.IGNORECASE)
    
    principle_terms_lower = {p.lower() for p in principles}

    for line in lines:
        stripped_line = line.strip()
        # Protect headings, Type lines, and list items
        if stripped_line.startswith(('#', '**Type:**', '-', '*')):
            new_lines.append(line)
            continue
        
        replacements = {}
        
        # Find all possible matches on the line
        for match in master_pattern.finditer(line):
            term = match.group(1)
            
            is_principle = term.lower() in principle_terms_lower
            is_capitalized = term[0].isupper()

            # The rule: link if it's a Principle (any case) OR if it's another concept that is capitalized.
            if is_principle or is_capitalized:
                start, end = match.start(), match.end()
                
                is_substring = any(start >= r_start and end <= r_end for r_start, r_end, _ in replacements.values())
                if is_substring:
                    continue

                lookup_term = term.title() if is_principle else term
                link_target = lexicon.get(lookup_term)

                if link_target:
                    # Check if the match is inside a bolded section
                    # Find all bold sections on the line
                    is_in_bold = False
                    for bold_match in re.finditer(r'\*\*(.*?)\*\*', line):
                        if match.start() > bold_match.start() and match.end() < bold_match.end():
                            is_in_bold = True
                            break
                    if is_in_bold:
                        continue

                    if link_target not in seen_in_file:
                        seen_in_file.add(link_target)
                        replacement_text = f'[[{link_target}|{term}]]'
                    else:
                        replacement_text = f'`{term}`'
                    
                    replacements[start] = (start, end, replacement_text)

        # Apply replacements from last to first to not mess up indices
        new_line = list(line)
        for start_index in sorted(replacements.keys(), reverse=True):
            start, end, text = replacements[start_index]
            new_line[start:end] = list(text)
        
        new_lines.append("".join(new_line))

    # --- Reconstruction ---
    final_content = '\n'.join(new_lines)
    if had_trailing_newline and not final_content.endswith('\n'):
        final_content += '\n'
    
    return final_content