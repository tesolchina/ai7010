#!/usr/bin/env python3
"""
Generate missing slides 7 and 10 with more explicit prompts
"""

import requests
import json
from pathlib import Path
import base64
from datetime import datetime

API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
OUTPUT_DIR = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides')
LOG_FILE = OUTPUT_DIR / 'missing_slides_log.txt'

def log(message):
    """Log progress"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    with open(LOG_FILE, 'a') as f:
        f.write(f"{log_msg}\n")
    print(log_msg)

def read_api_key():
    """Read API key"""
    with open(API_KEY_FILE, 'r') as f:
        content = f.read().strip()
        return content.split('=')[1].strip() if '=' in content else content.strip()

def generate_slide(api_key, slide_num, content_prompt):
    """Generate a slide"""
    
    log(f"{'='*60}")
    log(f"Generating Slide {slide_num}")
    log(f"{'='*60}")
    
    prompt = f"""{content_prompt}

REQUIRED: This MUST be an actual visual slide image, not text instructions.

CRITICAL SPECIFICATIONS:
- Widescreen 16:9 format (1920x1080)
- Professional academic/tech presentation design
- Use teal/cyan (#00CBA7) as accent color
- Modern, clean typography
- Good use of white space
- **IMPORTANT: Include footer with "© 2024 AI Research Institute | Date: 27 Nov 2025"**

Generate the actual slide image now."""

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tesolchina/ai7010",
        "X-Title": "AI Research Slides - Gemini"
    }
    
    data = {
        "model": "google/gemini-3-pro-image-preview",
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "max_tokens": 2000
    }
    
    try:
        log(f"  Requesting image from Gemini...")
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("choices"):
                message = result["choices"][0]["message"]
                
                if message.get("images"):
                    image = message["images"][0]
                    image_url = image.get("image_url", {}).get("url", "")
                    
                    if image_url and image_url.startswith("data:image"):
                        base64_data = image_url.split(',')[1] if ',' in image_url else image_url
                        image_data = base64.b64decode(base64_data)
                        
                        output_path = OUTPUT_DIR / f"slide_{slide_num}_gemini.png"
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        log(f"  ✓ Slide {slide_num} generated: {len(image_data)} bytes")
                        log(f"  ✓ Saved to: {output_path}")
                        return True
                
                log(f"  ⚠ No image in response")
        else:
            log(f"  ✗ Status {response.status_code}: {response.text[:200]}")
        
        return False
        
    except Exception as e:
        log(f"  ✗ Error: {e}")
        return False

def main():
    """Generate missing slides"""
    
    with open(LOG_FILE, 'w') as f:
        f.write("")
    
    log("="*80)
    log("GENERATING MISSING SLIDES 7 and 10")
    log("="*80)
    
    api_key = read_api_key()
    log(f"✓ API key loaded")
    log("")
    
    # Slide 7: Lab template
    slide_7_prompt = """Create a presentation slide titled "Lab template: Input-process-output"

Content to display:
Lab: (name)
Input: file paths/ folder paths  
Process: instructions for AI agents on how to process the input
Output: designate a folder path (and file paths) where the output could be delivered
Reflection notes: what we learn through this lab

Make it clean, structured, and educational with modern design."""

    # Slide 10: Lab 2 Screening
    slide_10_prompt = """Create a presentation slide titled "Lab 2: Screening & Synthesis with IPO Model"

Three sections showing the Input-Process-Output model:

📥 INPUT:
• CSV file with abstracts from Lab 1
• Screening criteria
• Research questions

⚙️ PROCESS:
• Use AI to screen abstracts
• Filter relevant articles
• Extract key findings
• Synthesize results

📤 OUTPUT:
• Screened article list
• Synthesis summary
• Structured findings report

Use three-column layout with modern icons and professional design."""

    # Generate slides
    success_7 = generate_slide(api_key, 7, slide_7_prompt)
    
    import time
    time.sleep(3)
    
    success_10 = generate_slide(api_key, 10, slide_10_prompt)
    
    log("")
    log("="*80)
    log("COMPLETION SUMMARY")
    log(f"Slide 7: {'✓ Success' if success_7 else '✗ Failed'}")
    log(f"Slide 10: {'✓ Success' if success_10 else '✗ Failed'}")
    log("="*80)

if __name__ == "__main__":
    main()

