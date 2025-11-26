#!/usr/bin/env python3
"""
Text cleanup script using LLM API.
Removes redundant and repeated text from OCR output.
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def log_progress(message, log_file="cleanup_progress.log"):
    """Log progress messages to a file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)
    
    print(log_message.strip())

def cleanup_text_with_llm(input_text, api_key, log_file="cleanup_progress.log"):
    """
    Send text to LLM API to clean up and remove redundant content.
    
    Args:
        input_text: The text to clean up
        api_key: OpenRouter API key
        log_file: Path to log file
    
    Returns:
        Cleaned up text from the LLM
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Construct the request payload
    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct",
        "messages": [
            {
                "role": "user",
                "content": f"""I have OCR output from a Chinese historical document that contains extensive text repetition and redundancy. Please help me clean this up.

Here is the text:

{input_text}

Please:
1. Remove ALL redundant and repeated text
2. Keep only the UNIQUE content
3. Preserve the document structure (title, headings, sections)
4. Maintain proper formatting in markdown
5. Keep the text accurate and readable
6. Return ONLY the cleaned text without explanations

Please provide the clean, non-redundant version:"""
            }
        ],
        "temperature": 0.1,
        "max_tokens": 8000
    }
    
    log_progress("Sending text cleanup request to OpenRouter API...", log_file)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            cleaned_text = result['choices'][0]['message']['content']
            log_progress(f"Successfully received cleaned text ({len(cleaned_text)} characters)", log_file)
            return cleaned_text
        else:
            log_progress(f"Unexpected API response format: {result}", log_file)
            return None
            
    except requests.exceptions.RequestException as e:
        log_progress(f"API request failed: {str(e)}", log_file)
        if hasattr(e, 'response') and e.response is not None:
            log_progress(f"Response content: {e.response.text}", log_file)
        return None

def process_file(input_path, output_path, log_file="cleanup_progress.log"):
    """
    Read a markdown file, clean it up using LLM, and save the result.
    
    Args:
        input_path: Path to the input markdown file
        output_path: Path to the output markdown file
        log_file: Path to the log file
    """
    # Clear/initialize log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\n")
        f.write(f"Text Cleanup Processing Log\n")
        f.write(f"{'='*60}\n\n")
    
    log_progress(f"Starting text cleanup processing", log_file)
    log_progress(f"Input file: {input_path}", log_file)
    log_progress(f"Output file: {output_path}", log_file)
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        log_progress("ERROR: OPENROUTER_API_KEY not found in environment variables", log_file)
        log_progress("Please ensure .env file contains OPENROUTER_API_KEY=your_key_here", log_file)
        return False
    
    log_progress(f"API key loaded successfully", log_file)
    
    try:
        # Read input file
        log_progress(f"Reading input file...", log_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        input_size = len(input_text)
        log_progress(f"Input file size: {input_size} characters", log_file)
        
        # Clean up text using LLM
        cleaned_text = cleanup_text_with_llm(input_text, api_key, log_file)
        
        if cleaned_text:
            # Write output to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            output_size = len(cleaned_text)
            reduction = ((input_size - output_size) / input_size * 100) if input_size > 0 else 0
            
            log_progress(f"\n{'='*60}", log_file)
            log_progress(f"✓ Processing completed successfully!", log_file)
            log_progress(f"✓ Output saved to: {output_path}", log_file)
            log_progress(f"✓ Original size: {input_size} characters", log_file)
            log_progress(f"✓ Cleaned size: {output_size} characters", log_file)
            log_progress(f"✓ Reduction: {reduction:.1f}%", log_file)
            log_progress(f"{'='*60}", log_file)
            
            return True
        else:
            log_progress(f"Failed to clean up text", log_file)
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
    input_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/output.md"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/output_cleaned.md"
    log_file = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/cleanup_progress.log"
    
    print("=" * 60)
    print("Text Cleanup via LLM API")
    print("Removing redundant and repeated text")
    print("=" * 60)
    print()
    
    success = process_file(input_path, output_path, log_file)
    
    if success:
        print(f"\n✓ Cleanup complete!")
        print(f"✓ Output file: {output_path}")
        print(f"✓ Log file: {log_file}")
        sys.exit(0)
    else:
        print(f"\n✗ Cleanup failed. Check log file: {log_file}")
        sys.exit(1)

