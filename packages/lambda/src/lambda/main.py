import sys
import argparse
import os

from .loaders import load_yaml_config, parse_codex_snapshot
from .dispatcher import run_check
from . import reporting
from forge.packages.common import ui as loom

def main():
    """Main entry point for the Lambda CLI tool."""
    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    default_rules_path = os.path.join(package_root, 'soul.rules.yaml')
    default_entities_path = os.path.join(package_root, 'sovereign_entities.yaml')

    parser = argparse.ArgumentParser(description="Lambda (Λ/λ): A deterministic linter.", add_help=False)
    parser.add_argument('-i', '--input', help="Path to snapshot file (used if stdin is empty).")
    parser.add_argument('-r', '--rules', default=default_rules_path, help="Path to rules file.")
    parser.add_argument('-e', '--entities', default=default_entities_path, help="Path to entities file.")
    parser.add_argument('-o', '--output-format', choices=['text', 'json'], default='text', help="Output format.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    render_plan = [{"type": "banner", "symbol": "Λ", "color": "cyan"}]

    snapshot_content = ""
    is_piped = not sys.stdin.isatty()

    if is_piped:
        snapshot_content = sys.stdin.read()
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            snapshot_content = f.read()
    else:
        render_plan.append({"type": "end", "text": "No input provided. Please pipe a snapshot or use --input.", "color": "yellow"})
        loom.render(render_plan)
        return

    try:
        rules_config = load_yaml_config(args.rules)
        entities_config = load_yaml_config(args.entities)
        sovereign_entities = entities_config.get('sovereign_entities', [])
        
        codex_files = parse_codex_snapshot(snapshot_content)
        render_plan.append({"type": "group", "title": "Parsing Snapshot", "items": [{"key": "Files Found", "value": str(len(codex_files))}]})
        
        all_violations = []
        for file_path, file_content in codex_files.items():
            for rule in rules_config.get('rules', []):
                violation = run_check(file_path, file_content, rule, sovereign_entities)
                if violation:
                    all_violations.append(violation)
        
        # Handle JSON output separately as it goes to stdout
        if args.output_format == 'json':
            reporting.print_json_report(all_violations)
            # We don't render a UI for JSON output
            return
            
        # Generate and append the main report to the render plan
        report_plan = reporting.generate_report_plan(all_violations, args.verbose)
        render_plan.extend(report_plan)

    except FileNotFoundError as e:
        render_plan.append({"type": "group", "title": "Fatal Error", "items": [{"key": "Message", "value": f"A required file was not found: {e}"}]})
    except Exception as e:
        render_plan.append({"type": "group", "title": "Fatal Error", "items": [{"key": "Message", "value": f"An unexpected error occurred: {e}"}]})

    render_plan.append({"type": "end"})
    loom.render(render_plan)

if __name__ == "__main__":
    main()