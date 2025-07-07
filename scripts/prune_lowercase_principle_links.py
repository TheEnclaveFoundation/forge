#!/usr/bin/env python3
import os
import re
import sys

# --- CONFIGURATION ---
MYCELIUM_PATH = './mycelium'
PRINCIPLES_DIR = os.path.join(MYCELIUM_PATH, 'Principles')
# --- END CONFIGURATION ---

def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def get_principles_list(principles_path):
    """Scans the Principles directory to get a list of concept names."""
    principles = []
    eprint("Building Principles list...")
    if not os.path.isdir(principles_path):
        eprint(f"Error: Principles directory not found at '{principles_path}'")
        sys.exit(1)
        
    for item in os.listdir(principles_path):
        if item.endswith('.md'):
            phrase = os.path.splitext(item)[0]
            principles.append(phrase)
    eprint(f"  > Found {len(principles)} Principles.")
    return principles

def main():
    """
    Finds and removes wikilinks from lowercase instances of Principles.
    """
    principles = get_principles_list(PRINCIPLES_DIR)
    if not principles:
        return

    # Build a regex to find links like [[Principles/Love|love]]
    # It specifically looks for a lowercase letter after the pipe.
    regex_pattern = r'\[\[(Principles/(' + '|'.join(re.escape(p) for p in principles) + r'))\|([a-z][^\]]*)\]\]'
    pattern = re.compile(regex_pattern)

    all_markdown_files = []
    for root, _, files in os.walk(MYCELIUM_PATH):
        for file in files:
            if file.endswith('.md'):
                all_markdown_files.append(os.path.join(root, file))

    eprint(f"Scanning {len(all_markdown_files)} markdown files for incorrect links...")
    changes_found = 0

    for filepath in all_markdown_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # The replacement function uses the 3rd capture group (the display text)
            new_content = pattern.sub(r'\3', original_content)

            if original_content != new_content:
                changes_found += 1
                relative_path = os.path.relpath(filepath, start='.')
                relative_path = './' + relative_path.replace('\\', '/')

                print("=== DELTA::START ===")
                print(f"PATH: {relative_path}")
                print("ACTION: REPLACE_FILE")
                print("=== DELTA::CONTENT ===")
                print(new_content)

        except Exception as e:
            eprint(f"Error processing file {filepath}: {e}")
            
    eprint(f"Scan complete. Found {changes_found} files needing correction.")

if __name__ == "__main__":
    main()