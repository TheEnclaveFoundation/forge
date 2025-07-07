# This module contains the logic for interacting with a local LLM endpoint.
import requests
import json
import os

def get_response(content: str, system_prompt: str, model_name: str) -> dict:
    """
    Sends a request to a local LLM API endpoint and returns the response.
    It is responsible for retrieving its own endpoint URL from the environment.
    """
    endpoint_url = os.getenv("LOCAL_MODEL_ENDPOINT")
    if not endpoint_url:
        return {"error": "LOCAL_MODEL_ENDPOINT not found in environment or .env file."}

    headers = {"Content-Type": "application/json"}
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
        # Assume the local endpoint returns a structure we can use directly.
        # If not, this is where we would standardize it.
        return response.json()
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