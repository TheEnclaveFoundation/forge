# This module contains the logic for interacting with Google's Gemini APIs.
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import os
import time
from typing import Type
from pydantic import BaseModel

from .. import validator

# --- Configuration ---
MAX_RETRIES = 1 # Re-prompting is a form of retry, so we limit network retries
INITIAL_BACKOFF_SECONDS = 1

def _call_api(model, prompt):
    """Internal function to make a single API call."""
    return model.generate_content(prompt)

def get_response(content: str, system_prompt: str, model_name: str, validation_model: Type[BaseModel] = None) -> dict:
    """
    Sends a request to the Google Gemini API, with optional validation and re-prompting.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": True, "error_type": "CONFIG_ERROR", "message": "Google API key not found."}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)
    full_prompt = f"{system_prompt}\n\n--- CONTENT TO ANALYZE ---\n\n{content}"
    
    last_error = None
    for attempt in range(MAX_RETRIES + 1): # Allow for one initial call + retries
        try:
            # --- API Call ---
            response = _call_api(model, full_prompt)
            final_response_text = response.text
            pydantic_object = None

            # --- Validation and Re-prompt Logic ---
            if validation_model:
                validation_attempt = validator.validate_response(final_response_text, validation_model)
                
                # If the first validation attempt fails, re-prompt the model once.
                if isinstance(validation_attempt, dict) and validation_attempt.get("error"):
                    reprompt_prompt = (
                        f"{full_prompt}\n\n"
                        "Your previous response failed validation with the following error:\n"
                        f"{validation_attempt['details']}\n\n"
                        "Please correct your response and output only the valid JSON object."
                    )
                    reprompt_response = _call_api(model, reprompt_prompt)
                    final_response_text = reprompt_response.text
                    
                    # Second and final validation attempt
                    final_validation_result = validator.validate_response(final_response_text, validation_model)
                    
                    if isinstance(final_validation_result, dict) and final_validation_result.get("error"):
                        return final_validation_result # Failed twice, return the final validation error
                    else:
                        pydantic_object = final_validation_result # Success on the second try
                else:
                    pydantic_object = validation_attempt # Success on the first try
            
            # --- Success Case ---
            input_tokens = model.count_tokens(full_prompt).total_tokens
            output_tokens = model.count_tokens(final_response_text).total_tokens
            
            return {
                "provider_used": "google", "model_name": model_name,
                "response_text": final_response_text,
                "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
                "validation_result": pydantic_object.model_dump() if pydantic_object else None
            }

        except google_exceptions.PermissionDenied as e:
            return {"error": True, "error_type": "API_AUTH_ERROR", "message": "Authentication failed.", "provider": "google", "details": str(e)}
        except google_exceptions.InvalidArgument as e:
            return {"error": True, "error_type": "BAD_REQUEST_ERROR", "message": "Invalid request.", "provider": "google", "details": str(e)}
        except Exception as e:
            last_error = e
            time.sleep(INITIAL_BACKOFF_SECONDS)
            continue
    
    return {"error": True, "error_type": "API_ERROR", "message": "An unexpected API error occurred.", "provider": "google", "details": str(last_error)}