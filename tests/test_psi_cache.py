import hashlib
from forge.packages.psi import cache_manager

# This is a basic unit test using standard Python assertions that pytest can discover and run.

def test_get_cache_key_consistency():
    """
    Tests that the _get_cache_key function is deterministic and
    produces the same hash for the same input every time.
    """
    # --- Arrange ---
    content = "Hello, Oracle."
    system_prompt = "You are a helpful assistant."
    model_name = "gemini-1.5-pro"

    # --- Act ---
    key1 = cache_manager._get_cache_key(content, system_prompt, model_name)
    key2 = cache_manager._get_cache_key(content, system_prompt, model_name)

    # --- Assert ---
    assert key1 == key2
    assert isinstance(key1, str)
    assert len(key1) == 64 # SHA-256 hashes are 64 hex characters

def test_get_cache_key_sensitivity():
    """
    Tests that any change to the input produces a different hash.
    """
    # --- Arrange ---
    content = "Hello, Oracle."
    system_prompt = "You are a helpful assistant."
    model_name = "gemini-1.5-pro"

    # --- Act ---
    key_original = cache_manager._get_cache_key(content, system_prompt, model_name)
    key_content_changed = cache_manager._get_cache_key("Goodbye, Oracle.", system_prompt, model_name)
    key_prompt_changed = cache_manager._get_cache_key(content, "You are an unhelpful assistant.", model_name)
    
    # --- Assert ---
    assert key_original != key_content_changed
    assert key_original != key_prompt_changed