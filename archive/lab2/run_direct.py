#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Set up paths
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Executing Lab 2 scripts...")
print("=" * 70)

# Execute PDF to Markdown
print("\n[1/2] Converting PDF to Markdown...")
exec(open('pdf_to_markdown.py').read())

# Execute OCR
print("\n[2/2] Extracting ToC via OCR...")
exec(open('ocr_toc.py').read())

# Show results
files_dir = script_dir / "Files"
if files_dir.exists():
    files = list(files_dir.glob("*"))
    if files:
        print(f"\n✅ Output files in {files_dir}:")
        for f in sorted(files):
            print(f"   - {f.name}")

print("\n✅ Complete!")







