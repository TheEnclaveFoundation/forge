# --- Data Models ---

class DeltaOperation:
    """Represents a single delta operation with its properties."""
    def __init__(self, index: int):
        self.index = index
        self.action = None
        # Standard path for most actions
        self.path = None
        # Specific paths for MOVE_FILE
        self.source_path = None
        self.destination_path = None
        # Content for content-based actions
        self.content = ""