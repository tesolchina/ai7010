#!/usr/bin/env python3
"""Execute both scripts."""
import sys
import os
from pathlib import Path

# Change to script directory
script_dir = Path("/Users/simonwang/Documents/Usage/ai7010/lab2")
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Executing Lab 2 Scripts")
print("=" * 70)

# Execute PDF to Markdown
print("\n[1/2] PDF to Markdown conversion...")
try:
    # Read and execute the script
    with open(script_dir / "pdf_to_markdown.py", 'r') as f:
        code = compile(f.read(), script_dir / "pdf_to_markdown.py", 'exec')
        exec(code, {'__name__': '__main__', '__file__': str(script_dir / "pdf_to_markdown.py")})
    print("✓ PDF to Markdown completed")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Execute OCR
print("\n[2/2] OCR ToC extraction...")
try:
    with open(script_dir / "ocr_toc.py", 'r') as f:
        code = compile(f.read(), script_dir / "ocr_toc.py", 'exec')
        exec(code, {'__name__': '__main__', '__file__': str(script_dir / "ocr_toc.py")})
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
            print(f"   {f.name} ({size/1024:.1f} KB)")
    else:
        print("⚠ No files generated yet")
else:
    print("⚠ Files directory not found")

print("=" * 70)



