#!/usr/bin/env python3
"""
Simple runner that imports and executes the modules directly.
"""

import sys
import os
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

print("=" * 70)
print("Lab 2: PDF Processing and OCR - Installation & Execution")
print("=" * 70)
print(f"\nWorking directory: {os.getcwd()}")

# Step 1: Install Python packages
print("\n" + "=" * 70)
print("Step 1: Installing Python packages...")
print("=" * 70)

packages = ["Pillow", "pytesseract", "PyMuPDF"]
for package in packages:
    print(f"\nInstalling {package}...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", package],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {package} installed successfully")
        else:
            print(f"⚠ Warning: {package} installation had issues")
            if result.stderr:
                print(f"  {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠ Error installing {package}: {e}")

# Step 2: Check Tesseract
print("\n" + "=" * 70)
print("Step 2: Checking Tesseract OCR...")
print("=" * 70)

try:
    import subprocess
    result = subprocess.run(
        ["which", "tesseract"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        version_result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True
        )
        if version_result.returncode == 0:
            version_line = version_result.stdout.split('\n')[0]
            print(f"✓ Tesseract OCR found: {version_line}")
            tesseract_available = True
        else:
            tesseract_available = False
    else:
        print("⚠ Tesseract OCR not found in PATH")
        print("  Please install Tesseract OCR:")
        print("    macOS: brew install tesseract")
        print("    Linux: sudo apt-get install tesseract-ocr")
        tesseract_available = False
except Exception as e:
    print(f"⚠ Error checking Tesseract: {e}")
    tesseract_available = False

# Step 3: Run PDF to Markdown
print("\n" + "=" * 70)
print("Step 3: Running PDF to Markdown conversion...")
print("=" * 70)

try:
    # Import and run the module
    sys.path.insert(0, str(script_dir))
    from pdf_to_markdown import main as pdf_main
    pdf_main()
    print("✓ PDF to Markdown conversion completed")
except Exception as e:
    print(f"❌ Error converting PDF to Markdown: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Run OCR
print("\n" + "=" * 70)
print("Step 4: Running OCR ToC extraction...")
print("=" * 70)

if not tesseract_available:
    print("⚠ Tesseract not available, but continuing with fallback...")

try:
    # Import and run the module
    from ocr_toc import main as ocr_main
    ocr_main()
    print("✓ OCR ToC extraction completed")
except Exception as e:
    print(f"❌ Error during OCR: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Show results
print("\n" + "=" * 70)
print("Step 5: Results")
print("=" * 70)

files_dir = script_dir / "Files"
if files_dir.exists():
    print(f"\nOutput files in {files_dir}:")
    files = list(files_dir.glob("*"))
    if files:
        for f in sorted(files):
            size = f.stat().st_size
            size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
            print(f"  ✓ {f.name} ({size_str})")
    else:
        print("  (no files found)")
else:
    print(f"\n⚠ Output directory {files_dir} not found")

print("\n" + "=" * 70)
print("✅ Processing complete!")
print("=" * 70)



