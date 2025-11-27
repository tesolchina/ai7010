#!/usr/bin/env python3
"""Direct execution of both scripts."""
import sys
import os
from pathlib import Path

# Setup paths
script_dir = Path("/Users/simonwang/Documents/Usage/ai7010/lab2")
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Lab 2: Executing All Scripts")
print("=" * 70)
print(f"Working directory: {os.getcwd()}\n")

# Step 1: PDF to Markdown
print("[1/2] Converting PDF to Markdown...")
print("-" * 70)

try:
    import fitz
    
    input_pdf = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/lab2/Files"
    pdf_name = Path(input_pdf).stem
    output_md = os.path.join(output_dir, f"{pdf_name}.md")
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF not found: {input_pdf}")
    else:
        # Import the function
        from pdf_to_markdown import pdf_to_markdown
        pdf_to_markdown(input_pdf, output_md)
        print("✓ PDF to Markdown conversion completed\n")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 2: OCR ToC
print("\n[2/2] Extracting ToC via OCR...")
print("-" * 70)

try:
    from PIL import Image
    import pytesseract
    
    input_image = "/Users/simonwang/Documents/Usage/ai7010/lab1/image/1764054472243.png"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/lab2/Files"
    image_name = Path(input_image).stem
    output_file = os.path.join(output_dir, f"{image_name}_toc")
    
    if not os.path.exists(input_image):
        print(f"Error: Input image not found: {input_image}")
    else:
        from ocr_toc import ocr_toc_image
        ocr_toc_image(input_image, output_file)
        print("✓ OCR ToC extraction completed\n")
        
except ImportError as e:
    print(f"⚠ Missing dependencies: {e}")
    print("  Install with: pip install Pillow pytesseract")
    print("  Also install Tesseract: brew install tesseract")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Show results
print("\n" + "=" * 70)
print("Results")
print("=" * 70)

files_dir = script_dir / "Files"
if files_dir.exists():
    files = sorted(files_dir.glob("*"))
    if files:
        print(f"\n✅ Generated {len(files)} files:")
        for f in files:
            size = f.stat().st_size
            size_str = f"{size/1024:.1f} KB" if size > 1024 else f"{size} B"
            print(f"   ✓ {f.name} ({size_str})")
    else:
        print("\n⚠ No files found in Files/")
else:
    print(f"\n⚠ Output directory {files_dir} not found")

print("\n" + "=" * 70)
print("✅ Complete!")
print("=" * 70)







