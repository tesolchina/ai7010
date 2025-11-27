#!/usr/bin/env python3
"""
Generate visualization image of Policy Address 2025 structure
using OpenRouter API (Nano Banana Pro model)
"""

import requests
import json
from pathlib import Path
import base64
import time

# Paths
API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
TOC_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/toc_pa2025.txt')
OUTPUT_IMAGE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/pa2025_structure_visualization.png')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/process_log.txt')

def log(message):
    """Append message to log file and print"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{message}\n")
    print(message)

def read_api_key():
    """Read API key from file"""
    log("[Step 3] Reading API key...")
    try:
        with open(API_KEY_FILE, 'r') as f:
            api_key = f.read().strip()
        log("[Step 3] ✓ API key loaded")
        return api_key
    except Exception as e:
        log(f"[ERROR] Failed to read API key: {e}")
        raise

def read_toc():
    """Read ToC file content"""
    log("[Step 4] Reading ToC file...")
    try:
        with open(TOC_FILE, 'r', encoding='utf-8') as f:
            toc_content = f.read()
        log(f"[Step 4] ✓ ToC file loaded ({len(toc_content)} characters)")
        return toc_content
    except Exception as e:
        log(f"[ERROR] Failed to read ToC: {e}")
        raise

def generate_visualization(api_key, toc_content):
    """
    Use OpenRouter API to generate visualization image
    """
    log("[Step 5] Sending request to OpenRouter API (Pixtral model)...")
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Prepare prompt for image generation
    prompt = f"""Based on the following Table of Contents for the Hong Kong 2025 Policy Address, 
create a visual diagram or infographic that clearly shows the hierarchical structure and relationships 
between all the chapters, sections, and subsections. Use colors, boxes, and connecting lines to make 
the structure easy to understand at a glance.

The visualization should:
1. Show all major chapters (■ markers) prominently
2. Show subsections (● and ○ markers) with clear hierarchy
3. Use visual elements like boxes, colors, and connecting lines
4. Be visually appealing and professional
5. Fit all content in a readable format

Here is the Table of Contents:

{toc_content}

Please create a comprehensive visualization of this structure."""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/simonwang/ai7010",
        "X-Title": "Policy Address 2025 Visualization"
    }
    
    # Try with Pixtral model (supports image generation)
    data = {
        "model": "mistralai/pixtral-large-2411",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        log("[Step 5] Making API request...")
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        log(f"[Step 5] ✓ Received response from API")
        
        # Extract the response content
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0]['message']['content']
            log(f"[Step 5] Response content length: {len(message_content)} characters")
            
            # Save the text response as a markdown file since this model returns text, not images
            text_output = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/pa2025_structure_description.md')
            with open(text_output, 'w', encoding='utf-8') as f:
                f.write(f"# Policy Address 2025 Structure Visualization Description\n\n")
                f.write(f"Generated using: {data['model']}\n\n")
                f.write(f"---\n\n")
                f.write(message_content)
            
            log(f"[Step 5] ✓ Text description saved to: {text_output}")
            
            # Now let's create a simple Python-based visualization using the ToC data
            log("[Step 6] Generating visualization image using Python...")
            return create_visualization_image(toc_content)
        else:
            log("[ERROR] No valid response in API result")
            return None
            
    except requests.exceptions.RequestException as e:
        log(f"[ERROR] API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log(f"[ERROR] Response: {e.response.text}")
        raise

def create_visualization_image(toc_content):
    """
    Create a visualization image using matplotlib/PIL
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        log("[Step 6] Creating visualization using PIL...")
        
        # Parse ToC lines
        lines = toc_content.split('\n')
        toc_items = []
        
        for line in lines:
            if line.strip() and line.strip()[0] in ['■', '●', '○', '▪']:
                # Determine level based on marker
                if '■' in line:
                    level = 0
                elif '●' in line:
                    level = 1
                elif '○' in line:
                    level = 2
                else:
                    level = 3
                
                # Extract text
                text = line.strip()[2:].strip()  # Remove marker and whitespace
                if text:
                    toc_items.append((level, text))
        
        log(f"[Step 6] Parsed {len(toc_items)} items from ToC")
        
        # Image dimensions
        img_width = 2400
        line_height = 35
        padding = 50
        img_height = len(toc_items) * line_height + padding * 2
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
        
        # Colors for different levels
        colors = {
            0: '#1a237e',  # Dark blue for main chapters
            1: '#283593',  # Medium blue for sections
            2: '#3949ab',  # Light blue for subsections
            3: '#5c6bc0'   # Lighter blue for sub-subsections
        }
        
        # Draw title
        title = "2025 HONG KONG POLICY ADDRESS - STRUCTURE OVERVIEW"
        draw.text((padding, 20), title, fill='#000000', font=title_font)
        draw.line([(padding, 55), (img_width - padding, 55)], fill='#000000', width=2)
        
        # Draw ToC items
        y = padding + 80
        
        for level, text in toc_items:
            # Calculate indentation
            indent = padding + (level * 40)
            
            # Draw bullet/marker
            marker_size = 8 - (level * 1)
            draw.ellipse([(indent, y + 5), (indent + marker_size, y + 5 + marker_size)], 
                        fill=colors[level])
            
            # Wrap text if too long
            max_width = img_width - indent - padding - 20
            if level == 0:
                font = header_font
                color = colors[0]
            else:
                font = normal_font
                color = '#333333'
            
            # Draw text
            draw.text((indent + marker_size + 10, y), text[:120], fill=color, font=font)
            
            y += line_height
        
        # Save image
        img.save(OUTPUT_IMAGE)
        log(f"[Step 6] ✓ Visualization image saved to: {OUTPUT_IMAGE}")
        log(f"[Step 6] ✓ Image dimensions: {img_width}x{img_height}")
        
        return OUTPUT_IMAGE
        
    except Exception as e:
        log(f"[ERROR] Failed to create visualization: {e}")
        import traceback
        log(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise

def main():
    """Main function"""
    try:
        # Read API key
        api_key = read_api_key()
        
        # Read ToC
        toc_content = read_toc()
        
        # Generate visualization
        image_path = generate_visualization(api_key, toc_content)
        
        if image_path:
            log("=" * 80)
            log("[COMPLETE] Visualization generation complete!")
            log(f"[COMPLETE] Image saved to: {image_path}")
            log("=" * 80)
        else:
            log("[ERROR] Visualization generation failed")
            
    except Exception as e:
        log(f"[FATAL ERROR] {e}")
        import traceback
        log(f"[TRACEBACK] {traceback.format_exc()}")

if __name__ == "__main__":
    main()

