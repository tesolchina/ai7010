#!/usr/bin/env python3
"""
Improved OCR script for the first 3 pages of a PDF file.
Tries multiple extraction methods to ensure readable output.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import sys

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy.
    """
    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)
    
    return image

def ocr_first_3_pages(pdf_path, output_path):
    """
    Extract and OCR the first 3 pages from a PDF file using multiple methods.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to the output markdown file
    """
    print(f"Opening PDF: {pdf_path}")
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_process = min(3, total_pages)
        
        print(f"Total pages in PDF: {total_pages}")
        print(f"Processing first {pages_to_process} pages...")
        
        # Prepare output content
        output_lines = []
        output_lines.append(f"# OCR Output from {os.path.basename(pdf_path)}\n\n")
        output_lines.append(f"**Extracted from First 3 Pages**\n\n")
        output_lines.append(f"*Processing Date: {import_datetime()}*\n\n")
        
        for page_num in range(pages_to_process):
            print(f"\n{'='*50}")
            print(f"Processing Page {page_num + 1}/{pages_to_process}")
            print(f"{'='*50}")
            
            page = doc[page_num]
            output_lines.append(f"## Page {page_num + 1}\n\n")
            
            # Method 1: Try direct text extraction
            print("Method 1: Direct text extraction...")
            text_direct = page.get_text("text", sort=True)
            char_count = len(text_direct.strip())
            print(f"  → Extracted {char_count} characters")
            
            # Method 2: Try with different extraction mode
            print("Method 2: Block-based text extraction...")
            text_blocks = page.get_text("blocks", sort=True)
            text_from_blocks = "\n".join([block[4] for block in text_blocks if len(block) > 4])
            block_char_count = len(text_from_blocks.strip())
            print(f"  → Extracted {block_char_count} characters")
            
            # Choose the best direct extraction
            best_text = text_from_blocks if block_char_count > char_count else text_direct
            
            if len(best_text.strip()) > 100:  # Substantial text found
                print(f"  ✓ Using direct extraction ({len(best_text)} characters)")
                output_lines.append(best_text)
                output_lines.append("\n\n---\n\n")
            else:
                # Method 3: OCR with image preprocessing
                print("Method 3: OCR with enhanced image...")
                print("  - Converting page to high-res image...")
                
                # Use higher DPI for better OCR
                mat = fitz.Matrix(3.0, 3.0)  # 3x zoom = ~216 DPI
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                print(f"  - Image size: {img.size[0]}x{img.size[1]} pixels")
                print(f"  - Preprocessing image for better OCR...")
                
                # Preprocess for better OCR
                img_processed = preprocess_image(img)
                
                # Save debug image for first page
                if page_num == 0:
                    debug_path = output_path.replace('.md', '_debug_page1.png')
                    img_processed.save(debug_path)
                    print(f"  - Debug image saved to: {debug_path}")
                
                print(f"  - Running Tesseract OCR (this may take 30-60 seconds per page)...")
                
                # Configure Tesseract for better Chinese recognition
                custom_config = r'--oem 3 --psm 6'
                
                # Try Traditional Chinese first (since filename suggests it's a traditional document)
                ocr_text = pytesseract.image_to_string(
                    img_processed,
                    lang='chi_tra+eng',
                    config=custom_config
                )
                
                if ocr_text.strip():
                    print(f"  ✓ OCR completed: {len(ocr_text)} characters")
                    output_lines.append(ocr_text)
                    output_lines.append("\n\n---\n\n")
                else:
                    print(f"  ! Warning: No text detected")
                    output_lines.append("*[No text detected on this page]*\n\n---\n\n")
        
        # Close the PDF
        doc.close()
        
        # Write output to file
        output_content = ''.join(output_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n{'='*50}")
        print(f"✓ Processing completed successfully!")
        print(f"✓ Output saved to: {output_path}")
        print(f"✓ Total output size: {len(output_content)} characters")
        print(f"{'='*50}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def import_datetime():
    """Helper to get current datetime string"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    import os
    
    # Define paths
    pdf_path = "/Users/simonwang/Documents/Usage/ai7010/data/NLC416-15jh007924-99162_基督教全國大會報告書.pdf"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/3pagesPy.md"
    
    print("=" * 60)
    print("PDF OCR Script - First 3 Pages (Improved)")
    print("=" * 60)
    print()
    
    success = ocr_first_3_pages(pdf_path, output_path)
    
    if success:
        print("\nYou can now view the output file: 3pagesPy.md")
        sys.exit(0)
    else:
        sys.exit(1)

