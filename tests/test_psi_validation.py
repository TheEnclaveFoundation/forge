from pydantic import BaseModel
from forge.packages.psi import validator

# 1. Define the data structure we expect from the LLM
class SimpleResponse(BaseModel):
    name: str
    value: int
    is_correct: bool

def test_successful_validation():
    """
    Tests that a valid JSON string is correctly parsed into a Pydantic model.
    """
    # --- Arrange ---
    json_string = '{"name": "test", "value": 123, "is_correct": true}'
    
    # --- Act ---
    # This function does not exist yet. We will create it next.
    result = validator.validate_response(json_string, SimpleResponse)

    # --- Assert ---
    assert isinstance(result, SimpleResponse)
    assert result.name == "test"
    assert result.value == 123
    assert result.is_correct is True

def test_failed_validation():
    """
    Tests that an invalid JSON string returns a validation error, not the model.
    """
    # --- Arrange ---
    # This JSON is missing the 'is_correct' field.
    json_string = '{"name": "test", "value": 123}'

    # --- Act ---
    result = validator.validate_response(json_string, SimpleResponse)

    # --- Assert ---
    # The result should be the error object, not the Pydantic model.
    assert not isinstance(result, SimpleResponse)
    assert isinstance(result, dict)
    assert result.get("error_type") == "VALIDATION_ERROR"