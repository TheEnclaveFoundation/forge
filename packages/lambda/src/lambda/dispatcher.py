import sys
from . import checks

def run_check(file_path: str, file_content: str, rule: dict, sovereign_entities: list) -> dict or None:
    """Maps a rule type from the config to the correct check function."""
    check_type = rule.get('check', {}).get('type')
    scope = rule.get('check', {}).get('scope', {})

    # Scope check
    if 'directory' in scope and not file_path.strip('./').startswith(scope['directory']):
        return None
    
    # Dispatch to the appropriate check function
    if check_type == "contains_text":
        return checks.check_contains_text(file_path, file_content, rule)
    elif check_type == "lacks_link_on_entity_interaction":
        return checks.check_lacks_link_on_entity_interaction(file_path, file_content, rule, sovereign_entities)
    elif check_type == "must_start_with":
        return checks.check_must_start_with(file_path, file_content, rule)
    else:
        print(f"  [Warning] Unknown check type '{check_type}' in rule '{rule['name']}'. Skipping.", file=sys.stderr)
        return None
