# --- Iota: Harmonizer ---
import re
import os
import json
from typing import Dict, Set, List, Any
from forge.packages.psi.client import get_oracle_response
from forge.packages.common.ui import eprint, Colors
from pydantic import BaseModel

# --- Pydantic model for Oracle validation ---
class OracleValidation(BaseModel):
    is_concept: bool

# --- Helper Functions ---
def _is_start_of_sentence(text: str, index: int) -> bool:
    """Checks if a match at a given index is at the start of a sentence."""
    if index == 0:
        return True
    # Look for a period, question mark, or exclamation mark followed by whitespace
    # in the characters immediately preceding the match.
    preceding_text = text[max(0, index - 2):index]
    if re.search(r'[\.?!]\s$', preceding_text):
        return True
    return False

def _get_paragraph(text: str, index: int) -> str:
    """Extracts the full paragraph surrounding a match index."""
    start = text.rfind('\n\n', 0, index) + 2
    end = text.find('\n\n', index)
    if end == -1:
        return text[start:]
    return text[start:end]

def _consult_oracle(paragraph: str, term: str, lexicon: List[str]) -> bool:
    """Calls the Psi Oracle to validate a term's usage."""
    eprint(f"{Colors.GREY}├─┄╴Consulting Oracle for ambiguous term: '{term}'...{Colors.RESET}")
    
    foundation_root = os.environ.get("ENCLAVE_FOUNDATION_ROOT", os.path.expanduser("~/softrecursion/TheEnclaveFoundation"))
    prompt_path = os.path.join(foundation_root, "forge", "prompts", "prompt-iota-oracle.txt")
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        eprint(f"{Colors.RED}  └─ Error: Oracle prompt file not found at {prompt_path}{Colors.RESET}")
        return False # Fail safely

    lexicon_str = json.dumps(lexicon)
    system_prompt = prompt_template.format(
        lexicon_list=lexicon_str,
        term_to_check=term,
        paragraph_to_check=paragraph
    )

    response = get_oracle_response(
        content=paragraph, # Content is part of the prompt, but psi client requires it
        system_prompt=system_prompt,
        model_name="gemini-1.5-pro", # Using a high-capability model for this reasoning task
        validation_model=OracleValidation
    )

    if response.get("error"):
        error_message = response.get('message', 'Unknown error.')
        error_details = response.get('details', 'No details provided.')
        eprint(f"{Colors.RED}  └─ Oracle Error: {error_message} (Details: {error_details}){Colors.RESET}")
        return False # Fail safely

    validation_result = response.get('validation_result')
    if validation_result and validation_result.get('is_concept'):
        eprint(f"{Colors.GREEN}  └─ Oracle Verdict: Is a Concept.{Colors.RESET}")
        return True
    
    eprint(f"{Colors.YELLOW}  └─ Oracle Verdict: Is a common noun.{Colors.RESET}")
    return False

# --- Main Harmonizer Logic ---
def harmonize_content(original_content: str, lexicon: Dict[str, str], provider: Any) -> str:
    """
    Applies the "one concept, one primary link" rule to a string of document content,
    using the provided format provider and consulting the Psi Oracle for ambiguous cases.
    """
    had_trailing_newline = original_content.endswith('\n')
    clean_content = provider.strip_formatting(original_content)
    lines = clean_content.splitlines()
    new_lines = []
    seen_in_file: Set[str] = set()

    all_concepts_sorted = sorted(lexicon.keys(), key=len, reverse=True)
    
    master_pattern_str = r'\b(' + '|'.join(re.escape(k) for k in all_concepts_sorted) + r')\b'
    master_pattern = re.compile(master_pattern_str)
    
    for line_num, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith(('#', '**Type:**', '-', '*')):
            new_lines.append(line)
            continue
        
        replacements = {}
        for match in master_pattern.finditer(line):
            term = match.group(1)
            start, end = match.start(), match.end()
            
            is_substring = any(start >= r_start and end <= r_end for r_start, r_end, _ in replacements.values())
            if is_substring:
                continue

            link_target = lexicon.get(term)
            if not link_target:
                continue

            # --- Heuristic Check ---
            full_text_for_context = "\n".join(lines)
            if _is_start_of_sentence(line, start):
                paragraph = _get_paragraph(full_text_for_context, full_text_for_context.find(line) + start)
                if not _consult_oracle(paragraph, term, list(lexicon.keys())):
                    continue # Oracle says it's a common noun, so we skip it.

            # --- Link Harmonization Logic ---
            is_in_bold = any(m.start() < start and m.end() > end for m in re.finditer(r'\*\*(.*?)\*\*', line))
            if is_in_bold:
                continue

            if link_target not in seen_in_file:
                seen_in_file.add(link_target)
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
