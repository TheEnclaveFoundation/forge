import json
from collections import Counter
from typing import List, Dict, Any

def _build_verbose_report_plan(violations: list) -> List[Dict[str, Any]]:
    """Builds a render plan for a verbose list of violations."""
    plan = []
    for v in violations:
        details = []
        if v['error_type'] == 'contains_text':
            details.append({"key": "Details", "value": f"Found forbidden word '{v['details']['forbidden_word']}'"})
        elif v['error_type'] == 'lacks_link':
            details.append({"key": "Details", "value": f"Required link '{v['details']['required_link']}' is missing."})
        elif v['error_type'] == 'must_start_with':
            details.append({"key": "Details", "value": f"Document must begin with '{v['details']['required_prefix']}'."})
        
        line_info = f"(Line {v['line_number']}) " if 'line_number' in v else ""
        
        plan.append({"type": "group", "title": f"{v['rule_name']} [{v['severity']}]", "items": [
            {"key": "File", "value": f"{v['file_path']} {line_info}"},
            *details
        ]})
    return plan

def _build_brief_report_plan(violations: list) -> List[Dict[str, Any]]:
    """Builds a render plan for a summarized report of violations."""
    rule_counts = Counter(v['rule_name'] for v in violations)
    rule_severities = {v['rule_name']: v['severity'] for v in violations}

    items = []
    for rule_name, count in rule_counts.items():
        severity = rule_severities.get(rule_name, 'DEFAULT')
        items.append({"key": f"[{severity}] {rule_name}", "value": f"{count} violation(s)"})

    return [{"type": "group", "title": "Violation Summary", "items": items}]

def generate_report_plan(violations: list, verbose: bool) -> List[Dict[str, Any]]:
    """
    Acts as a controller, building the render plan in the desired format.
    """
    if not violations:
        return [{"type": "group", "title": "Violation Report", "items": [{"key": "Status", "value": "No violations found."}]}]

    if verbose:
        return _build_verbose_report_plan(violations)
    else:
        return _build_brief_report_plan(violations)

def print_json_report(violations: list):
    """Prints a machine-readable JSON report to stdout."""
    report = { "lambda_version": "1.3", "violations_found": len(violations), "violations": violations }
    print(json.dumps(report, indent=2))
