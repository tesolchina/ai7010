#!/usr/bin/env python3
"""
Generate high-level visualization using LLM image generation
Based on OpenRouter API with image generation models
"""

import requests
import json
from pathlib import Path
import base64
from datetime import datetime

# Paths
API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
TOC_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/toc_pa2025.txt')
OUTPUT_IMAGE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/pa2025_llm_visualization.png')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/llm_generation_log.txt')

def log(message):
    """Append message to log file and print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    with open(LOG_FILE, 'a') as f:
        f.write(f"{log_msg}\n")
    print(log_msg)

def init_log():
    """Initialize log file"""
    with open(LOG_FILE, 'w') as f:
        f.write("="*80 + "\n")
        f.write("LLM IMAGE GENERATION LOG\n")
        f.write("Task: Generate high-level visualization of Policy Address 2025 structure\n")
        f.write("="*80 + "\n\n")

def read_api_key():
    """Read API key from file"""
    log("Reading API key...")
    try:
        with open(API_KEY_FILE, 'r') as f:
            content = f.read().strip()
            if 'sk-or-v1-' in content:
                api_key = content.split('=')[1].strip()
            else:
                api_key = content.strip()
        log(f"✓ API key loaded: {api_key[:20]}...{api_key[-10:]}")
        return api_key
    except Exception as e:
        log(f"✗ ERROR: Failed to read API key: {e}")
        raise

def read_toc():
    """Read ToC file and create summary"""
    log("Reading ToC file...")
    try:
        with open(TOC_FILE, 'r', encoding='utf-8') as f:
            toc_content = f.read()
        
        # Extract main chapters only for high-level view
        lines = toc_content.split('\n')
        main_chapters = []
        for line in lines:
            if '■' in line or '●' in line:
                main_chapters.append(line.strip())
        
        summary = '\n'.join(main_chapters[:30])  # First 30 lines for high-level
        log(f"✓ ToC loaded: {len(toc_content)} chars total")
        log(f"✓ High-level summary: {len(main_chapters)} main sections")
        return summary
        
    except Exception as e:
        log(f"✗ ERROR: Failed to read ToC: {e}")
        raise

def generate_image_with_llm(api_key, toc_summary):
    """
    Use OpenRouter API to generate visualization image
    """
    log("Preparing LLM image generation request...")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Create a concise prompt for high-level visualization
    prompt = f"""Create a high-level visual diagram showing the structure of Hong Kong's 2025 Policy Address.

Show ONLY the main chapters as large sections/boxes with clear labels. Use a professional, clean design.

Main chapters to visualize:
{toc_summary}

Requirements:
- Simple, clean diagram showing chapter relationships
- Use colors to distinguish different policy areas
- Professional government document style
- Focus on HIGH-LEVEL structure only, no details
- Make it easy to understand at a glance"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/simonwang/ai7010",
        "X-Title": "Policy Address 2025 Visualization"
    }
    
    # Try different image-capable models
    models_to_try = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-90b-vision-instruct:free",
        "anthropic/claude-3.5-sonnet"
    ]
    
    for model in models_to_try:
        log(f"Trying model: {model}")
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000
        }
        
        # Add modalities if supported
        if "gemini" in model:
            data["modalities"] = ["image", "text"]
        
        try:
            log(f"Sending request to OpenRouter API...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            log(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                log("✓ Received successful response from API")
                
                # Check for images in response
                if result.get("choices"):
                    message = result["choices"][0]["message"]
                    
                    # Check if image was generated
                    if message.get("images"):
                        log(f"✓ Image generated! Found {len(message['images'])} image(s)")
                        
                        for idx, image in enumerate(message["images"]):
                            image_url = image["image_url"]["url"]
                            log(f"Processing image {idx + 1}...")
                            
                            # Save base64 image
                            if image_url.startswith("data:image"):
                                save_base64_image(image_url, OUTPUT_IMAGE)
                                log(f"✓ Image saved to: {OUTPUT_IMAGE}")
                                return True
                    
                    # If no image, save the text response
                    content = message.get("content", "")
                    if content:
                        log(f"Response content: {content[:200]}...")
                        log("Note: Model returned text instead of image")
                        
                        # Save text response for reference
                        text_output = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/llm_text_response.txt')
                        with open(text_output, 'w') as f:
                            f.write(content)
                        log(f"✓ Text response saved to: {text_output}")
                
                # Try next model if no image generated
                log("No image in response, trying next model...")
                continue
                
            elif response.status_code == 429:
                log(f"⚠ Rate limited (429) - trying next model...")
                continue
            else:
                log(f"⚠ Status {response.status_code}: {response.text[:200]}")
                continue
                
        except Exception as e:
            log(f"⚠ Error with {model}: {e}")
            continue
    
    log("✗ No models were able to generate an image")
    return False

def save_base64_image(data_url, output_path):
    """Save base64 encoded image to file"""
    try:
        # Extract base64 data
        if ',' in data_url:
            base64_data = data_url.split(',')[1]
        else:
            base64_data = data_url
        
        # Decode and save
        image_data = base64.b64decode(base64_data)
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        log(f"✓ Decoded and saved {len(image_data)} bytes")
    except Exception as e:
        log(f"✗ Error saving image: {e}")
        raise

def main():
    """Main function"""
    init_log()
    log("Starting LLM-based visualization generation...")
    log("")
    
    try:
        # Read API key
        api_key = read_api_key()
        log("")
        
        # Read ToC summary
        toc_summary = read_toc()
        log("")
        
        # Generate image
        log("Attempting to generate visualization with LLM...")
        success = generate_image_with_llm(api_key, toc_summary)
        
        log("")
        log("="*80)
        if success:
            log("✓✓✓ SUCCESS! LLM visualization generated!")
            log(f"Output: {OUTPUT_IMAGE}")
        else:
            log("⚠ LLM did not generate an image")
            log("Note: Most text-based models don't generate images directly")
            log("The Python-generated visualization is still available")
        log("="*80)
        
    except Exception as e:
        log("")
        log("="*80)
        log(f"✗✗✗ FATAL ERROR: {e}")
        log("="*80)
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    main()

