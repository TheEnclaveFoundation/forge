# --- Iota: Indexer ---
# This module contains the logic for Component 1: Dynamic Lexicon Indexer.
# It scans repository filenames to build an index of linkable concepts
# and their full relative paths for correct wikilinking.
import os
from typing import Dict, List

def _generate_terms_from_filename(filepath: str, repo_base_path: str) -> Dict[str, str]:
    """
    Generates potential search terms from a given filename and maps them
    to a clean, relative path for wikilinking.

    Example:
    filepath: /path/to/mycelium/World/Entities/Echo.md
    repo_base_path: /path/to/mycelium
    -> returns: {'Echo': 'World/Entities/Echo'}
    """
    # Get the filename without the directory path
    basename = os.path.basename(filepath)
    # Get the filename without the extension, which is our display text
    display_text, _ = os.path.splitext(basename)

    # Calculate the link path relative to the repo root
    # e.g., /path/to/mycelium/World/Entities/Echo.md -> World/Entities/Echo.md
    relative_path_with_ext = os.path.relpath(filepath, repo_base_path)
    # -> World/Entities/Echo
    link_target, _ = os.path.splitext(relative_path_with_ext)
    # Ensure forward slashes for consistency
    link_target = link_target.replace('\\', '/')

    terms = {}
    # The primary term is the clean name, e.g., "Echo"
    terms[display_text] = link_target
    # Also allow for the version with hyphens if needed, e.g., "Prime-Resonance"
    if '-' in display_text:
        terms[display_text.replace('-', ' ')] = link_target

    return terms

def build_lexicon_index(repo_paths: List[str]) -> Dict[str, str]:
    """
    Walks the directory trees of the given repositories and builds a comprehensive
    index of all linkable terms, mapping them to their correct relative paths.
    """
    lexicon_index = {}
    for repo_path in repo_paths:
        if not os.path.isdir(repo_path):
            continue

        for root, _, files in os.walk(repo_path):
            # We are only interested in markdown files for linking
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    # We pass the repo_path itself to correctly calculate the relative link
                    new_terms = _generate_terms_from_filename(filepath, repo_path)
                    lexicon_index.update(new_terms)

    return lexicon_index