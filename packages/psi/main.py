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

# --- Provider Dispatcher ---
# A mapping from provider names to their respective modules.
# This makes the dispatcher extensible. Add a new provider here.
PROVIDER_MAP = {
    'google': google,
    'local': local,
    # 'openai': openai # Future-proofing
}

def load_provider_config() -> dict:
    """Loads the providers.yaml config and builds a model-to-provider map."""
    try:
        providers_path = os.path.join(os.path.dirname(__file__), 'providers.yaml')
        with open(providers_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        model_map = {}
        for provider, models in config.items():
            for model_info in models:
                model_map[model_info['model_name']] = provider
        return model_map
    except Exception as e:
        print(json.dumps({"error": f"Failed to load or parse providers.yaml: {e}"}), file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for the Psi CLI tool."""
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

    parser = argparse.ArgumentParser(description="Psi (Ψ): The Oracle for qualitative analysis.", add_help=False)
    parser.add_argument('--prompt-file', required=True, type=str, help="Path to a file containing the system prompt.")
    parser.add_argument('--model', required=True, type=str, help="The specific model to use (e.g., 'gemini-1.5-pro').")
    parser.add_argument('--no-cache', action='store_true', help="Bypass the cache for a fresh response.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    # Read content from stdin
    content_to_analyze = sys.stdin.read()
    if not content_to_analyze.strip():
        print(json.dumps({"error": "No content received from stdin."}), file=sys.stderr)
        sys.exit(1)

    # Read system prompt from file
    try:
        with open(args.prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"Prompt file not found: {args.prompt_file}"}), file=sys.stderr)
        sys.exit(1)

    # 1. Check cache first
    if not args.no_cache:
        cached_response = cache_manager.get_cached_response(content_to_analyze, system_prompt, args.model)
        if cached_response:
            print(json.dumps(cached_response, indent=2))
            return

    # 2. If no cache, proceed to API call
    model_to_provider_map = load_provider_config()
    provider_name = model_to_provider_map.get(args.model)
    if not provider_name:
        print(json.dumps({"error": f"Model '{args.model}' not found in providers.yaml."}), file=sys.stderr)
        sys.exit(1)

    provider_module = PROVIDER_MAP.get(provider_name)
    if not provider_module:
        print(json.dumps({"error": f"Provider '{provider_name}' is configured but not implemented."}), file=sys.stderr)
        sys.exit(1)
    
    result = provider_module.get_response(content_to_analyze, system_prompt, args.model)
    
    # 3. Cache the new response
    if not args.no_cache and not result.get('error'):
        cache_manager.set_cached_response(content_to_analyze, system_prompt, args.model, result)

    # Print the final result to stdout
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()