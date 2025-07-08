# This module contains the logic for interacting with a local LLM endpoint.
import requests
import json
import os
import time

# --- Configuration ---
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1

def _estimate_tokens(text: str) -> int:
    """Provides a rough estimation of token count. A common heuristic is 4 chars/token."""
    return len(text) // 4

def get_response(content: str, system_prompt: str, model_name: str) -> dict:
    """
    Sends a request to a local LLM API endpoint and returns the response,
    including standardized error handling.
    """
    endpoint_url = os.getenv("LOCAL_MODEL_ENDPOINT")
    if not endpoint_url:
        return {
            "error": True, "error_type": "CONFIG_ERROR",
            "message": "Local model endpoint not found in environment.",
            "provider": "local", "details": "Please set LOCAL_MODEL_ENDPOINT in your .env file."
        }

    headers = {"Content-Type": "application/json"}
    full_prompt = f"{system_prompt}\n\n--- CONTENT TO ANALYZE ---\n\n{content}"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        "stream": False
    }
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(endpoint_url, headers=headers, data=json.dumps(payload), timeout=120)
            response.raise_for_status()
            response_data = response.json()
            response_text = ""
            if 'choices' in response_data and len(response_data['choices']) > 0:
                if 'message' in response_data['choices'][0]:
                     response_text = response_data['choices'][0]['message'].get('content', '')
            response_data['usage'] = {
                "input_tokens": _estimate_tokens(full_prompt),
                "output_tokens": _estimate_tokens(response_text),
                "note": "Token count is an estimation for local models."
            }
            return response_data
        except requests.exceptions.RequestException as e:
            last_error = e
            backoff = INITIAL_BACKOFF_SECONDS * (2 ** attempt)
            time.sleep(backoff)
            continue
        except json.JSONDecodeError as e:
            return {
                "error": True, "error_type": "API_ERROR",
                "message": "Failed to decode JSON response from local model.",
                "provider": "local", "details": response.text
            }

    return {
        "error": True, "error_type": "NETWORK_ERROR",
        "message": "Failed to connect to local model endpoint after multiple retries.",
        "provider": "local", "details": str(last_error)
    }