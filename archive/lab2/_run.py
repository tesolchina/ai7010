#!/usr/bin/env python3
import sys
import os
import importlib.util
from pathlib import Path

script_dir = Path("/Users/simonwang/Documents/Usage/ai7010/lab2")
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Running Lab 2 Scripts")
print("=" * 70)

# Run PDF to Markdown
print("\n[1/2] PDF to Markdown...")
try:
    spec = importlib.util.spec_from_file_location("pdf_to_markdown", script_dir / "pdf_to_markdown.py")
    pdf_mod = importlib.util.module_from_spec(spec)
    sys.modules["pdf_to_markdown"] = pdf_mod
    spec.loader.exec_module(pdf_mod)
    pdf_mod.main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Run OCR
print("\n[2/2] OCR ToC...")
try:
    spec = importlib.util.spec_from_file_location("ocr_toc", script_dir / "ocr_toc.py")
    ocr_mod = importlib.util.module_from_spec(spec)
    sys.modules["ocr_toc"] = ocr_mod
    spec.loader.exec_module(ocr_mod)
    ocr_mod.main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Results
files_dir = script_dir / "Files"
if files_dir.exists():
    files = sorted(files_dir.glob("*"))
    if files:
        print(f"\n✅ Generated {len(files)} files:")
        for f in files:
            print(f"   {f.name}")
print("=" * 70)







