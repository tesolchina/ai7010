#!/usr/bin/env python3
"""
Test OpenRouter API key validity
"""

import requests
import json
from pathlib import Path

API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')

def test_api_key():
    """Test if the API key is valid by making a simple request"""
    
    # Read API key
    print("Reading API key from file...")
    with open(API_KEY_FILE, 'r') as f:
        content = f.read().strip()
        # Extract the key value
        if 'sk-or-v1-' in content:
            api_key = content.split('=')[1].strip()
        else:
            api_key = content.strip()
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print("\n" + "="*60)
    print("Testing API key with OpenRouter...")
    print("="*60 + "\n")
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/simonwang/ai7010",
        "X-Title": "API Key Test"
    }
    
    # Simple test request with a free model
    data = {
        "model": "google/gemini-2.0-flash-exp:free",  # Free model for testing
        "messages": [
            {
                "role": "user",
                "content": "Hello! Just testing if this API key works. Please respond with 'OK'."
            }
        ],
        "max_tokens": 10
    }
    
    try:
        print("Sending test request to OpenRouter...")
        print(f"Model: {data['model']}")
        print(f"Endpoint: {url}\n")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! API key is VALID")
            print("="*60)
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"Response from API: {message}")
            
            if 'model' in result:
                print(f"Model used: {result['model']}")
            
            if 'usage' in result:
                print(f"Tokens used: {result['usage']}")
                
            print("="*60)
            return True
            
        else:
            print("\n❌ FAILED! API key is INVALID or has issues")
            print("="*60)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print("="*60)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    
    if success:
        print("\n✓ Your OpenRouter API key is working correctly!")
        print("You can now use it for API requests.")
    else:
        print("\n✗ There's an issue with your API key.")
        print("Please check:")
        print("  1. The key is correct and not expired")
        print("  2. You have credits/quota available")
        print("  3. The key has proper permissions")

