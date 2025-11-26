#!/usr/bin/env python3
"""
LLM-based OCR script for pages 4-50 of a PDF file.
Uses OpenRouter API with Qwen-2.5-72b VL vision model.
"""

import fitz  # PyMuPDF
from PIL import Image
import io
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

def call_openrouter_vision(image_base64, api_key, log_file="progress.log"):
    """
    Call OpenRouter API with Qwen-2.5-72b VL model to process an image.
    
    Args:
        image_base64: Base64-encoded image
        api_key: OpenRouter API key
        log_file: Path to log file
    
    Returns:
        Extracted text from the LLM
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Construct the request payload
    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct",  # Vision model
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please extract and transcribe ALL text from this image. This appears to be a Chinese document. Preserve the layout and structure as much as possible. Return the text in markdown format."
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

def process_pdf_with_llm(pdf_path, output_path, log_file="progress.log", start_page=4, end_page=50):
    """
    Process pages 4-50 of a PDF using LLM vision model.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to the output markdown file
        log_file: Path to the log file
        start_page: Starting page number (1-based, default 4)
        end_page: Ending page number (1-based, default 50)
    """
    # Clear/initialize log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\n")
        f.write(f"LLM OCR Processing Log - Pages {start_page}-{end_page}\n")
        f.write(f"{'='*60}\n\n")
    
    log_progress(f"Starting LLM OCR processing", log_file)
    log_progress(f"Input PDF: {pdf_path}", log_file)
    log_progress(f"Output file: {output_path}", log_file)
    log_progress(f"Page range: {start_page}-{end_page}", log_file)
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        log_progress("ERROR: OPENROUTER_API_KEY not found in environment variables", log_file)
        log_progress("Please ensure .env file contains OPENROUTER_API_KEY=your_key_here", log_file)
        return False
    
    log_progress(f"API key loaded successfully", log_file)
    
    try:
        # Open the PDF
        log_progress(f"Opening PDF file...", log_file)
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Convert to 0-based indexing
        start_idx = start_page - 1
        end_idx = min(end_page, total_pages)
        pages_to_process = end_idx - start_idx
        
        log_progress(f"Total pages in PDF: {total_pages}", log_file)
        log_progress(f"Processing pages {start_page}-{end_idx} ({pages_to_process} pages)", log_file)
        
        # Prepare output content
        output_lines = []
        output_lines.append(f"# LLM OCR Output from {os.path.basename(pdf_path)}\n\n")
        output_lines.append(f"**Extracted from Pages {start_page}-{end_idx} using Qwen-2.5-72b VL**\n\n")
        output_lines.append(f"*Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        output_lines.append("---\n\n")
        
        # Process each page
        for page_idx in range(start_idx, end_idx):
            page_number = page_idx + 1
            current_progress = page_idx - start_idx + 1
            
            log_progress(f"\n{'='*50}", log_file)
            log_progress(f"Processing Page {page_number} ({current_progress}/{pages_to_process})", log_file)
            log_progress(f"{'='*50}", log_file)
            
            page = doc[page_idx]
            
            # Convert page to base64 image
            log_progress(f"Converting page {page_number} to image...", log_file)
            img_base64 = pdf_page_to_base64(page, dpi=200)
            img_size_kb = len(img_base64) / 1024
            log_progress(f"Image created: {img_size_kb:.1f} KB (base64)", log_file)
            
            # Call LLM API
            log_progress(f"Calling OpenRouter API (Qwen-2.5-72b VL)...", log_file)
            extracted_text = call_openrouter_vision(img_base64, api_key, log_file)
            
            if extracted_text:
                output_lines.append(f"## Page {page_number}\n\n")
                output_lines.append(extracted_text)
                output_lines.append("\n\n---\n\n")
                log_progress(f"Page {page_number} processed successfully", log_file)
            else:
                output_lines.append(f"## Page {page_number}\n\n")
                output_lines.append("*[Failed to extract text from this page]*\n\n")
                output_lines.append("---\n\n")
                log_progress(f"Page {page_number} processing failed", log_file)
            
            # Write intermediate results every 10 pages
            if current_progress % 10 == 0:
                output_content = ''.join(output_lines)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                log_progress(f"Intermediate save: {current_progress}/{pages_to_process} pages completed", log_file)
        
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
        log_progress(f"✓ Total pages processed: {pages_to_process}", log_file)
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
    pdf_path = "/Users/simonwang/Documents/Usage/ai7010/data/NLC416-15jh007924-99162_基督教全國大會報告書.pdf"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/llm_ocr/50pagesLLM.md"
    log_file = "/Users/simonwang/Documents/Usage/ai7010/lab3/llm_ocr/llm_ocr_50pages_progress.log"
    
    print("=" * 60)
    print("PDF OCR Script - LLM Vision Model (Qwen-2.5-72b VL)")
    print("Pages 4-50 (47 pages)")
    print("=" * 60)
    print()
    
    success = process_pdf_with_llm(pdf_path, output_path, log_file, start_page=4, end_page=50)
    
    if success:
        print(f"\n✓ Processing complete!")
        print(f"✓ Output file: {output_path}")
        print(f"✓ Log file: {log_file}")
        sys.exit(0)
    else:
        print(f"\n✗ Processing failed. Check log file: {log_file}")
        sys.exit(1)


