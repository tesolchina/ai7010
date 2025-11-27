#!/usr/bin/env python3
"""
LLM-based OCR script for processing entire PDF files.
Uses OpenRouter API with Qwen-2.5-72b VL vision model.
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import base64
import requests
import json
import os
import sys
from datetime import datetime

# Add project root to path to import api_key_loader
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from api_key_loader import load_api_key

def log_progress(message, log_file="PDFllm_progress.log"):
    """Log progress messages to a file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)
    
    print(log_message.strip())

def pdf_page_to_base64(page, dpi=200):
    """
    Convert a PDF page to a base64-encoded PNG image.
    
    Args:
        page: PyMuPDF page object
        dpi: Resolution for rendering (default 200)
    
    Returns:
        Base64-encoded PNG image string
    """
    # Calculate zoom factor for desired DPI (72 is default)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    
    # Render page to pixmap
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    # Convert to PIL Image
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_base64

def call_openrouter_vision(image_base64, api_key, prompt=None, log_file="PDFllm_progress.log"):
    """
    Call OpenRouter API with Qwen-2.5-72b VL model to process an image.
    
    Args:
        image_base64: Base64-encoded image
        api_key: OpenRouter API key
        prompt: Custom prompt (optional)
        log_file: Path to log file
    
    Returns:
        Extracted text from the LLM
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Default prompt if not provided
    if prompt is None:
        prompt = "Please extract and transcribe ALL text from this image. Preserve the layout and structure as much as possible. Return the text in markdown format."
    
    # Construct the request payload
    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct",  # Vision model
        "messages": [
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
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }
    
    log_progress("Sending request to OpenRouter API...", log_file)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
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

def process_pdf_with_llm(pdf_path, output_path, api_key, log_file="PDFllm_progress.log", max_pages=None):
    """
    Process an entire PDF using LLM vision model.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to the output markdown file
        api_key: OpenRouter API key
        log_file: Path to the log file
        max_pages: Maximum number of pages to process (None for all pages)
    """
    # Clear/initialize log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\n")
        f.write(f"PDF LLM Processing Log\n")
        f.write(f"{'='*60}\n\n")
    
    log_progress(f"Starting LLM PDF processing", log_file)
    log_progress(f"Input PDF: {pdf_path}", log_file)
    log_progress(f"Output file: {output_path}", log_file)
    log_progress(f"API Key: {api_key[:20]}...", log_file)
    
    try:
        # Open the PDF
        log_progress(f"Opening PDF file...", log_file)
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_process = min(max_pages, total_pages) if max_pages else total_pages
        
        log_progress(f"Total pages in PDF: {total_pages}", log_file)
        log_progress(f"Processing {pages_to_process} pages", log_file)
        
        # Prepare output content
        output_lines = []
        output_lines.append(f"# LLM OCR Output from {os.path.basename(pdf_path)}\n\n")
        output_lines.append(f"**Extracted using Qwen-2.5-72b VL via OpenRouter API**\n\n")
        output_lines.append(f"*Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        output_lines.append(f"*Total Pages Processed: {pages_to_process}*\n\n")
        output_lines.append("---\n\n")
        
        # Process each page
        for page_num in range(pages_to_process):
            log_progress(f"\n{'='*50}", log_file)
            log_progress(f"Processing Page {page_num + 1}/{pages_to_process}", log_file)
            log_progress(f"{'='*50}", log_file)
            
            page = doc[page_num]
            
            # Convert page to base64 image
            log_progress(f"Converting page {page_num + 1} to image...", log_file)
            img_base64 = pdf_page_to_base64(page, dpi=200)
            img_size_kb = len(img_base64) / 1024
            log_progress(f"Image created: {img_size_kb:.1f} KB (base64)", log_file)
            
            # Call LLM API
            log_progress(f"Calling OpenRouter API (Qwen-2.5-72b VL)...", log_file)
            extracted_text = call_openrouter_vision(img_base64, api_key, log_file=log_file)
            
            if extracted_text:
                output_lines.append(f"## Page {page_num + 1}\n\n")
                output_lines.append(extracted_text)
                output_lines.append("\n\n---\n\n")
                log_progress(f"Page {page_num + 1} processed successfully", log_file)
                
                # Save intermediate results every 5 pages
                if (page_num + 1) % 5 == 0:
                    output_content = ''.join(output_lines)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(output_content)
                    log_progress(f"Intermediate save: {page_num + 1} pages saved", log_file)
            else:
                output_lines.append(f"## Page {page_num + 1}\n\n")
                output_lines.append("*[Failed to extract text from this page]*\n\n")
                output_lines.append("---\n\n")
                log_progress(f"Page {page_num + 1} processing failed", log_file)
        
        # Close the PDF
        doc.close()
        log_progress("Closed PDF file", log_file)
        
        # Write final output to file
        output_content = ''.join(output_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        log_progress(f"\n{'='*60}", log_file)
        log_progress(f"✓ Processing completed successfully!", log_file)
        log_progress(f"✓ Output saved to: {output_path}", log_file)
        log_progress(f"✓ Total output size: {len(output_content)} characters", log_file)
        log_progress(f"{'='*60}", log_file)
        
        return True
        
    except Exception as e:
        log_progress(f"\n✗ Error occurred: {str(e)}", log_file)
        import traceback
        error_details = traceback.format_exc()
        log_progress(f"Traceback:\n{error_details}", log_file)
        return False

if __name__ == "__main__":
    import sys
    
    # Define paths
    pdf_path = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab4/PDFllm.md"
    log_file = "/Users/simonwang/Documents/Usage/ai7010/lab4/PDFllm_progress.log"
    
    # Load API key from central APIkey.md file
    try:
        api_key = load_api_key("openRouter")
        print(f"✓ API key loaded from APIkey.md")
    except Exception as e:
        print(f"✗ Error loading API key: {e}")
        return
    
    print("=" * 60)
    print("PDF OCR Script - LLM Vision Model (Qwen-2.5-72b VL)")
    print("=" * 60)
    print()
    
    # You can optionally limit pages for testing (e.g., max_pages=3)
    # For full PDF processing, set max_pages=None
    success = process_pdf_with_llm(pdf_path, output_path, api_key, log_file, max_pages=3)
    
    if success:
        print(f"\n✓ Processing complete!")
        print(f"✓ Output file: {output_path}")
        print(f"✓ Log file: {log_file}")
        sys.exit(0)
    else:
        print(f"\n✗ Processing failed. Check log file: {log_file}")
        sys.exit(1)
