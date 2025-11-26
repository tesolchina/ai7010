#!/usr/bin/env python3
"""
Install dependencies and run both PDF to Markdown and OCR programs.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a shell command."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Warning: {result.stderr}", file=sys.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    result = subprocess.run(
        "which tesseract",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        # Get version
        version_result = subprocess.run(
            "tesseract --version",
            shell=True,
            capture_output=True,
            text=True
        )
        if version_result.returncode == 0:
            version_line = version_result.stdout.split('\n')[0]
            print(f"✓ Tesseract OCR found: {version_line}")
        return True
    else:
        print("⚠ Tesseract OCR not found in PATH")
        print("  Please install Tesseract OCR:")
        print("    macOS: brew install tesseract")
        print("    Linux: sudo apt-get install tesseract-ocr")
        return False


def main():
    """Main installation and execution function."""
    print("=" * 70)
    print("Lab 2: PDF Processing and OCR - Installation & Execution")
    print("=" * 70)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"\nWorking directory: {os.getcwd()}")
    
    # Step 1: Install Python packages
    print("\n" + "=" * 70)
    print("Step 1: Installing Python packages...")
    print("=" * 70)
    
    packages = ["Pillow", "pytesseract", "PyMuPDF"]
    for package in packages:
        print(f"\nInstalling {package}...")
        success = run_command(
            f"{sys.executable} -m pip install --quiet --upgrade {package}",
            f"Installing {package}",
            check=False
        )
        if success:
            print(f"✓ {package} installed successfully")
        else:
            print(f"⚠ Warning: {package} installation had issues")
    
    # Step 2: Check Tesseract
    print("\n" + "=" * 70)
    print("Step 2: Checking Tesseract OCR...")
    print("=" * 70)
    tesseract_available = check_tesseract()
    
    # Step 3: Run PDF to Markdown
    print("\n" + "=" * 70)
    print("Step 3: Running PDF to Markdown conversion...")
    print("=" * 70)
    
    pdf_script = script_dir / "pdf_to_markdown.py"
    if not pdf_script.exists():
        print(f"Error: pdf_to_markdown.py not found at {pdf_script}")
        return 1
    
    success = run_command(
        f"cd {script_dir} && {sys.executable} pdf_to_markdown.py",
        "Converting PDF to Markdown",
        check=False
    )
    
    if not success:
        print("⚠ PDF to Markdown conversion had issues")
    
    # Step 4: Run OCR
    print("\n" + "=" * 70)
    print("Step 4: Running OCR ToC extraction...")
    print("=" * 70)
    
    ocr_script = script_dir / "ocr_toc.py"
    if not ocr_script.exists():
        print(f"Error: ocr_toc.py not found at {ocr_script}")
        return 1
    
    if tesseract_available:
        success = run_command(
            f"cd {script_dir} && {sys.executable} ocr_toc.py",
            "Extracting ToC via OCR",
            check=False
        )
        if not success:
            print("⚠ OCR extraction had issues")
    else:
        print("⚠ Skipping OCR (Tesseract not installed)")
        print("  The program will use fallback ToC structure")
        # Try running anyway - it has fallback
        run_command(
            f"cd {script_dir} && {sys.executable} ocr_toc.py",
            "Extracting ToC (with fallback)",
            check=False
        )
    
    # Step 5: Show results
    print("\n" + "=" * 70)
    print("Step 5: Results")
    print("=" * 70)
    
    files_dir = script_dir / "Files"
    if files_dir.exists():
        print(f"\nOutput files in {files_dir.absolute()}:")
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
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

