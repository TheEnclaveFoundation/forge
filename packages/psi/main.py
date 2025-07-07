# --- Psi (Ψ/ψ) | The Oracle ---
# This package contains the logic for interacting with a high-capability
# LLM to provide nuanced, qualitative judgment.

import sys
import argparse
import json
import os
from dotenv import load_dotenv

# Import the provider modules
from .providers import local
# from .providers import google, openai # These will be implemented later

def consult_oracle(content: str, system_prompt: str, provider: str, api_key: str, endpoint_url: str) -> dict:
    """
    Routes the request to the correct provider and makes the API call.
    """
    if provider == 'local':
        if not endpoint_url:
            return {"error": "Local provider selected, but no LOCAL_MODEL_ENDPOINT was found in the environment or .env file."}
        return local.get_response(content, system_prompt, endpoint_url)
    # In the future, we would add the logic for other providers here
    # elif provider == 'google':
    #     return google.get_response(content, system_prompt, api_key)
    else:
        # Fallback to a mocked response for now
        mock_response = {
            "provider_used": provider,
            "analysis_summary": "The provided text generally adheres to the core principles, but the tone could be warmer.",
            "actionable_feedback": [
                "Consider rephrasing the section on 'Locus Sovereignty' to be less technical."
            ],
            "adherence_score": 0.85,
            "request_tokens": len(content.split()) + len(system_prompt.split()),
            "response_tokens": 42
        }
        return mock_response

def main():
    """Main entry point for the Psi CLI tool."""
    # Load secrets from a .env file in the project root
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

    parser = argparse.ArgumentParser(description="Psi (Ψ): The Oracle for qualitative analysis.", add_help=False)
    parser.add_argument('--prompt-file', required=True, type=str, help="Path to a file containing the system prompt (the 'lens').")
    parser.add_argument('--provider', choices=['google', 'openai', 'local'], default='google', help="The LLM provider to use.")
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    # Get the appropriate secrets from environment variables
    api_key = os.getenv(f"{args.provider.upper()}_API_KEY")
    endpoint_url = os.getenv("LOCAL_MODEL_ENDPOINT")

    # The local provider doesn't need an API key, but others will.
    if args.provider != 'local' and not api_key:
        print(json.dumps({"error": f"API key '{args.provider.upper()}_API_KEY' not found in environment or .env file."}), file=sys.stderr)
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
    
    result = consult_oracle(content_to_analyze, system_prompt, args.provider, api_key, endpoint_url)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()