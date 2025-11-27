# Direct execution script
import sys
import os
from pathlib import Path

script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 70)
print("Lab 2: Executing all scripts")
print("=" * 70)

# Run PDF to Markdown
print("\n[1/2] PDF to Markdown conversion...")
sys.path.insert(0, str(script_dir))
import importlib.util
spec = importlib.util.spec_from_file_location("pdf_to_markdown", script_dir / "pdf_to_markdown.py")
pdf_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdf_module)
pdf_module.main()

# Run OCR
print("\n[2/2] OCR ToC extraction...")
spec = importlib.util.spec_from_file_location("ocr_toc", script_dir / "ocr_toc.py")
ocr_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ocr_module)
ocr_module.main()

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
        print("⚠ No files generated")
print("=" * 70)







