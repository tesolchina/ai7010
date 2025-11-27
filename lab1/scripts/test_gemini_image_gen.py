#!/usr/bin/env python3
"""
Test google/gemini-3-pro-image-preview model for image generation
This model should be able to generate images directly
"""

import requests
import json
from pathlib import Path
import base64
from datetime import datetime

# Paths
API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
TOC_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/toc_pa2025.txt')
OUTPUT_IMAGE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/pa2025_gemini_generated.png')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/llm_generation_log.txt')

def log(message):
    """Append message to log file and print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    with open(LOG_FILE, 'a') as f:
        f.write(f"{log_msg}\n")
    print(log_msg)

def read_api_key():
    """Read API key from file"""
    with open(API_KEY_FILE, 'r') as f:
        content = f.read().strip()
        if 'sk-or-v1-' in content:
            api_key = content.split('=')[1].strip()
        else:
            api_key = content.strip()
    return api_key

def read_toc_summary():
    """Read ToC and create brief summary"""
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get main chapters only
    chapters = []
    for line in lines:
        if '●' in line and 'Chapter' in line:
            chapters.append(line.split('●')[1].strip())
    
    return '\n'.join(chapters)

def test_gemini_image_generation():
    """Test Gemini image generation model"""
    
    log("")
    log("="*80)
    log("TESTING GOOGLE GEMINI-3-PRO-IMAGE-PREVIEW MODEL")
    log("="*80)
    
    # Read API key
    log("Reading API key...")
    api_key = read_api_key()
    log(f"✓ API key loaded: {api_key[:20]}...{api_key[-10:]}")
    
    # Read ToC summary
    log("Reading ToC summary...")
    toc_summary = read_toc_summary()
    log(f"✓ ToC summary prepared ({len(toc_summary)} chars)")
    
    # Prepare request
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/simonwang/ai7010",
        "X-Title": "Policy Address Visualization - Gemini"
    }
    
    # Create prompt for image generation
    prompt = f"""Generate a clean, professional diagram showing the structure of Hong Kong's 2025 Policy Address.

Create a visual diagram with:
- Title: "2025 Hong Kong Policy Address Structure"
- 10 colored boxes representing these chapters:

{toc_summary}

Use different colors for different themes:
- Blue for governance chapters
- Green for development chapters  
- Purple for international chapters
- Orange for social/cultural chapters

Make it professional, clean, and easy to read at a glance."""

    log("")
    log("Preparing API request...")
    log(f"Model: google/gemini-3-pro-image-preview")
    log(f"Modalities: [image, text]")
    log(f"Prompt length: {len(prompt)} chars")
    
    data = {
        "model": "google/gemini-3-pro-image-preview",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "modalities": ["image", "text"],
        "max_tokens": 2000
    }
    
    try:
        log("")
        log("Sending request to OpenRouter API...")
        log("Please wait...")
        
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data),
            timeout=90
        )
        
        log(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            log("✓ Request successful!")
            result = response.json()
            
            # Pretty print the response structure
            log("")
            log("Response structure:")
            log(json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2))
            
            # Check for choices
            if result.get("choices"):
                log(f"✓ Found {len(result['choices'])} choice(s)")
                
                message = result["choices"][0]["message"]
                log(f"Message keys: {list(message.keys())}")
                
                # Check for images
                if message.get("images"):
                    log(f"✓✓✓ SUCCESS! Found {len(message['images'])} image(s)!")
                    
                    for idx, image in enumerate(message["images"]):
                        log(f"Processing image {idx + 1}...")
                        
                        # Get image URL/data
                        image_url = image.get("image_url", {}).get("url", "")
                        
                        if image_url:
                            log(f"Image URL prefix: {image_url[:50]}...")
                            
                            # Save base64 image
                            if image_url.startswith("data:image"):
                                # Extract base64 data
                                if ',' in image_url:
                                    base64_data = image_url.split(',')[1]
                                else:
                                    base64_data = image_url
                                
                                # Decode and save
                                image_data = base64.b64decode(base64_data)
                                with open(OUTPUT_IMAGE, 'wb') as f:
                                    f.write(image_data)
                                
                                log(f"✓ Image decoded: {len(image_data)} bytes")
                                log(f"✓ Saved to: {OUTPUT_IMAGE}")
                                
                                return True
                            else:
                                log(f"⚠ Image URL not in base64 format")
                                log(f"Full URL: {image_url}")
                        else:
                            log("⚠ No image_url found in image object")
                            log(f"Image object: {image}")
                
                # Check for text content
                if message.get("content"):
                    content = message["content"]
                    log(f"Text content ({len(content)} chars):")
                    log(content[:500] + "..." if len(content) > 500 else content)
                    
                    # Save text response
                    text_file = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/gemini_response.txt')
                    with open(text_file, 'w') as f:
                        f.write(content)
                    log(f"✓ Text response saved to: {text_file}")
            
            # Print full response for debugging
            log("")
            log("Full API response:")
            log(json.dumps(result, indent=2))
            
            return False
            
        elif response.status_code == 429:
            log("⚠ Rate limited (429)")
            log("The model is temporarily unavailable due to rate limits")
            log(f"Response: {response.text}")
            return False
            
        elif response.status_code == 404:
            log("⚠ Model not found (404)")
            log("This model may not be available on OpenRouter")
            log(f"Response: {response.text}")
            return False
            
        elif response.status_code == 400:
            log("⚠ Bad request (400)")
            log("The request parameters may be incorrect")
            log(f"Response: {response.text}")
            return False
            
        else:
            log(f"✗ Request failed with status {response.status_code}")
            log(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log("✗ Request timed out after 90 seconds")
        return False
        
    except Exception as e:
        log(f"✗ Error: {e}")
        import traceback
        log(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        success = test_gemini_image_generation()
        
        log("")
        log("="*80)
        if success:
            log("✓✓✓ IMAGE SUCCESSFULLY GENERATED!")
            log(f"Output: {OUTPUT_IMAGE}")
        else:
            log("⚠ No image was generated")
            log("Check logs above for details")
        log("="*80)
        
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        log(traceback.format_exc())

