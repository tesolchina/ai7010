#!/usr/bin/env python3
"""
Use Gemini 3 Pro Image Preview to generate redesigned slide 2
Based on the test script approach
"""

import requests
import json
from pathlib import Path
import base64
from datetime import datetime

# Paths
API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
ORIGINAL_SLIDE = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides/slide_images/slide_2.png')
OUTPUT_IMAGE = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides/slide_2_gemini.png')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides/gemini_image_gen_log.txt')

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
        if '=' in content:
            api_key = content.split('=')[1].strip()
        else:
            api_key = content.strip()
    return api_key

def generate_slide_with_gemini():
    """Generate redesigned slide 2 using Gemini image generation"""
    
    # Initialize log
    with open(LOG_FILE, 'w') as f:
        f.write("")
    
    log("="*80)
    log("GENERATING SLIDE 2 WITH GOOGLE GEMINI-3-PRO-IMAGE-PREVIEW")
    log("="*80)
    
    # Read API key
    log("Reading API key...")
    api_key = read_api_key()
    log(f"✓ API key loaded: {api_key[:15]}...")
    
    # Prepare request
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tesolchina/ai7010",
        "X-Title": "AI Research Slides - Gemini Redesign"
    }
    
    # Create detailed prompt for slide generation
    prompt = """Generate a professional, modern presentation slide with the following specifications:

TITLE: "Two Ways to Communicate with AI"

LAYOUT: Two-column comparison layout

LEFT COLUMN - "Browser":
• More intuitive
• Natural language
• Context switching
• Time-consuming
• AI can only produce (multimodal) textual responses

RIGHT COLUMN - "IDE (Integrated Development Environment)":
• Learning curve
• Some setup
• Natural language + ...
• AI embedded in the context
• AI agents can autonomously read and edit files, search the web and write and run scripts

DESIGN SPECIFICATIONS:
- Background: Modern dark gradient (deep navy #1a1a2e to darker shade)
- Title: Large, centered at top in vibrant teal/cyan color (#00CBA7)
- Two rounded content boxes with subtle borders in teal
- Clean modern sans-serif fonts (Montserrat style)
- White text for bullet points
- Professional, tech-inspired aesthetic
- Minimalist and clean with good use of white space
- Widescreen 16:9 aspect ratio (1920x1080)

Style: Professional tech presentation suitable for academic/research context. Modern, bold, and visually striking."""

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
        log("Requesting Gemini to generate the slide image...")
        log("This may take 30-60 seconds...")
        
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data),
            timeout=120
        )
        
        log(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            log("✓ Request successful!")
            result = response.json()
            
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
                                
                                log("")
                                log("="*80)
                                log("✓✓✓ SLIDE 2 SUCCESSFULLY GENERATED!")
                                log(f"Output: {OUTPUT_IMAGE}")
                                log("="*80)
                                
                                return True
                            else:
                                log(f"⚠ Image URL not in base64 format")
                        else:
                            log("⚠ No image_url found")
                
                # Check for text content
                if message.get("content"):
                    content = message["content"]
                    log(f"Text response received ({len(content)} chars):")
                    log(content[:500] + "..." if len(content) > 500 else content)
                    
                    # Save text response
                    text_file = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides/slide_2_gemini_response.txt')
                    with open(text_file, 'w') as f:
                        f.write(content)
                    log(f"✓ Text response saved to: {text_file}")
                
                # No images found
                log("")
                log("⚠ No image was generated in the response")
                log("Full message structure:")
                log(json.dumps(message, indent=2))
            
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
        log("✗ Request timed out after 120 seconds")
        return False
        
    except Exception as e:
        log(f"✗ Error: {e}")
        import traceback
        log(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        success = generate_slide_with_gemini()
        
        if not success:
            log("")
            log("="*80)
            log("⚠ Image generation did not complete successfully")
            log("Check log above for details")
            log("="*80)
        
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        log(traceback.format_exc())

