#!/bin/bash
# Installation and execution script for Lab 2

set -e

echo "=========================================="
echo "Lab 2: PDF Processing and OCR"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

echo "Step 1: Installing Python packages..."
python3 -m pip install --quiet --upgrade Pillow pytesseract PyMuPDF

echo ""
echo "Step 2: Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract OCR is installed"
    tesseract --version | head -1
else
    echo "⚠ Tesseract OCR not found"
    echo "  Please install Tesseract OCR:"
    echo "    macOS: brew install tesseract"
    echo "    Linux: sudo apt-get install tesseract-ocr"
    echo ""
    echo "  Continuing without OCR functionality..."
fi

echo ""
echo "Step 3: Running PDF to Markdown conversion..."
python3 pdf_to_markdown.py

echo ""
echo "Step 4: Running OCR ToC extraction..."
if command -v tesseract &> /dev/null; then
    python3 ocr_toc.py
else
    echo "⚠ Skipping OCR (Tesseract not installed)"
fi

echo ""
echo "=========================================="
echo "✅ Processing complete!"
echo "=========================================="
echo ""
echo "Output files are in: Files/"
ls -lh Files/ 2>/dev/null || echo "No files found in Files/"



