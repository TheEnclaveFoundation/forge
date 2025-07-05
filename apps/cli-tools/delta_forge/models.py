# --- Data Models ---

class DeltaOperation:
    """Represents a single delta operation with its properties."""
    def __init__(self, index: int):
        self.index = index
        self.path = None
        self.action = None
        self.target_block = ""
        self.replacement_content = ""
        self.content = ""