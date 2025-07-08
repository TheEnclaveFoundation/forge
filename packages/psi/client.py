# --- Psi: Oracle Client ---
import os
import sys
import yaml
from pydantic import BaseModel
from typing import Type

from .providers import google, local
from . import cache_manager
from . import config

# --- Provider Dispatcher ---
PROVIDER_MAP = {
    'google': google,
    'local': local,
}

def load_provider_config() -> dict:
    """Loads the providers.yaml config and builds a model-to-provider map."""
    try:
        providers_path = os.path.join(os.path.dirname(__file__), 'providers.yaml')
        with open(providers_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
    
        model_map = {}
        for provider, models in cfg.items():
            for model_info in models:
                model_map[model_info['model_name']] = provider
        return model_map
    except Exception as e:
        # In a library context, we should raise an exception or return an error dict
        return {"error": True, "error_type": "CONFIG_ERROR", "message": f"Failed to load or parse providers.yaml: {e}"}

def get_oracle_response(content: str, system_prompt: str, model_name: str, no_cache: bool = False, validation_model: Type[BaseModel] = None, prompt_file_path: str = "dynamic") -> dict:
    """
    The core, reusable function for getting a response from an LLM Oracle.
    This function handles provider dispatch, caching, and validation.
    It does NOT handle CLI-specific tasks like UI rendering or arg parsing.
    """
    result = None
    if not no_cache:
        result = cache_manager.get_cached_response(content, system_prompt, model_name)
    
    if result:
        return result

    model_to_provider_map = load_provider_config()
    if model_to_provider_map.get("error"):
        return model_to_provider_map

    provider_name = model_to_provider_map.get(model_name)
    if not provider_name or not PROVIDER_MAP.get(provider_name):
        return {"error": True, "error_type": "CONFIG_ERROR", "message": f"Model '{model_name}' or its provider is not configured."}
    
    provider_module = PROVIDER_MAP.get(provider_name)
    result = provider_module.get_response(
        content, 
        system_prompt, 
        model_name,
        validation_model=validation_model
    )
    
    # Cache the new result if successful
    if not no_cache and not result.get('error'):
        cache_manager.set_cached_response(content, system_prompt, model_name, result, prompt_file_path)

    return result

