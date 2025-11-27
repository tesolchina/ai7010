#!/usr/bin/env python3
"""
OCR the first 3 pages of a PDF file and save the output to a markdown file.
Uses PyMuPDF's built-in OCR capabilities with Tesseract.
"""

import fitz  # PyMuPDF
import sys
import os

def ocr_first_3_pages(pdf_path, output_path):
    """
    Extract and OCR the first 3 pages from a PDF file.
    
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
        output_lines.append(f"# OCR Output from {pdf_path.split('/')[-1]}\n\n")
        output_lines.append(f"**First 3 Pages**\n\n")
        
        for page_num in range(pages_to_process):
            print(f"\nProcessing page {page_num + 1}...")
            page = doc[page_num]
            
            output_lines.append(f"## Page {page_num + 1}\n\n")
            
            # Method 1: Try to extract text directly first (fastest)
            text = page.get_text("text", sort=True)
            
            if text.strip() and len(text.strip()) > 50:  # If we get substantial text
                print(f"  - Extracted text directly (PDF has text layer): {len(text)} characters")
                output_lines.append(text)
                output_lines.append("\n\n---\n\n")
            else:
                # Method 2: Use PyMuPDF's built-in OCR via Tesseract
                print(f"  - No or minimal text layer found, performing OCR...")
                print(f"  - This may take a moment...")
                
                try:
                    # Get OCR text using PyMuPDF's textpage_ocr
                    # This uses Tesseract internally with better integration
                    tp = page.get_textpage_ocr(flags=0, language="chi_tra+chi_sim+eng", dpi=300)
                    ocr_text = page.get_text("text", textpage=tp, sort=True)
                    
                    if ocr_text.strip():
                        print(f"  - OCR completed: {len(ocr_text)} characters extracted")
                        output_lines.append(ocr_text)
                        output_lines.append("\n\n---\n\n")
                    else:
                        print(f"  - Warning: No text detected on this page")
                        output_lines.append("*[No text detected on this page]*\n\n---\n\n")
                        
                except Exception as ocr_error:
                    print(f"  - OCR error: {str(ocr_error)}")
                    print(f"  - Falling back to direct text extraction...")
                    # Fall back to whatever text we can get
                    if text.strip():
                        output_lines.append(text)
                    else:
                        output_lines.append("*[OCR failed - no text available]*\n\n")
                    output_lines.append("\n---\n\n")
        
        # Close the PDF
        doc.close()
        
        # Write output to file
        output_content = ''.join(output_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n✓ OCR completed successfully!")
        print(f"✓ Output saved to: {output_path}")
        print(f"✓ Total output size: {len(output_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Define paths
    pdf_path = "/Users/simonwang/Documents/Usage/ai7010/data/NLC416-15jh007924-99162_基督教全國大會報告書.pdf"
    output_path = "/Users/simonwang/Documents/Usage/ai7010/lab3/3pagesPy.md"
    
    print("=" * 60)
    print("PDF OCR Script - First 3 Pages")
    print("=" * 60)
    
    success = ocr_first_3_pages(pdf_path, output_path)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

