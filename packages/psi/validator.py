# --- Psi: Pydantic Response Validator ---
import json
from typing import Type
from pydantic import BaseModel, ValidationError

def validate_response(json_string: str, model: Type[BaseModel]):
    """
    Attempts to parse and validate a JSON string against a given Pydantic model.

    Args:
        json_string: The JSON string response from the LLM.
        model: The Pydantic model class to validate against.

    Returns:
        An instance of the Pydantic model on success, or a standardized
        error dictionary on failure.
    """
    try:
        data = json.loads(json_string)
        validated_model = model.model_validate(data)
        return validated_model
    except ValidationError as e:
        return {
            "error": True,
            "error_type": "VALIDATION_ERROR",
            "message": "The LLM response did not conform to the required format.",
            "details": str(e)
        }
    except json.JSONDecodeError as e:
        return {
            "error": True,
            "error_type": "VALIDATION_ERROR",
            "message": "The LLM response was not valid JSON.",
            "details": str(e)
        }