# This module contains the logic for interacting with a local LLM endpoint.
import requests
import json

def get_response(content: str, system_prompt: str, endpoint_url: str) -> dict:
    """
    Sends a request to a local LLM API endpoint and returns the response.
    """
    headers = {"Content-Type": "application/json"}
    
    # This payload structure is a common format for local models.
    # It may need to be adjusted based on the specific API of the local server.
    payload = {
        "model": "local-model", # The model name is often required, even if it's just one
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        "stream": False
    }

    try:
        response = requests.post(endpoint_url, headers=headers, data=json.dumps(payload), timeout=120)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        # This will catch connection errors, timeouts, etc.
        return {
            "error": "Failed to connect to local model endpoint.",
            "details": str(e)
        }
    except json.JSONDecodeError:
        return {
            "error": "Failed to decode JSON response from local model.",
            "details": response.text
        }