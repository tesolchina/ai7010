#!/usr/bin/env python3
"""
Utility module to load API keys from centralized APIkey.md file
This helps keep API keys out of the codebase and git repository
"""

import os
import re

def load_api_key(key_name="openRouter", api_key_file=None):
    """
    Load API key from APIkey.md file
    
    Args:
        key_name: Name of the API key to load (e.g., "openRouter")
        api_key_file: Path to API key file (defaults to APIkey.md in project root)
    
    Returns:
        str: The API key value
        
    Raises:
        FileNotFoundError: If API key file doesn't exist
        ValueError: If API key not found in file
    """
    if api_key_file is None:
        # Default to APIkey.md in project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        api_key_file = os.path.join(script_dir, "APIkey.md")
    
    if not os.path.exists(api_key_file):
        raise FileNotFoundError(
            f"API key file not found: {api_key_file}\n"
            f"Please create APIkey.md with your API keys"
        )
    
    with open(api_key_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the API key file
    # Expected format: "keyName API key= sk-..."
    pattern = rf"{key_name}\s+API\s+key\s*=\s*(sk-[\w-]+)"
    match = re.search(pattern, content, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    raise ValueError(
        f"API key '{key_name}' not found in {api_key_file}\n"
        f"Expected format: '{key_name} API key= sk-...'"
    )


if __name__ == "__main__":
    # Test the function
    try:
        key = load_api_key("openRouter")
        print(f"✓ Successfully loaded OpenRouter API key: {key[:20]}...")
    except Exception as e:
        print(f"✗ Error: {e}")





