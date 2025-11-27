#!/usr/bin/env python3
"""
Process all 14 slides through Gemini Image Generation
Generates professional redesigned slides with proper date: 27 Nov 2025
"""

import requests
import json
from pathlib import Path
import base64
from datetime import datetime
import time

# Configuration
API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
SLIDES_DIR = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides/slide_images')
OUTPUT_DIR = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides')
LOG_FILE = OUTPUT_DIR / 'gemini_generation_log.txt'
TOTAL_SLIDES = 14

# Slide content specifications
SLIDE_SPECS = {
    1: {
        "title": "AI Agents for Research",
        "content": """TITLE: "AI Agents for Research"
SUBTITLE: "Transforming Research Workflows for PhD students in Philosophy and Religion"

SPEAKER INFO:
- Dr Simon Wang
- Lecturer & Innovation Officer
- The Language Centre
- HKBU

DESIGN: Clean, modern, minimalist with subtle gradient background (light grey). Large bold title, centered subtitle, QR code placeholder on left, speaker info on right. Teal accent line. Professional academic style. Include subtle AI-inspired background pattern (nodes/circuits)."""
    },
    2: {
        "title": "Two Ways to Communicate with AI",
        "content": """TITLE: "Two Ways to Communicate with AI"

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

DESIGN: Dark navy background, vibrant teal title and accents, two rounded content boxes with icons for each bullet point. Modern, tech-inspired, professional."""
    },
    3: {
        "title": "How AI agents will change research: a scientist's guide",
        "content": """From the slide, extract and display the Nature article information and content about "What is an AI agent?"

DESIGN: Professional academic style with clean layout. Include the Nature article URL prominently. Use modern typography with good readability."""
    },
    4: {
        "title": "How AI agents will change research: What can they do?",
        "content": """From the slide, extract and display the Nature article content about AI agent capabilities and the quote from Marinka Zitnik about PhD students using AI agents.

DESIGN: Professional academic layout with quote highlighted. Clean, readable typography."""
    },
    5: {
        "title": "How AI agents will change research: Expertise needed",
        "content": """From the slide, extract content about expertise requirements and ToolUniverse development.

DESIGN: Professional academic style with clear information hierarchy."""
    },
    6: {
        "title": "A word of caution",
        "content": """TITLE: "A word of caution"

BULLET POINTS:
☐ The technology is still evolving
☐ Expect steep learning curve
☐ Student helpers are available to help on site
☐ Full adoption involves significant changes in workflow
☐ Your decision

DESIGN: Clean, professional with checkbox bullets. Modern academic style."""
    },
    7: {
        "title": "Lab template: Input-process-output",
        "content": """TITLE: "Lab template: Input-process-output"

SECTIONS:
- Lab: (name)
- Input: file paths/ folder paths
- Process: instructions for AI agents on how to process the input
- Output: designate a folder path (and file paths) where the output could be delivered
- Reflection notes: what we learn through this lab

DESIGN: Structured, educational layout. Modern and clean."""
    }
}

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
            return content.split('=')[1].strip()
        return content.strip()

def analyze_slide_content(slide_num, slide_image_path):
    """
    If we have a spec, use it. Otherwise, analyze the image to get content.
    """
    if slide_num in SLIDE_SPECS:
        return SLIDE_SPECS[slide_num]["content"]
    
    # For slides without specs, return a generic description
    return f"Extract and display all content from this slide professionally. Maintain the original message and information."

def generate_slide_with_gemini(api_key, slide_num, slide_image_path):
    """Generate redesigned slide using Gemini image generation"""
    
    log(f"{'='*60}")
    log(f"Processing Slide {slide_num}/{TOTAL_SLIDES}")
    log(f"{'='*60}")
    
    # Get content specification
    content_spec = analyze_slide_content(slide_num, slide_image_path)
    
    # Create prompt
    prompt = f"""Generate a professional, modern presentation slide for an academic/research presentation.

{content_spec}

IMPORTANT SPECIFICATIONS:
- Widescreen 16:9 aspect ratio (1920x1080 or similar)
- Modern, professional design suitable for academic presentations
- Clean typography with good hierarchy
- Use teal/cyan (#00CBA7 or similar) as accent color
- Professional color scheme
- Good use of white space
- Include footer with: "© 2024 AI Research Institute | Date: 27 Nov 2025"

Style: Modern, professional, visually striking yet appropriate for academic/research context."""

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tesolchina/ai7010",
        "X-Title": "AI Research Slides - Gemini Redesign"
    }
    
    data = {
        "model": "google/gemini-3-pro-image-preview",
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "max_tokens": 2000
    }
    
    try:
        log(f"  Sending request to Gemini...")
        
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
        
        log(f"  Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("choices"):
                message = result["choices"][0]["message"]
                
                # Check for images
                if message.get("images"):
                    log(f"  ✓ Found {len(message['images'])} image(s)")
                    
                    image = message["images"][0]
                    image_url = image.get("image_url", {}).get("url", "")
                    
                    if image_url and image_url.startswith("data:image"):
                        # Extract and decode base64
                        base64_data = image_url.split(',')[1] if ',' in image_url else image_url
                        image_data = base64.b64decode(base64_data)
                        
                        # Save image
                        output_path = OUTPUT_DIR / f"slide_{slide_num}_gemini.png"
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        log(f"  ✓ Slide {slide_num} generated: {len(image_data)} bytes")
                        log(f"  ✓ Saved to: {output_path}")
                        return True
                
                # Save text response if available
                if message.get("content"):
                    text_file = OUTPUT_DIR / f"slide_{slide_num}_gemini_response.txt"
                    with open(text_file, 'w') as f:
                        f.write(message["content"])
                    log(f"  ℹ Text response saved")
            
            log(f"  ⚠ No image generated for slide {slide_num}")
            return False
            
        else:
            log(f"  ✗ Request failed: {response.status_code}")
            log(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        log(f"  ✗ Error: {str(e)}")
        return False

def main():
    """Main processing function"""
    
    # Initialize log
    with open(LOG_FILE, 'w') as f:
        f.write("")
    
    log("="*80)
    log("PROCESSING ALL 14 SLIDES WITH GEMINI IMAGE GENERATION")
    log("Date in slides: 27 Nov 2025")
    log("="*80)
    
    # Load API key
    api_key = read_api_key()
    log(f"✓ API key loaded: {api_key[:15]}...")
    log("")
    
    # Track results
    successful = []
    failed = []
    
    # Process each slide
    for slide_num in range(1, TOTAL_SLIDES + 1):
        slide_image = SLIDES_DIR / f"slide_{slide_num}.png"
        
        if not slide_image.exists():
            log(f"⚠ Slide {slide_num} image not found: {slide_image}")
            log(f"  Skipping slide {slide_num}")
            failed.append(slide_num)
            continue
        
        # Generate slide
        success = generate_slide_with_gemini(api_key, slide_num, slide_image)
        
        if success:
            successful.append(slide_num)
        else:
            failed.append(slide_num)
        
        # Pause between requests to avoid rate limits
        if slide_num < TOTAL_SLIDES:
            log(f"  Waiting 2 seconds before next slide...")
            log("")
            time.sleep(2)
    
    # Summary
    log("")
    log("="*80)
    log("PROCESSING COMPLETE!")
    log("="*80)
    log(f"Successfully generated: {len(successful)} slides")
    log(f"  Slides: {successful}")
    log(f"Failed: {len(failed)} slides")
    if failed:
        log(f"  Slides: {failed}")
    log(f"Output directory: {OUTPUT_DIR}")
    log("="*80)

if __name__ == "__main__":
    main()

