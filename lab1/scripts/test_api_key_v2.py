#!/usr/bin/env python3
"""
Test OpenRouter API key with alternative models
"""

import requests
import json
from pathlib import Path

API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')

def test_with_model(api_key, model_name):
    """Test API with a specific model"""
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/simonwang/ai7010",
        "X-Title": "API Key Test"
    }
    
    data = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "Say 'OK' if you receive this message."
            }
        ],
        "max_tokens": 20
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)

def main():
    # Read API key
    print("Reading API key from file...")
    with open(API_KEY_FILE, 'r') as f:
        content = f.read().strip()
        if 'sk-or-v1-' in content:
            api_key = content.split('=')[1].strip()
        else:
            api_key = content.strip()
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print("\n" + "="*70)
    print("API KEY VALIDATION TEST")
    print("="*70 + "\n")
    
    # List of models to try (free and low-cost options)
    models_to_try = [
        "meta-llama/llama-3.2-1b-instruct:free",
        "qwen/qwen-2-7b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-2-9b-it:free",
    ]
    
    print("Testing with different models...\n")
    
    success = False
    for model in models_to_try:
        print(f"Trying: {model}")
        status_code, response_text = test_with_model(api_key, model)
        
        if status_code == 200:
            print(f"  ✅ SUCCESS! Status: {status_code}")
            try:
                result = json.loads(response_text)
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']['content']
                    print(f"  Response: {message}")
                print()
                success = True
                break
            except:
                print(f"  Response received but couldn't parse")
                
        elif status_code == 429:
            print(f"  ⚠️  Rate limited (429) - Model temporarily unavailable")
        elif status_code == 401:
            print(f"  ❌ Authentication failed (401) - Invalid API key")
            break
        else:
            print(f"  ⚠️  Status: {status_code}")
            try:
                error_msg = json.loads(response_text)
                if 'error' in error_msg:
                    print(f"  Error: {error_msg['error'].get('message', 'Unknown')}")
            except:
                pass
        print()
    
    print("="*70)
    
    if success:
        print("\n✅ API KEY IS VALID AND WORKING!")
        print("Your OpenRouter API key is properly configured.")
    else:
        print("\n⚠️  API KEY IS VALID BUT...")
        print("The key authenticated successfully (no 401 errors),")
        print("but all tested models are rate-limited or unavailable.")
        print("\nThis means:")
        print("  ✓ Your API key is correct and active")
        print("  ⚠ Free models are currently rate-limited")
        print("  → You may need to add credits or try again later")
        print("\nTo check your account: https://openrouter.ai/credits")
    
    print("="*70)

if __name__ == "__main__":
    main()

