# --- Iota: Indexer ---
# This module contains the logic for Component 1: Dynamic Lexicon Indexer.
# It scans repository filenames to build an index of linkable concepts
# and their plain-text variations.
import os
from typing import Dict, List

def _generate_terms_from_filename(filepath: str) -> Dict[str, str]:
    """
    Generates potential search terms from a given filename.

    Example: 'Enclave-Genome.md' -> {'Enclave-Genome': 'Enclave-Genome', 'Enclave Genome': 'Enclave-Genome'}
    """
    # Get the filename without the directory path
    basename = os.path.basename(filepath)
    # Get the filename without the extension, which is our canonical link target
    link_target, _ = os.path.splitext(basename)

    terms = {}

    # 1. The raw filename (kebab-case) is a term
    terms[link_target] = link_target

    # 2. The prose-style name (space-separated) is a term
    prose_name = link_target.replace('-', ' ')
    terms[prose_name] = link_target

    return terms

def build_lexicon_index(repo_paths: List[str]) -> Dict[str, str]:
    """
    Walks the directory trees of the given repositories and builds a comprehensive
    index of all linkable terms.
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
                    new_terms = _generate_terms_from_filename(filepath)
                    lexicon_index.update(new_terms)

    return lexicon_index
