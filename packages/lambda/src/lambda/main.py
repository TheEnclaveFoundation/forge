import sys
import argparse
import os

from forge.packages.common.ui import Colors
from .loaders import load_yaml_config, parse_codex_snapshot
from .dispatcher import run_check
from .reporting import print_report
from .ui import print_banner, print_summary, print_header, print_end_line

def main():
    """Main entry point for the Lambda CLI tool."""
    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    default_rules_path = os.path.join(package_root, 'soul.rules.yaml')
    default_entities_path = os.path.join(package_root, 'sovereign_entities.yaml')

    parser = argparse.ArgumentParser(description="Lambda (Λ/λ): A deterministic linter.", add_help=False)
    parser.add_argument('-i', '--input', help="Path to snapshot file (used if stdin is empty).")
    parser.add_argument('-r', '--rules', default=default_rules_path, help="Path to rules file.")
    parser.add_argument('-e', '--entities', default=default_entities_path, help="Path to entities file.")
    parser.add_argument('-o', '--output-format', choices=['text', 'json'], default='text', help="Output format. JSON is always verbose.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    print_banner()

    snapshot_content = ""
    is_piped = not sys.stdin.isatty()

    if is_piped:
        snapshot_content = sys.stdin.read()
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            snapshot_content = f.read()
    else:
        print_header("Error:")
        print_end_line(f"{Colors.YELLOW}No input provided. Please pipe a snapshot or use --input.{Colors.RESET}")
        return

    try:
        rules_config = load_yaml_config(args.rules)
        entities_config = load_yaml_config(args.entities)
        sovereign_entities = entities_config.get('sovereign_entities', [])
        
        codex_files = parse_codex_snapshot(snapshot_content)
        
        all_violations = []
        for file_path, file_content in codex_files.items():
            for rule in rules_config.get('rules', []):
                violation = run_check(file_path, file_content, rule, sovereign_entities)
                if violation:
                    all_violations.append(violation)
        
        violation_count = print_report(all_violations, args.output_format, args.verbose)
        print_summary(violation_count)

    except FileNotFoundError as e:
        print_header("Fatal Error:")
        print_end_line(f"{Colors.RED}A required file was not found: {e}{Colors.RESET}")
    except Exception as e:
        print_header("Fatal Error:")
        print_end_line(f"{Colors.RED}An unexpected error occurred: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()