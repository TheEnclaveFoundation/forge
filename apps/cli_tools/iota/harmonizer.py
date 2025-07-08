# --- Iota: Harmonizer ---
import re
from typing import Dict, Set, List, Any

def harmonize_content(original_content: str, lexicon: Dict[str, str], principles: List[str], provider: Any) -> str:
    """
    Applies the "one concept, one primary link" rule to a string of document content,
    using the provided format provider.
    """
    had_trailing_newline = original_content.endswith('\n')
    # Use the provider to strip all existing formatting
    clean_content = provider.strip_formatting(original_content)
    lines = clean_content.splitlines()
    new_lines = []
    seen_in_file: Set[str] = set()

    all_concepts_sorted = sorted(lexicon.keys(), key=len, reverse=True)
    
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
        for match in master_pattern.finditer(line):
            term = match.group(1)
            
            is_principle = term.lower() in principle_terms_lower
            is_capitalized = term[0].isupper()

            if is_principle or is_capitalized:
                start, end = match.start(), match.end()
                
                is_substring = any(start >= r_start and end <= r_end for r_start, r_end, _ in replacements.values())
                if is_substring:
                    continue

                lookup_term = term.title() if is_principle else term
                link_target = lexicon.get(lookup_term)

                if link_target:
                    is_in_bold = False
                    for bold_match in re.finditer(r'\*\*(.*?)\*\*', line):
                        if match.start() > bold_match.start() and match.end() < bold_match.end():
                            is_in_bold = True
                            break
                    if is_in_bold:
                        continue
 
                    if link_target not in seen_in_file:
                        seen_in_file.add(link_target)
                        # Use the provider to create the link
                        replacement_text = provider.create_link(link_target, term)
                    else:
                         replacement_text = f'`{term}`'
                    
                    replacements[start] = (start, end, replacement_text)

        new_line = list(line)
        for start_index in sorted(replacements.keys(), reverse=True):
            start, end, text = replacements[start_index]
            new_line[start:end] = list(text)
        
        new_lines.append("".join(new_line))

    final_content = '\n'.join(new_lines)
    if had_trailing_newline and not final_content.endswith('\n'):
        final_content += '\n'
    
    return final_content
