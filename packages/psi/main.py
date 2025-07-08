#!/usr/bin/env python3
# --- Psi (Ψ/ψ) | The Oracle (CLI Wrapper) ---
import sys
import argparse
import json
import os
from dotenv import load_dotenv

from .client import get_oracle_response
from . import config
from . import models
from forge.packages.common import ui as loom

# --- Pydantic Model Registry ---
MODEL_REGISTRY = {
    'SimpleResponse': models.SimpleResponse,
}

def main():
    """Main entry point for the Psi CLI tool."""
    load_dotenv(dotenv_path=os.path.join(config.FOUNDATION_ROOT, '.env'))
    is_piped = not sys.stdout.isatty()

    parser = argparse.ArgumentParser(description="Psi (Ψ): The Oracle for qualitative analysis.", add_help=False)
    parser.add_argument('--prompt-file', required=True, type=str, help="Path to a file containing the system prompt (relative to project root).")
    parser.add_argument('--model', required=True, type=str, help="The specific model to use.")
    parser.add_argument('--validate-with', type=str, choices=MODEL_REGISTRY.keys(), help="The Pydantic model to validate the response against.")
    parser.add_argument('--no-cache', action='store_true', help="Bypass the cache for a fresh response.")
    parser.add_argument('--verbose', action='store_true', help="Output the full, raw JSON response to stdout.")
    parser.add_argument('--response', action='store_true', help="Output the LLM's response.")
    parser.add_argument('--metadata', action='store_true', help="Print a formatted metadata report to stderr.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()
    
    render_plan = []
    
    prompt_file_path = args.prompt_file
    if not os.path.isabs(prompt_file_path):
        prompt_file_path = os.path.join(config.FOUNDATION_ROOT, prompt_file_path)

    content_to_analyze = sys.stdin.read()
    if not content_to_analyze.strip():
        render_plan.append({"type": "banner", "symbol": "Ψ", "color": "cyan"})
        render_plan.append({"type": "end", "text": "No content received from stdin.", "color": "yellow"})
        loom.render(render_plan)
        return

    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": True, "error_type": "CONFIG_ERROR", "message": f"Prompt file not found: {prompt_file_path}"}))
        return

    validation_model = MODEL_REGISTRY.get(args.validate_with) if args.validate_with else None

    # --- Call the reusable client function ---
    result = get_oracle_response(
        content=content_to_analyze,
        system_prompt=system_prompt,
        model_name=args.model,
        no_cache=args.no_cache,
        validation_model=validation_model,
        prompt_file_path=args.prompt_file
    )

    # --- Handle All Output ---
    if result.get('error'):
        print(json.dumps(result, indent=2))
        return

    # --- Assemble and Render UI ---
    render_plan.append({"type": "banner", "symbol": "Ψ", "color": "cyan"})
    render_plan.append({"type": "group", "title": "Oracle Parameters", "items": [
        {"key": "Model", "value": args.model},
        {"key": "Prompt", "value": args.prompt_file}
    ]})

    if args.metadata:
        is_cached = result.get('__cache_hit__', False)
        status = "Cache Hit" if is_cached else "Live Call"
        usage = result.get('usage', {})
        render_plan.append({"type": "group", "title": "Metadata", "items": [
            {"key": "Status", "value": status},
            {"key": "Provider", "value": result.get('provider_used', 'N/A')},
            {"key": "Model", "value": result.get('model_name', 'N/A')},
            {"key": "Tokens", "value": f"{usage.get('input_tokens', 'N/A')} (in) / {usage.get('output_tokens', 'N/A')} (out)"}
        ]})
    
    if args.response:
        response_text = result.get('response_text', '')
        if not response_text and 'choices' in result:
             if len(result['choices']) > 0 and 'message' in result['choices'][0]:
                response_text = result['choices'][0]['message'].get('content', '')
        render_plan.append({"type": "prose", "title": "Oracle Response", "text": response_text})

    render_plan.append({"type": "end"})
    loom.render(render_plan)
    
    # --- Handle Stdout for Piping ---
    if args.verbose:
        print(json.dumps(result, indent=2))
    elif args.response and is_piped:
        response_text = result.get('response_text', '')
        if not response_text and 'choices' in result:
             if len(result['choices']) > 0 and 'message' in result['choices'][0]:
                response_text = result['choices'][0]['message'].get('content', '')
        print(response_text)

if __name__ == "__main__":
    main()
