import re

def check_contains_text(file_path: str, file_content: str, rule: dict) -> dict or None:
    """Checks if a file contains any forbidden words from a list using whole-word matching."""
    params = rule['check']['params']
    words_to_check = params.get('words', [])
    flags = re.IGNORECASE
    
    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        for word in words_to_check:
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
