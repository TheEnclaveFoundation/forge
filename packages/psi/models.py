from pydantic import BaseModel

class SimpleResponse(BaseModel):
    """
    A simple Pydantic model for testing validation.
    """
    name: str
    value: int
    is_correct: bool
