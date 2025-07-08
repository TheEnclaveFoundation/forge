# This module contains the logic for interacting with Google's Gemini APIs.
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import os
import time

# --- Configuration ---
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1

def get_response(content: str, system_prompt: str, model_name: str) -> dict:
    """
    Sends a request to the Google Gemini API and returns the response,
    including standardized error handling.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "error": True, "error_type": "CONFIG_ERROR",
            "message": "Google API key not found in environment.",
            "provider": "google", "details": "Please set GOOGLE_API_KEY in your .env file."
        }

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)
    full_prompt = f"{system_prompt}\n\n--- CONTENT TO ANALYZE ---\n\n{content}"
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(full_prompt)
            
            input_tokens = model.count_tokens(full_prompt).total_tokens
            output_tokens = model.count_tokens(response.text).total_tokens
            
            return {
                "provider_used": "google", "model_name": model_name,
                "response_text": response.text,
                "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}
            }
        except google_exceptions.PermissionDenied as e:
            return {
                "error": True, "error_type": "API_AUTH_ERROR",
                "message": "Authentication failed. Please check your API key.",
                "provider": "google", "details": str(e)
            }
        except google_exceptions.InvalidArgument as e:
             return {
                "error": True, "error_type": "BAD_REQUEST_ERROR",
                "message": "The request was invalid (e.g., unsupported model or content).",
                "provider": "google", "details": str(e)
            }
        except Exception as e:
            last_error = e
            backoff = INITIAL_BACKOFF_SECONDS * (2 ** attempt)
            time.sleep(backoff)
            continue

    return {
        "error": True, "error_type": "API_ERROR",
        "message": "API call failed after multiple retries.",
        "provider": "google", "details": str(last_error)
    }
