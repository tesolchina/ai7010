#!/usr/bin/env python3
"""Execute scripts now."""
import sys
import os
from pathlib import Path

# Setup
script_dir = Path("/Users/simonwang/Documents/Usage/ai7010/lab2")
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Lab 2: Executing all scripts")
print("=" * 70)
print(f"Working directory: {os.getcwd()}")

# Run PDF to Markdown
print("\n[1/2] Converting PDF to Markdown...")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("pdf_to_markdown", script_dir / "pdf_to_markdown.py")
    pdf_module = importlib.util.module_from_spec(spec)
    sys.modules["pdf_to_markdown"] = pdf_module
    spec.loader.exec_module(pdf_module)
    pdf_module.main()
    print("✓ PDF to Markdown completed")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Run OCR
print("\n[2/2] Extracting ToC via OCR...")
try:
    spec = importlib.util.spec_from_file_location("ocr_toc", script_dir / "ocr_toc.py")
    ocr_module = importlib.util.module_from_spec(spec)
    sys.modules["ocr_toc"] = ocr_module
    spec.loader.exec_module(ocr_module)
    ocr_module.main()
    print("✓ OCR ToC extraction completed")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Show results
print("\n" + "=" * 70)
files_dir = script_dir / "Files"
if files_dir.exists():
    files = sorted(files_dir.glob("*"))
    if files:
        print(f"✅ Generated {len(files)} files:")
        for f in files:
            size = f.stat().st_size
            size_str = f"{size/1024:.1f} KB" if size > 1024 else f"{size} B"
            print(f"   ✓ {f.name} ({size_str})")
    else:
        print("⚠ No files found in Files/")
else:
    print(f"⚠ Output directory {files_dir} not found")

print("=" * 70)
print("✅ Complete!")



