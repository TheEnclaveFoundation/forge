# This module contains the logic for interacting with Google's Gemini APIs.
import google.generativeai as genai
import os

def get_response(content: str, system_prompt: str, api_key: str, model_name: str) -> dict:
    """
    Sends a request to the Google Gemini API and returns the response.

    Args:
        content: The main text content to be analyzed.
        system_prompt: The system prompt to guide the model's behavior.
        api_key: The Google API key for authentication.
        model_name: The specific Gemini model to use (e.g., "gemini-1.5-pro").

    Returns:
        A dictionary containing the model's response or an error message.
    """
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # Construct the full prompt for the model
        full_prompt = f"{system_prompt}\n\n--- CONTENT TO ANALYZE ---\n\n{content}"

        response = model.generate_content(full_prompt)
        
        # In a real implementation, we would parse this response into our
        # standard JSON format. For now, we'll return the raw text content.
        return {
            "provider_used": "google",
            "model_name": model_name,
            "response_text": response.text
        }

    except Exception as e:
        # Catch any potential API errors (e.g., invalid key, model not found)
        return {
            "error": "An error occurred while communicating with the Google Gemini API.",
            "details": str(e)
        }