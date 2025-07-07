# --- Psi: Cache Manager ---
import os
import json
import hashlib
import time
from typing import Dict, Any

# --- Configuration ---
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '.cache', 'psi')
CACHE_TTL_SECONDS = 60 * 60 * 24 * 7 # 7 days

# --- Internal Functions ---

def _get_cache_key(content: str, system_prompt: str, model_name: str) -> str:
    """Generates a consistent SHA-256 hash for the request."""
    payload = f"{content}|{system_prompt}|{model_name}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def _get_cache_path(key: str) -> str:
    """Constructs the full file path for a given cache key."""
    # Use subdirectories to avoid too many files in one folder
    return os.path.join(CACHE_DIR, key[:2], key)

# --- Public API ---

def get_cached_response(content: str, system_prompt: str, model_name: str) -> Dict[str, Any] | None:
    """
    Retrieves a cached response if it exists and is not expired.
    Returns the cached data or None.
    """
    key = _get_cache_key(content, system_prompt, model_name)
    path = _get_cache_path(key)

    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            cached_data = json.load(f)
        
        is_expired = (time.time() - cached_data.get('timestamp', 0)) > CACHE_TTL_SECONDS
        if is_expired:
            os.remove(path) 
            return None
            
        response = cached_data.get('response', {})
        response['__cache_hit'] = True
        return response

    except (json.JSONDecodeError, IOError):
        return None

def set_cached_response(content: str, system_prompt: str, model_name: str, response: Dict[str, Any]):
    """Saves a response to the cache."""
    key = _get_cache_key(content, system_prompt, model_name)
    path = _get_cache_path(key)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # The 'response' object itself now contains the usage data from the provider
    cache_data = {
        'timestamp': time.time(),
        'model_name': model_name,
        'response': response
    }

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    except IOError:
        pass