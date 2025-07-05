import json
from collections import Counter
from forge.packages.common.ui import Colors
from .ui import print_header, print_line

def _print_verbose_report(violations: list, output_format: str):
    """Formats and prints the full, detailed list of violations."""
    if output_format == 'json':
        report = { "lambda_version": "1.3", "violations_found": len(violations), "violations": violations }
        print(json.dumps(report, indent=2))
        return

    print_header("Violation Report (Verbose):")
    for v in violations:
        line_info = f"(Line {v['line_number']}) " if 'line_number' in v else ""
        print_line(f"{v['file_path']} {line_info}")
        print_line(f"  └─ Rule: {v['rule_name']} [{v['severity']}]")
        if v['error_type'] == 'contains_text':
            print_line(f"     └─ Details: Found forbidden word '{v['details']['forbidden_word']}'")
        elif v['error_type'] == 'lacks_link':
            print_line(f"     └─ Details: Required link '{v['details']['required_link']}' is missing.")
        elif v['error_type'] == 'must_start_with':
            print_line(f"     └─ Details: Document must begin with '{v['details']['required_prefix']}'.")

def _print_brief_report(violations: list):
    """Formats and prints a summarized, color-coded report of violations."""
    print_header("Violation Summary:")
    rule_counts = Counter(v['rule_name'] for v in violations)
    rule_severities = {v['rule_name']: v['severity'] for v in violations}

    severity_colors = {
        'ERROR': Colors.RED,
        'STYLE': Colors.YELLOW,
        'STRUCTURE': Colors.PURPLE,
        'DEFAULT': Colors.GREY
    }

    for rule_name, count in rule_counts.items():
        severity = rule_severities.get(rule_name, 'DEFAULT')
        color = severity_colors.get(severity, severity_colors['DEFAULT'])
        print_line(f"{color}[{severity}]{Colors.RESET} {rule_name}: {count} violation(s)")

def print_report(violations: list, output_format: str, verbose: bool) -> int:
    """
    Acts as a controller, printing the report in the desired format
    and returning the total violation count.
    """
    if not violations:
        print_header("Violation Report:")
        print_line(f"{Colors.GREEN}No violations found.{Colors.RESET}")
        return 0

    if verbose or output_format == 'json':
        _print_verbose_report(violations, output_format)
    else:
        _print_brief_report(violations)
    
    return len(violations)
