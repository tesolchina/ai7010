"""
Generate new slide images based on Gemini redesign specifications
Uses DALL-E or other image generation models to create visual slides
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI

# Configuration
API_KEY_FILE = "/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt"
OUTPUT_DIR = "/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides"
PROGRESS_LOG = os.path.join(OUTPUT_DIR, "image_generation_log.txt")

# Models
ANALYSIS_MODEL = "google/gemini-2.5-flash-image-preview"  # For analyzing original slides
IMAGE_GEN_MODEL = "openai/dall-e-3"  # For generating new slide images

def log_progress(message):
    """Log progress to both console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(PROGRESS_LOG, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def load_api_key():
    """Load API key from file"""
    with open(API_KEY_FILE, 'r') as f:
        content = f.read().strip()
        if '=' in content:
            return content.split('=')[1].strip()
        return content

def analyze_and_create_prompt(client, slide_image_path, slide_number):
    """
    Use Gemini to analyze the slide and create a detailed image generation prompt
    """
    log_progress(f"Analyzing slide {slide_number} with Gemini...")
    
    try:
        # Read the image file
        import base64
        with open(slide_image_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Create analysis prompt for Gemini
        prompt = f"""You are an expert presentation designer. Analyze this slide (Slide {slide_number}) and create a DALL-E image generation prompt that will produce a beautiful, modern redesigned version.

Your task:
1. Understand the current slide's content and message
2. Create a detailed DALL-E prompt (max 400 words) that will generate a stunning redesigned slide

The DALL-E prompt should specify:
- Exact text to display on the slide
- Layout and composition
- Color scheme and visual style
- Typography style (modern, professional, etc.)
- Background elements, icons, graphics
- Overall aesthetic (minimalist, bold, tech-inspired, etc.)

Make it professional, modern, and suitable for an academic/tech presentation.

IMPORTANT: 
- Start with "A professional presentation slide design showing..."
- Include ALL text that should appear on the slide
- Be specific about colors, layout, and style
- Keep it under 400 words

Return ONLY the DALL-E prompt, nothing else."""

        # Call Gemini API
        response = client.chat.completions.create(
            model=ANALYSIS_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        dalle_prompt = response.choices[0].message.content.strip()
        log_progress(f"✓ Created DALL-E prompt for slide {slide_number}")
        
        return dalle_prompt
        
    except Exception as e:
        log_progress(f"✗ Error analyzing slide {slide_number}: {str(e)}")
        return None

def generate_slide_image(client, dalle_prompt, slide_number):
    """
    Generate new slide image using DALL-E
    """
    log_progress(f"Generating new image for slide {slide_number}...")
    
    try:
        response = client.images.generate(
            model=IMAGE_GEN_MODEL.split('/')[-1],  # Just 'dall-e-3'
            prompt=dalle_prompt,
            size="1792x1024",  # Widescreen presentation format
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        log_progress(f"✓ Image generated for slide {slide_number}")
        log_progress(f"  URL: {image_url}")
        
        return image_url
        
    except Exception as e:
        log_progress(f"✗ Error generating image for slide {slide_number}: {str(e)}")
        return None

def download_image(image_url, output_path):
    """Download image from URL"""
    import requests
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        log_progress(f"✓ Image saved to: {output_path}")
        return True
        
    except Exception as e:
        log_progress(f"✗ Error downloading image: {str(e)}")
        return False

def save_prompt(slide_number, dalle_prompt):
    """Save the DALL-E prompt for reference"""
    output_file = os.path.join(OUTPUT_DIR, f"slide_{slide_number}_dalle_prompt.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"DALL-E PROMPT FOR SLIDE {slide_number}\n")
        f.write("=" * 50 + "\n\n")
        f.write(dalle_prompt)
    
    log_progress(f"Saved DALL-E prompt to: {output_file}")

def main(start_slide=1, end_slide=2):
    """Main processing function"""
    
    # Initialize progress log
    with open(PROGRESS_LOG, 'w', encoding='utf-8') as f:
        f.write("")
    
    log_progress("="*60)
    log_progress("Starting Slide Image Generation Process")
    log_progress(f"Processing slides {start_slide} to {end_slide}")
    log_progress("="*60)
    
    # Load API key and initialize client
    try:
        api_key = load_api_key()
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        log_progress("✓ API client initialized successfully")
    except Exception as e:
        log_progress(f"✗ Failed to initialize API client: {e}")
        return
    
    # Process each slide
    slide_images_dir = os.path.join(OUTPUT_DIR, "slide_images")
    
    for slide_num in range(start_slide, end_slide + 1):
        slide_image = os.path.join(slide_images_dir, f"slide_{slide_num}.png")
        
        if not os.path.exists(slide_image):
            log_progress(f"⚠ Warning: Image not found for slide {slide_num}")
            continue
        
        log_progress(f"\n{'='*60}")
        log_progress(f"Processing slide {slide_num}/{end_slide}")
        log_progress(f"{'='*60}")
        
        # Step 1: Analyze with Gemini and create DALL-E prompt
        dalle_prompt = analyze_and_create_prompt(client, slide_image, slide_num)
        
        if not dalle_prompt:
            log_progress(f"Skipping slide {slide_num} due to analysis error")
            continue
        
        # Save the prompt
        save_prompt(slide_num, dalle_prompt)
        
        # Step 2: Generate image with DALL-E
        image_url = generate_slide_image(client, dalle_prompt, slide_num)
        
        if not image_url:
            log_progress(f"Skipping slide {slide_num} due to generation error")
            continue
        
        # Step 3: Download and save the generated image
        output_image_path = os.path.join(OUTPUT_DIR, f"slide_{slide_num}_new.png")
        download_image(image_url, output_image_path)
        
        log_progress(f"{'='*60}")
        log_progress(f"Completed slide {slide_num}/{end_slide}")
        log_progress(f"{'='*60}\n")
        
        # Brief pause between requests
        if slide_num < end_slide:
            log_progress("Waiting 2 seconds before next slide...")
            time.sleep(2)
    
    log_progress("="*60)
    log_progress("Image generation complete!")
    log_progress(f"New slide images saved to: {OUTPUT_DIR}")
    log_progress("="*60)

if __name__ == "__main__":
    import sys
    
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    main(start_slide=start, end_slide=end)

