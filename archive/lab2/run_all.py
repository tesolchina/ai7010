#!/usr/bin/env python3
"""
Run both PDF to Markdown conversion and OCR ToC extraction.
"""

import sys
import os
from pathlib import Path

# Import our modules
try:
    from pdf_to_markdown import pdf_to_markdown
    from ocr_toc import ocr_toc_image
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure pdf_to_markdown.py and ocr_toc.py are in the same directory")
    sys.exit(1)


def main():
    """Run both conversion processes."""
    print("=" * 70)
    print("PDF Processing Pipeline")
    print("=" * 70)
    print()
    
    # Paths
    input_pdf = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    input_image = "/Users/simonwang/Documents/Usage/ai7010/lab1/image/1764054472243.png"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/lab2/Files"
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Convert PDF to Markdown
    print("\n" + "=" * 70)
    print("Step 1: Converting PDF to Markdown")
    print("=" * 70)
    try:
        pdf_name = Path(input_pdf).stem
        output_md = os.path.join(output_dir, f"{pdf_name}.md")
        pdf_to_markdown(input_pdf, output_md)
        print("✅ PDF to Markdown conversion completed\n")
    except Exception as e:
        print(f"❌ Error converting PDF to Markdown: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 2: OCR ToC image
    print("\n" + "=" * 70)
    print("Step 2: OCR ToC Image")
    print("=" * 70)
    try:
        image_name = Path(input_image).stem
        output_toc = os.path.join(output_dir, f"{image_name}_toc")
        ocr_toc_image(input_image, output_toc)
        print("✅ OCR ToC extraction completed\n")
    except Exception as e:
        print(f"❌ Error during OCR: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: Make sure Tesseract OCR is installed:")
        print("  macOS: brew install tesseract")
        print("  Linux: sudo apt-get install tesseract-ocr")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ All processing completed successfully!")
    print("=" * 70)
    print(f"\nOutput files are in: {output_dir}")
    print(f"  - Markdown: {pdf_name}.md")
    print(f"  - ToC JSON: {image_name}_toc.json")
    print(f"  - ToC Text: {image_name}_toc.txt")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())







