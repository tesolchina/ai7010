"""
Process Google Slides through Gemini AI for visual redesign
Processes slides one at a time and logs progress
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI

# Configuration
API_KEY_FILE = "/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt"
OUTPUT_DIR = "/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides"
PROGRESS_LOG = os.path.join(OUTPUT_DIR, "progress_log.txt")
TOTAL_SLIDES = 14

# Model to use - Gemini 2.5 Flash with image preview capabilities
MODEL = "google/gemini-2.5-flash-image-preview"

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
        # Extract the key after the = sign
        if '=' in content:
            return content.split('=')[1].strip()
        return content

def process_slide_with_gemini(client, slide_image_path, slide_number):
    """
    Process a single slide image through Gemini for redesign
    Returns the redesigned slide description
    """
    log_progress(f"Processing slide {slide_number}/{TOTAL_SLIDES}...")
    
    try:
        # Read the image file
        with open(slide_image_path, 'rb') as img_file:
            import base64
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Create the prompt
        prompt = f"""You are an expert presentation designer with expertise in creating visually stunning, modern slides.

TASK: Analyze this slide (Slide {slide_number}) and create a complete redesign that is more visually appealing while preserving the core message.

Please provide a comprehensive redesign plan including:

1. **SLIDE LAYOUT & STRUCTURE**
   - Detailed spatial arrangement of all elements
   - Grid/alignment system to use
   - White space distribution
   - Content hierarchy (what draws attention first, second, third)

2. **COLOR PALETTE**
   - Primary, secondary, and accent colors (with HEX codes)
   - Color psychology rationale
   - Contrast considerations for readability

3. **TYPOGRAPHY**
   - Font families for headers, subheaders, and body text
   - Font sizes (in pt)
   - Font weights and styles
   - Text alignment and spacing

4. **VISUAL ELEMENTS**
   - Specific icons, illustrations, or graphics to add
   - Placement and size of visual elements
   - Background patterns, gradients, or textures
   - Any charts, diagrams, or data visualizations

5. **DESIGN PRINCIPLES APPLIED**
   - Balance and symmetry
   - Visual flow and eye movement
   - Use of emphasis and focal points
   - Modern design trends incorporated

6. **IMPLEMENTATION DETAILS**
   - Exact text to display (keeping original meaning)
   - Positioning coordinates (top/middle/bottom, left/center/right)
   - Layer ordering (what's in front/behind)
   - Any animations or transitions to consider

7. **MOOD & AESTHETIC**
   - Overall style (minimalist, bold, playful, professional, etc.)
   - Emotional impact desired
   - Target audience considerations

Make this redesign modern, engaging, and professional. Think like a top-tier presentation designer creating slides for a TED talk or major conference."""

        # Call Gemini API
        response = client.chat.completions.create(
            model=MODEL,
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
            max_tokens=2000
        )
        
        redesign = response.choices[0].message.content
        log_progress(f"✓ Slide {slide_number} processed successfully")
        
        return redesign
        
    except Exception as e:
        error_msg = f"✗ Error processing slide {slide_number}: {str(e)}"
        log_progress(error_msg)
        return f"Error: {str(e)}"

def save_redesign(slide_number, redesign_text):
    """Save the redesign description to a file"""
    output_file = os.path.join(OUTPUT_DIR, f"slide_{slide_number}_redesign.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"SLIDE {slide_number} REDESIGN\n")
        f.write("=" * 50 + "\n\n")
        f.write(redesign_text)
    
    log_progress(f"Saved redesign for slide {slide_number} to: {output_file}")

def main(start_slide=1, end_slide=None):
    """Main processing function"""
    # Initialize
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize progress log
    with open(PROGRESS_LOG, 'w', encoding='utf-8') as f:
        f.write("")  # Create empty file
    
    if end_slide is None:
        end_slide = TOTAL_SLIDES
    
    log_progress("="*60)
    log_progress("Starting Google Slides Redesign Process")
    log_progress(f"Processing slides {start_slide} to {end_slide} (Total: {TOTAL_SLIDES})")
    log_progress("="*60)
    
    # Load API key and initialize client
    try:
        api_key = load_api_key()
        log_progress(f"Loaded API key: {api_key[:15]}...")
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
    
    if not os.path.exists(slide_images_dir):
        log_progress(f"Creating directory for slide images: {slide_images_dir}")
        os.makedirs(slide_images_dir, exist_ok=True)
        log_progress("Please capture slide images first using browser tools")
        log_progress("Images should be named: slide_1.png, slide_2.png, etc.")
        return
    
    # Check which slides are available
    available_slides = []
    for slide_num in range(start_slide, end_slide + 1):
        slide_image = os.path.join(slide_images_dir, f"slide_{slide_num}.png")
        if os.path.exists(slide_image):
            available_slides.append(slide_num)
    
    log_progress(f"Found {len(available_slides)} slides to process: {available_slides}")
    
    for slide_num in available_slides:
        slide_image = os.path.join(slide_images_dir, f"slide_{slide_num}.png")
        
        log_progress(f"\n{'='*60}")
        log_progress(f"Starting processing of slide {slide_num}/{end_slide}")
        log_progress(f"{'='*60}")
        
        # Process the slide
        redesign = process_slide_with_gemini(client, slide_image, slide_num)
        
        # Save the redesign
        save_redesign(slide_num, redesign)
        
        log_progress(f"{'='*60}")
        log_progress(f"Completed slide {slide_num}/{end_slide}")
        log_progress(f"{'='*60}\n")
        
        # Brief pause between requests
        if slide_num < end_slide:
            time.sleep(1)
    
    log_progress("="*60)
    log_progress(f"Processing complete! Processed {len(available_slides)} slides.")
    log_progress(f"Output saved to: {OUTPUT_DIR}")
    log_progress("="*60)

if __name__ == "__main__":
    import sys
    
    # Allow command-line arguments for start and end slides
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else TOTAL_SLIDES
    
    main(start_slide=start, end_slide=end)

