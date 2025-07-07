# This module contains the logic for interacting with a local LLM endpoint.
import requests
import json
import os

def _estimate_tokens(text: str) -> int:
    """Provides a rough estimation of token count. A common heuristic is 4 chars/token."""
    return len(text) // 4

def get_response(content: str, system_prompt: str, model_name: str) -> dict:
    """
    Sends a request to a local LLM API endpoint and returns the response,
    including an *estimated* token count.
    """
    endpoint_url = os.getenv("LOCAL_MODEL_ENDPOINT")
    if not endpoint_url:
        return {"error": "LOCAL_MODEL_ENDPOINT not found in environment or .env file."}

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

    try:
        response = requests.post(endpoint_url, headers=headers, data=json.dumps(payload), timeout=120)
        response.raise_for_status()
        
        response_data = response.json()
        
        # We need to extract the actual text content from the response, which can vary
        response_text = ""
        if 'choices' in response_data and len(response_data['choices']) > 0:
            if 'message' in response_data['choices'][0]:
                 response_text = response_data['choices'][0]['message'].get('content', '')

        # Add estimated token usage to the original response object
        response_data['usage'] = {
            "input_tokens": _estimate_tokens(full_prompt),
            "output_tokens": _estimate_tokens(response_text),
            "note": "Token count is an estimation for local models."
        }

        return response_data
        
    except requests.exceptions.RequestException as e:
        return {
            "error": "Failed to connect to local model endpoint.",
            "details": str(e)
        }
    except json.JSONDecodeError:
        return {
            "error": "Failed to decode JSON response from local model.",
            "details": response.text
        }
