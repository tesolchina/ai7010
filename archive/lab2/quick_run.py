#!/usr/bin/env python3
"""Quick runner - imports and executes directly."""

import sys
import os
from pathlib import Path

# Setup
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Lab 2: Running all scripts")
print("=" * 70)

# Import and run PDF to Markdown
print("\n[1/2] PDF to Markdown...")
try:
    import pdf_to_markdown
    pdf_to_markdown.main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Import and run OCR
print("\n[2/2] OCR ToC extraction...")
try:
    import ocr_toc
    ocr_toc.main()
except Exception as e:
    print(f"Error: {e}")
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
            print(f"   {f.name}")
    else:
        print("⚠ No files generated")
else:
    print("⚠ Output directory not found")

print("=" * 70)







