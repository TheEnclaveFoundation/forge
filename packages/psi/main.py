# --- Psi (Ψ/ψ) | The Oracle ---
# This package contains the logic for interacting with a high-capability
# LLM to provide nuanced, qualitative judgment.

import sys
import argparse
import json
import os
import yaml
from dotenv import load_dotenv

# Import the provider modules
from .providers import local, google
# from .providers import openai # To be implemented later

def consult_oracle(content: str, system_prompt: str, provider_config: dict, api_key: str, endpoint_url: str) -> dict:
    """
    Routes the request to the correct provider and makes the API call.
    """
    provider_name = provider_config.get('name')
    model_name = provider_config.get('model')

    if provider_name == 'local':
        if not endpoint_url:
            return {"error": "Local provider selected, but no LOCAL_MODEL_ENDPOINT was found."}
        return local.get_response(content, system_prompt, endpoint_url)
    
    elif provider_name == 'google':
        if not api_key:
            return {"error": "Google provider selected, but no GOOGLE_API_KEY was found."}
        return google.get_response(content, system_prompt, api_key, model_name)
    
    else:
        # Fallback for providers not yet implemented
        return {
            "error": f"Provider '{provider_name}' is not yet implemented."
        }

def main():
    """Main entry point for the Psi CLI tool."""
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

    parser = argparse.ArgumentParser(description="Psi (Ψ): The Oracle for qualitative analysis.", add_help=False)
    parser.add_argument('--prompt-file', required=True, type=str, help="Path to a file containing the system prompt.")
    parser.add_argument('--model', required=True, type=str, help="The specific model to use (e.g., 'gemini-1.5-pro').")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    # Load provider configurations
    try:
        providers_path = os.path.join(os.path.dirname(__file__), 'providers.yaml')
        with open(providers_path, 'r', encoding='utf-8') as f:
            providers_config = yaml.safe_load(f)
    except Exception as e:
        print(json.dumps({"error": f"Failed to load providers.yaml: {e}"}), file=sys.stderr)
        sys.exit(1)

    # Find which provider the selected model belongs to
    selected_provider_name = None
    for provider, models in providers_config.items():
        if any(m['model_name'] == args.model for m in models):
            selected_provider_name = provider
            break
    
    if not selected_provider_name:
        print(json.dumps({"error": f"Model '{args.model}' not found in providers.yaml."}), file=sys.stderr)
        sys.exit(1)

    # Get the appropriate secrets from environment variables
    api_key = os.getenv(f"{selected_provider_name.upper()}_API_KEY")
    endpoint_url = os.getenv("LOCAL_MODEL_ENDPOINT")
    
    provider_config = {'name': selected_provider_name, 'model': args.model}

    if selected_provider_name != 'local' and not api_key:
        print(json.dumps({"error": f"API key '{selected_provider_name.upper()}_API_KEY' not found in environment or .env file."}), file=sys.stderr)
        sys.exit(1)

    content_to_analyze = sys.stdin.read()
    if not content_to_analyze.strip():
        print(json.dumps({"error": "No content received from stdin."}), file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"Prompt file not found: {args.prompt_file}"}), file=sys.stderr)
        sys.exit(1)
    
    result = consult_oracle(content_to_analyze, system_prompt, provider_config, api_key, endpoint_url)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()