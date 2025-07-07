# This module contains the logic for interacting with Google's Gemini APIs.
import google.generativeai as genai
import os

def get_response(content: str, system_prompt: str, model_name: str) -> dict:
    """
    Sends a request to the Google Gemini API and returns the response,
    including token count information.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY not found in environment or .env file."}

    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(model_name=model_name)

        full_prompt = f"{system_prompt}\n\n--- CONTENT TO ANALYZE ---\n\n{content}"

        response = model.generate_content(full_prompt)
        
        # Calculate token counts
        input_tokens = model.count_tokens(full_prompt).total_tokens
        output_tokens = model.count_tokens(response.text).total_tokens
        
        return {
            "provider_used": "google",
            "model_name": model_name,
            "response_text": response.text,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
        }
    except Exception as e:
        return {
            "error": "An error occurred while communicating with the Google Gemini API.",
            "details": str(e)
        }
