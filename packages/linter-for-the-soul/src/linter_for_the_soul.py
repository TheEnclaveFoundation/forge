#!/usr/bin/env python3
import sys
import os
import re
import json
import argparse
import yaml

# --- Linter for the Soul v1.2 ---
# - Fixed `contains_text` check to use whole-word matching instead of substring matching.

def parse_codex_snapshot(snapshot_content: str) -> dict:
    """Parses the full codex snapshot into a dictionary of file paths and content."""
    print("  - Parsing codex snapshot...")
    file_pattern = re.compile(r'^--- FILE: (.*) ---$', re.MULTILINE)
    parts = file_pattern.split(snapshot_content)[1:]
    if not parts:
        raise ValueError("Snapshot appears to be empty or malformed. No '--- FILE: ...' markers found.")
    codex_files = {parts[i]: parts[i+1].strip() for i in range(0, len(parts), 2)}
    print(f"    ✅ Found {len(codex_files)} files in the snapshot.")
    return codex_files

def load_yaml_config(filepath: str) -> dict:
    """Loads a YAML file and returns its content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# --- CHECK FUNCTIONS ---

def check_contains_text(file_path: str, file_content: str, rule: dict) -> dict or None:
    """Checks if a file contains any forbidden words from a list using whole-word matching."""
    params = rule['check']['params']
    words_to_check = params.get('words', [])
    
    # NOTE: This check is now case-insensitive by default for robustness.
    flags = re.IGNORECASE
    
    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        for word in words_to_check:
            # \b is a word boundary. This prevents matching 'form' in 'information'.
            if re.search(r'\b' + re.escape(word) + r'\b', line, flags):
                return {
                    "file_path": file_path,
                    "line_number": i + 1,
                    "rule_name": rule['name'],
                    "severity": rule['severity'],
                    "error_type": "contains_text",
                    "details": { "forbidden_word": word, "full_line_content": line.strip() }
                }
    return None

def check_lacks_link_on_entity_interaction(file_path: str, file_content: str, rule: dict, sovereign_entities: list) -> dict or None:
    """Checks for required links when multiple sovereign entities are mentioned."""
    params = rule['check']['params']
    min_entities = params.get('min_entities', 2)
    required_link = params.get('required_link', '')

    found_entities = set()
    for entity in sovereign_entities:
        if re.search(r'\b' + re.escape(entity) + r'\b', file_content, re.IGNORECASE):
            found_entities.add(entity)

    if len(found_entities) >= min_entities:
        if required_link not in file_content:
            return {
                "file_path": file_path,
                "rule_name": rule['name'],
                "severity": rule['severity'],
                "error_type": "lacks_link",
                "details": { "required_link": required_link, "context": f"Interaction involves {sorted(list(found_entities))}" }
            }
    return None

def check_must_start_with(file_path: str, file_content: str, rule: dict) -> dict or None:
    """Checks if a file's content starts with a specific string."""
    params = rule['check']['params']
    prefix = params.get('prefix', '')
    
    if not file_content.lstrip().startswith(prefix):
        return {
            "file_path": file_path,
            "rule_name": rule['name'],
            "severity": rule['severity'],
            "error_type": "must_start_with",
            "details": { "required_prefix": prefix }
        }
    return None

# --- DISPATCHER & MAIN (Unchanged) ---
def run_check(file_path: str, file_content: str, rule: dict, sovereign_entities: list) -> dict or None:
    check_type = rule.get('check', {}).get('type')
    scope = rule.get('check', {}).get('scope', {})
    if 'directory' in scope and not file_path.strip('./').startswith(scope['directory']):
        return None
    if check_type == "contains_text":
        return check_contains_text(file_path, file_content, rule)
    elif check_type == "lacks_link_on_entity_interaction":
        return check_lacks_link_on_entity_interaction(file_path, file_content, rule, sovereign_entities)
    elif check_type == "must_start_with":
        return check_must_start_with(file_path, file_content, rule)
    else:
        print(f"  [Warning] Unknown check type '{check_type}' in rule '{rule['name']}'. Skipping.", file=sys.stderr)
        return None
def print_report(violations: list, output_format: str):
    print("\n--- Linter Report ---")
    if not violations:
        print("✅ No violations found. The soul of the Codex is pure.")
        return
    if output_format == 'json':
        report = { "linter_version": "1.2", "violations_found": len(violations), "violations": violations }
        print(json.dumps(report, indent=2))
    else:
        for v in violations:
            line_info = f"(Line {v['line_number']}) " if 'line_number' in v else ""
            print(f"[{v['severity']}] {v['file_path']} {line_info}")
            print(f"  - Rule: {v['rule_name']}")
            if v['error_type'] == 'contains_text':
                print(f"  - Details: Found forbidden word '{v['details']['forbidden_word']}' in line: \"{v['details']['full_line_content']}\"")
            elif v['error_type'] == 'lacks_link':
                 print(f"  - Details: {v['details']['context']} but required link '{v['details']['required_link']}' is missing.")
            elif v['error_type'] == 'must_start_with':
                 print(f"  - Details: Document must begin with '{v['details']['required_prefix']}'.")
            print("-" * 20)
        print(f"❌ Linter finished with {len(violations)} violation(s).")
def main():
    parser = argparse.ArgumentParser(description="Linter for the Soul: An ethical and philosophical linter for the Architect's Codex.")
    parser.add_argument('-i', '--input', default='codex_snapshot.txt', help="Path to the codex snapshot file.")
    parser.add_argument('-r', '--rules', default='soul.rules.yaml', help="Path to the soul rules configuration file.")
    parser.add_argument('-e', '--entities', default='sovereign_entities.yaml', help="Path to the sovereign entities manifest.")
    parser.add_argument('-o', '--output-format', choices=['text', 'json'], default='text', help="Format for the final report.")
    args = parser.parse_args()
    print("🚀 Running the Linter for the Soul v1.2...")
    try:
        print("  - Loading configurations...")
        rules_config = load_yaml_config(args.rules)
        entities_config = load_yaml_config(args.entities)
        sovereign_entities = entities_config.get('sovereign_entities', [])
        print(f"    ✅ Loaded {len(rules_config.get('rules',[]))} rules and {len(sovereign_entities)} sovereign entities.")
        with open(args.input, 'r', encoding='utf-8') as f:
            snapshot_content = f.read()
        codex_files = parse_codex_snapshot(snapshot_content)
        print("  - Analyzing files against the rulebook...")
        all_violations = []
        for file_path, file_content in codex_files.items():
            for rule in rules_config.get('rules', []):
                violation = run_check(file_path, file_content, rule, sovereign_entities)
                if violation:
                    all_violations.append(violation)
        print_report(all_violations, args.output_format)
    except FileNotFoundError as e:
        print(f"\n[FATAL ERROR] A required file was not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    main()