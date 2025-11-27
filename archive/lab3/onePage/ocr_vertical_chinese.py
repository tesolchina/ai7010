#!/usr/bin/env python3
"""
LLM-based OCR script for vertical Chinese text.
Converts vertical text to horizontal readable format.
Uses OpenRouter API with Qwen-2.5-72b VL vision model.
"""

from PIL import Image
import base64
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def log_progress(message, log_file="progress.log"):
    """Log progress messages to a file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)
    
    print(log_message.strip())

def image_to_base64(image_path):
    """
    Convert an image file to a base64-encoded string.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Base64-encoded image string
    """
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    return img_base64

def call_openrouter_vision(image_base64, api_key, log_file="progress.log"):
    """
    Call OpenRouter API with Qwen-2.5-72b VL model to OCR vertical Chinese text.
    
    Args:
        image_base64: Base64-encoded image
        api_key: OpenRouter API key
        log_file: Path to log file
    
    Returns:
        Extracted and converted text from the LLM
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Construct the request payload with specific instructions for vertical text
    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct",  # Vision model
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Please carefully OCR ALL the text from this image. This is a historical Chinese document with VERTICAL text layout (reading top-to-bottom, right-to-left).

Please:
1. Extract ALL the text accurately, including the title at the top
2. Convert the vertical text layout to horizontal readable format (left-to-right)
3. Preserve the structure and paragraphs
4. Maintain proper punctuation and formatting
5. Return the text in clean, readable markdown format

Start from the rightmost column and work your way left, converting each vertical column to horizontal text."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "max_tokens": 6000
    }
    
    log_progress("Sending request to OpenRouter API...", log_file)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            extracted_text = result['choices'][0]['message']['content']
            log_progress(f"Successfully received response ({len(extracted_text)} characters)", log_file)
            return extracted_text
        else:
            log_progress(f"Unexpected API response format: {result}", log_file)
            return None
            
    except requests.exceptions.RequestException as e:
        log_progress(f"API request failed: {str(e)}", log_file)
        if hasattr(e, 'response') and e.response is not None:
            log_progress(f"Response content: {e.response.text}", log_file)
        return None

def process_image_with_llm(image_path, output_path, log_file="progress.log"):
    """
    Process a single image with vertical Chinese text using LLM vision model.
    
    Args:
        image_path: Path to the input image file
        output_path: Path to the output markdown file
        log_file: Path to the log file
    """
    # Clear/initialize log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\n")
        f.write(f"Vertical Chinese Text OCR Processing Log\n")
        f.write(f"{'='*60}\n\n")
    
    log_progress(f"Starting vertical Chinese text OCR processing", log_file)
    log_progress(f"Input image: {image_path}", log_file)
    log_progress(f"Output file: {output_path}", log_file)
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        log_progress("ERROR: OPENROUTER_API_KEY not found in environment variables", log_file)
        log_progress("Please ensure .env file contains OPENROUTER_API_KEY=your_key_here", log_file)
        return False
    
    log_progress(f"API key loaded successfully", log_file)
    
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            log_progress(f"ERROR: Image file not found: {image_path}", log_file)
            return False
        
        # Convert image to base64
        log_progress(f"Converting image to base64...", log_file)
        img_base64 = image_to_base64(image_path)
        img_size_kb = len(img_base64) / 1024
        log_progress(f"Image converted: {img_size_kb:.1f} KB (base64)", log_file)
        
        # Call LLM API
        log_progress(f"Calling OpenRouter API (Qwen-2.5-72b VL) for vertical text OCR...", log_file)
        extracted_text = call_openrouter_vision(img_base64, api_key, log_file)
        
        if extracted_text:
            # Prepare output content
            output_lines = []
            output_lines.append(f"# Vertical Chinese Text OCR Output\n\n")
            output_lines.append(f"**Source:** {os.path.basename(image_path)}\n\n")
            output_lines.append(f"**Processing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            output_lines.append(f"**Note:** Converted from vertical (top-to-bottom, right-to-left) to horizontal (left-to-right) format\n\n")
            output_lines.append("---\n\n")
            output_lines.append(extracted_text)
            output_lines.append("\n\n---\n\n")
            
            # Write output to file
            output_content = ''.join(output_lines)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            log_progress(f"\n{'='*60}", log_file)
            log_progress(f"✓ Processing completed successfully!", log_file)
            log_progress(f"✓ Output saved to: {output_path}", log_file)
            log_progress(f"✓ Total output size: {len(output_content)} characters", log_file)
            log_progress(f"{'='*60}", log_file)
            
            return True
        else:
            log_progress(f"Failed to extract text from image", log_file)
            return False
        
    except Exception as e:
        log_progress(f"\n✗ Error occurred: {str(e)}", log_file)
        import traceback
        error_details = traceback.format_exc()
        log_progress(f"Traceback:\n{error_details}", log_file)
        return False

if __name__ == "__main__":
    import sys
    
    # Define paths
    image_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/image.png"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/output.md"
    log_file = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/ocr_progress.log"
    
    print("=" * 60)
    print("Vertical Chinese Text OCR")
    print("LLM Vision Model (Qwen-2.5-72b VL)")
    print("=" * 60)
    print()
    
    success = process_image_with_llm(image_path, output_path, log_file)
    
    if success:
        print(f"\n✓ Processing complete!")
        print(f"✓ Output file: {output_path}")
        print(f"✓ Log file: {log_file}")
        sys.exit(0)
    else:
        print(f"\n✗ Processing failed. Check log file: {log_file}")
        sys.exit(1)





