#!/usr/bin/env python3
"""
Advanced OCR script with OpenCV preprocessing.
Processes pages 25-27 with multiple enhancement techniques.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
import io
import sys
import os
from datetime import datetime

def preprocess_method_1_otsu(img_array):
    """Otsu's binarization method"""
    print("      • Otsu's thresholding...")
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(img_array, (5, 5), 0)
    # Otsu's thresholding
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def preprocess_method_2_adaptive(img_array):
    """Adaptive thresholding method"""
    print("      • Adaptive thresholding...")
    # Denoise
    denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
    # Adaptive threshold
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 21, 10
    )
    return binary

def preprocess_method_3_morphology(img_array):
    """Morphological operations to clean up"""
    print("      • Morphological processing...")
    # Denoise
    denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
    # Otsu
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Morphological operations to remove small noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    return cleaned

def preprocess_method_4_sauvola(img_array):
    """Sauvola binarization - good for degraded documents"""
    print("      • Sauvola thresholding (for degraded docs)...")
    # Denoise first
    denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
    # Use adaptive threshold as approximation
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 15, 8
    )
    return binary

def ocr_with_method(img_array, method_name, method_func, lang='chi_tra+eng'):
    """Apply a preprocessing method and run OCR"""
    try:
        processed = method_func(img_array)
        # Convert back to PIL Image
        pil_img = Image.fromarray(processed)
        
        # Run OCR with optimized config
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(pil_img, lang=lang, config=custom_config)
        
        char_count = len(text.strip())
        return text, char_count, processed
    except Exception as e:
        print(f"        ✗ Error with {method_name}: {str(e)}")
        return "", 0, img_array

def ocr_pages_advanced(pdf_path, output_path, start_page=25, num_pages=3):
    """
    Extract and OCR specified pages with advanced preprocessing.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to the output markdown file
        start_page: Starting page number (1-indexed)
        num_pages: Number of pages to process
    """
    print(f"Opening PDF: {os.path.basename(pdf_path)}")
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Convert to 0-indexed
        start_idx = start_page - 1
        end_idx = min(start_idx + num_pages, total_pages)
        pages_to_process = end_idx - start_idx
        
        print(f"Total pages in PDF: {total_pages}")
        print(f"Processing pages {start_page} to {start_page + pages_to_process - 1}...\n")
        
        # Prepare output
        output_lines = []
        output_lines.append(f"# OCR Output from {os.path.basename(pdf_path)}\n\n")
        output_lines.append(f"**Pages {start_page}-{start_page + pages_to_process - 1}**\n\n")
        output_lines.append(f"*Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        for page_idx in range(start_idx, end_idx):
            page_display_num = page_idx + 1
            print(f"\n{'='*70}")
            print(f"Page {page_display_num} (Page {page_idx - start_idx + 1} of {pages_to_process})")
            print(f"{'='*70}")
            
            page = doc[page_idx]
            output_lines.append(f"## Page {page_display_num}\n\n")
            
            # First, check for embedded text
            print("  Checking for embedded text layer...")
            text_direct = page.get_text("text")
            
            if len(text_direct.strip()) > 100:
                print(f"  ✓ Found embedded text: {len(text_direct)} characters")
                print("  → Using direct extraction (no OCR needed)")
                output_lines.append(text_direct)
                output_lines.append("\n\n---\n\n")
                continue
            
            # No embedded text - perform OCR
            print(f"  → No substantial text layer found, performing OCR...")
            
            # Render at high DPI
            print("  Step 1: Rendering page at 300 DPI...")
            mat = fitz.Matrix(4.17, 4.17)  # 300 DPI
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to numpy array via PIL
            img_data = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_img.convert('L'))
            
            print(f"  Image size: {img_array.shape[1]}x{img_array.shape[0]} pixels")
            
            # Try multiple preprocessing methods
            print("\n  Step 2: Trying multiple preprocessing methods...")
            
            methods = [
                ("Otsu Binarization", preprocess_method_1_otsu),
                ("Adaptive Threshold", preprocess_method_2_adaptive),
                ("Morphological Cleanup", preprocess_method_3_morphology),
                ("Sauvola Method", preprocess_method_4_sauvola),
            ]
            
            best_text = ""
            best_count = 0
            best_method = None
            best_img = None
            
            for method_name, method_func in methods:
                print(f"    Testing: {method_name}")
                text, count, processed_img = ocr_with_method(img_array, method_name, method_func)
                print(f"        → Extracted {count} characters")
                
                if count > best_count:
                    best_count = count
                    best_text = text
                    best_method = method_name
                    best_img = processed_img
            
            print(f"\n  Step 3: Best method = {best_method} ({best_count} characters)")
            
            # Save debug image of best method
            debug_path = os.path.join(
                os.path.dirname(output_path),
                f'debug_page{page_display_num}_best.png'
            )
            cv2.imwrite(debug_path, best_img)
            print(f"  Debug image saved: {debug_path}")
            
            # If still poor results, try with simplified Chinese
            if best_count < 50:
                print("\n  Step 4: Trying Simplified Chinese...")
                text_sim, count_sim, _ = ocr_with_method(
                    img_array, "Best method + chi_sim", 
                    methods[2][1],  # Use morphological
                    lang='chi_sim+eng'
                )
                if count_sim > best_count:
                    print(f"        → Better result: {count_sim} characters")
                    best_text = text_sim
                    best_count = count_sim
            
            # Add to output
            if best_text.strip():
                print(f"  ✓ Final output: {best_count} characters\n")
                output_lines.append(best_text)
            else:
                print(f"  ! No readable text extracted\n")
                output_lines.append("*[Unable to extract readable text from this page]*\n")
            
            output_lines.append("\n\n---\n\n")
        
        doc.close()
        
        # Write output
        output_content = ''.join(output_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n{'='*70}")
        print(f"✓ OCR Processing Complete!")
        print(f"✓ Output: {output_path}")
        print(f"✓ Total size: {len(output_content)} characters")
        print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    pdf_path = "/Users/simonwang/Documents/Usage/ai7010/data/NLC416-15jh007924-99162_基督教全國大會報告書.pdf"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/3pagesPy.md"
    
    print("\n" + "="*70)
    print("Advanced OCR - Pages 25-27")
    print("Testing Multiple Preprocessing Methods")
    print("="*70 + "\n")
    
    # Process pages 25-27
    success = ocr_pages_advanced(pdf_path, output_path, start_page=25, num_pages=3)
    
    if success:
        print("Next step: Review the output in 3pagesPy.md")
    
    sys.exit(0 if success else 1)

