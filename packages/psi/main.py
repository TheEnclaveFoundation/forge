#!/usr/bin/env python3
# --- Psi (Ψ/ψ) | The Oracle ---
import sys
import argparse
import json
import os
import yaml
from dotenv import load_dotenv

from .providers import google, local
from . import cache_manager
from . import config
from forge.packages.common import ui as loom

# --- Provider Dispatcher ---
PROVIDER_MAP = {
    'google': google,
    'local': local,
}

def load_provider_config() -> dict:
    """Loads the providers.yaml config and builds a model-to-provider map."""
    try:
        providers_path = os.path.join(os.path.dirname(__file__), 'providers.yaml')
        with open(providers_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        
        model_map = {}
        for provider, models in cfg.items():
            for model_info in models:
                model_map[model_info['model_name']] = provider
        return model_map
    except Exception as e:
        # Since this runs early, a simple print is fine.
        print(json.dumps({"error": True, "error_type": "CONFIG_ERROR", "message": f"Failed to load or parse providers.yaml: {e}"}), file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for the Psi CLI tool."""
    load_dotenv(dotenv_path=os.path.join(config.FOUNDATION_ROOT, '.env'))
    is_piped = not sys.stdout.isatty()

    parser = argparse.ArgumentParser(description="Psi (Ψ): The Oracle for qualitative analysis.", add_help=False)
    parser.add_argument('--prompt-file', required=True, type=str, help="Path to a file containing the system prompt (relative to project root).")
    parser.add_argument('--model', required=True, type=str, help="The specific model to use (e.g., 'gemini-1.5-pro').")
    parser.add_argument('--no-cache', action='store_true', help="Bypass the cache for a fresh response.")
    parser.add_argument('--verbose', action='store_true', help="Output the full, raw JSON response to stdout.")
    parser.add_argument('--response', action='store_true', help="Output the LLM's response.")
    parser.add_argument('--metadata', action='store_true', help="Print a formatted metadata report to stderr.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()
    
    # --- Assemble Render Plan ---
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
        print(json.dumps({"error": True, "error_type": "CONFIG_ERROR", "message": f"Prompt file not found: {prompt_file_path}"}), file=sys.stderr)
        return

    # --- Get Result (from Cache or Live) ---
    result = None
    if not args.no_cache:
        result = cache_manager.get_cached_response(content_to_analyze, system_prompt, args.model)
    
    if not result:
        model_to_provider_map = load_provider_config()
        provider_name = model_to_provider_map.get(args.model)
        # Error handling for provider/model not found
        if not provider_name or not PROVIDER_MAP.get(provider_name):
            print(json.dumps({"error": True, "error_type": "CONFIG_ERROR", "message": f"Model '{args.model}' or its provider is not configured."}), file=sys.stderr)
            return
        
        provider_module = PROVIDER_MAP.get(provider_name)
        result = provider_module.get_response(content_to_analyze, system_prompt, args.model)
        
        if not args.no_cache and not result.get('error'):
            cache_manager.set_cached_response(content_to_analyze, system_prompt, args.model, result, args.prompt_file)

    # --- Handle All Output ---

    # If an error occurred, print it as JSON and exit
    if result.get('error'):
        print(json.dumps(result, indent=2))
        return

    # Build the UI render plan for stderr
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

    render_plan.append({"type": "end", "text": "Done.", "color": "green"})
    loom.render(render_plan)
    
    # Handle stdout for piping
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