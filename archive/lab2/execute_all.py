#!/usr/bin/env python3
"""
Execute all scripts directly without subprocess.
"""

import sys
import os
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Lab 2: PDF Processing and OCR - Execution")
print("=" * 70)
print(f"\nWorking directory: {os.getcwd()}")

# Step 1: Install packages (try to import first)
print("\n" + "=" * 70)
print("Step 1: Checking dependencies...")
print("=" * 70)

missing_packages = []
for package in ["PIL", "pytesseract", "fitz"]:
    try:
        if package == "PIL":
            __import__("PIL")
        elif package == "pytesseract":
            __import__("pytesseract")
        elif package == "fitz":
            __import__("fitz")
        print(f"✓ {package} is available")
    except ImportError:
        print(f"✗ {package} is missing")
        missing_packages.append(package)

if missing_packages:
    print(f"\n⚠ Missing packages: {missing_packages}")
    print("  Please install with: pip install Pillow pytesseract PyMuPDF")

# Step 2: Run PDF to Markdown
print("\n" + "=" * 70)
print("Step 2: Running PDF to Markdown conversion...")
print("=" * 70)

try:
    from pdf_to_markdown import main as pdf_main
    pdf_main()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Run OCR
print("\n" + "=" * 70)
print("Step 3: Running OCR ToC extraction...")
print("=" * 70)

try:
    from ocr_toc import main as ocr_main
    ocr_main()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Show results
print("\n" + "=" * 70)
print("Step 4: Results")
print("=" * 70)

files_dir = script_dir / "Files"
if files_dir.exists():
    files = list(files_dir.glob("*"))
    if files:
        print(f"\nOutput files in {files_dir}:")
        for f in sorted(files):
            size = f.stat().st_size
            size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
            print(f"  ✓ {f.name} ({size_str})")
    else:
        print("\n  (no files found)")
else:
    print(f"\n⚠ Output directory {files_dir} not found")

print("\n" + "=" * 70)
print("✅ Processing complete!")
print("=" * 70)







