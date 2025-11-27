# Lab 2: PDF Processing and OCR

This directory contains programs to:
1. Convert PDF to Markdown format preserving all content
2. OCR the Table of Contents image and extract ToC entries

## Files

- `pdf_to_markdown.py` - Converts PDF to Markdown format
- `ocr_toc.py` - OCRs the ToC image and extracts table of contents
- `run_all.py` - Runs both processes in sequence

## Requirements

### Python Packages
```bash
pip install PyMuPDF Pillow pytesseract
```

### System Dependencies

**Tesseract OCR** (required for OCR functionality):

- **macOS:**
  ```bash
  brew install tesseract
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt-get install tesseract-ocr
  ```

- **Windows:**
  Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Usage

### Quick Start (Install and Run):
```bash
cd lab2
python3 install_and_run.py
```

This will:
1. Install all required Python packages
2. Check for Tesseract OCR
3. Convert PDF to Markdown
4. Extract ToC via OCR

### Run both processes manually:
```bash
python3 run_all.py
```

### Run individually:

**Convert PDF to Markdown:**
```bash
python3 pdf_to_markdown.py
```

**OCR ToC Image:**
```bash
python3 ocr_toc.py
```

## Output

All output files are saved to `Files/` directory:

- `bulletin-144-min may2024.md` - Markdown version of the PDF
- `1764054472243_toc.json` - ToC entries in JSON format
- `1764054472243_toc.txt` - ToC entries in text format

## Notes

- The PDF to Markdown converter preserves text formatting (bold, italic) and structure
- The OCR program extracts ToC entries with page numbers and hierarchy levels
- If OCR fails, the program falls back to a refined ToC structure based on image analysis

