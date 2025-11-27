#!/usr/bin/env python3
"""
Final OCR script with advanced image preprocessing for poor quality scans.
Handles degraded documents with noise reduction and adaptive thresholding.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import sys
import os
import numpy as np
from datetime import datetime

def advanced_preprocess(image):
    """
    Advanced preprocessing for poor quality scanned documents.
    """
    print("    - Converting to grayscale...")
    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')
    
    # Convert to numpy array for advanced processing
    img_array = np.array(image)
    
    print("    - Applying noise reduction...")
    # Convert back to PIL for filtering
    img = Image.fromarray(img_array)
    
    # Apply median filter to remove salt-and-pepper noise
    img = img.filter(ImageFilter.MedianFilter(size=3))
    
    print("    - Enhancing contrast...")
    # Moderate contrast enhancement (not too much)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    print("    - Applying adaptive binarization...")
    # Auto contrast to normalize brightness
    img = ImageOps.autocontrast(img, cutoff=2)
    
    return img

def ocr_first_3_pages(pdf_path, output_path):
    """
    Extract and OCR the first 3 pages from a PDF file.
    """
    print(f"Opening PDF: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_process = min(3, total_pages)
        
        print(f"Total pages in PDF: {total_pages}")
        print(f"Processing first {pages_to_process} pages...\n")
        
        # Prepare output
        output_lines = []
        output_lines.append(f"# OCR Output from {os.path.basename(pdf_path)}\n\n")
        output_lines.append(f"**Extracted from First 3 Pages**\n\n")
        output_lines.append(f"*Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        output_lines.append(f"*Note: This is a scanned document. OCR quality depends on scan quality.*\n\n")
        
        for page_num in range(pages_to_process):
            print(f"{'='*60}")
            print(f"Page {page_num + 1}/{pages_to_process}")
            print(f"{'='*60}")
            
            page = doc[page_num]
            output_lines.append(f"## Page {page_num + 1}\n\n")
            
            # Check for embedded text
            text_direct = page.get_text("text")
            
            if len(text_direct.strip()) > 100:
                print(f"✓ Found embedded text: {len(text_direct)} characters")
                output_lines.append(text_direct)
                output_lines.append("\n\n---\n\n")
                continue
            
            # Perform OCR
            print("Performing OCR (this may take 30-60 seconds)...")
            print("  Image rendering...")
            
            # High resolution for better OCR (300 DPI equivalent)
            mat = fitz.Matrix(4.17, 4.17)  # 72 * 4.17 ≈ 300 DPI
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            print(f"  Image size: {img.size[0]}x{img.size[1]} pixels")
            
            # Preprocess image
            print("  Preprocessing for OCR...")
            img_processed = advanced_preprocess(img)
            
            # Save debug images
            debug_dir = os.path.dirname(output_path)
            debug_path = os.path.join(debug_dir, f'debug_page{page_num + 1}_processed.png')
            img_processed.save(debug_path)
            print(f"  Debug image saved: {debug_path}")
            
            print("  Running Tesseract OCR...")
            print("    (Using Traditional Chinese + English)")
            
            # Try vertical text mode for traditional Chinese documents
            # PSM 6 = Assume a single uniform block of text
            # PSM 5 = Assume a single uniform block of vertically aligned text
            custom_config = r'--oem 3 --psm 6'
            
            ocr_text = pytesseract.image_to_string(
                img_processed,
                lang='chi_tra+eng',
                config=custom_config
            )
            
            if not ocr_text.strip():
                # Try simplified Chinese if traditional didn't work
                print("    Trying Simplified Chinese...")
                ocr_text = pytesseract.image_to_string(
                    img_processed,
                    lang='chi_sim+eng',
                    config=custom_config
                )
            
            if ocr_text.strip():
                print(f"  ✓ OCR completed: {len(ocr_text)} characters extracted")
                output_lines.append(ocr_text)
            else:
                print(f"  ! Warning: No text detected")
                output_lines.append("*[No readable text could be extracted from this page]*\n")
            
            output_lines.append("\n\n---\n\n")
        
        doc.close()
        
        # Write output
        output_content = ''.join(output_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n{'='*60}")
        print(f"✓ Processing completed!")
        print(f"✓ Output saved to: {output_path}")
        print(f"✓ Total characters: {len(output_content)}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    pdf_path = "/Users/simonwang/Documents/Usage/ai7010/data/NLC416-15jh007924-99162_基督教全國大會報告書.pdf"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/3pagesPy.md"
    
    print("\n" + "="*60)
    print("PDF OCR - First 3 Pages (Advanced Processing)")
    print("="*60 + "\n")
    
    success = ocr_first_3_pages(pdf_path, output_path)
    sys.exit(0 if success else 1)

