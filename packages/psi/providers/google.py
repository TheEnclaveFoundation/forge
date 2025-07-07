# This module contains the logic for interacting with Google's Gemini APIs.
import google.generativeai as genai
import os

def get_response(content: str, system_prompt: str, model_name: str) -> dict:
    """
    Sends a request to the Google Gemini API and returns the response.
    It is responsible for retrieving its own API key from the environment.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY not found in environment or .env file."}

    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(model_name=model_name)

        full_prompt = f"{system_prompt}\n\n--- CONTENT TO ANALYZE ---\n\n{content}"

        response = model.generate_content(full_prompt)
        
        return {
            "provider_used": "google",
            "model_name": model_name,
            "response_text": response.text
        }
    except Exception as e:
        return {
            "error": "An error occurred while communicating with the Google Gemini API.",
            "details": str(e)
        }
