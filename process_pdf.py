#!/usr/bin/env python3
"""
Script to split a PDF file into individual files based on table of contents.
"""

import sys
import os
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not installed. Install with: pip install PyMuPDF")
    sys.exit(1)


def extract_toc(pdf_path):
    """Extract table of contents from PDF."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    doc.close()
    return toc


def split_pdf_by_toc(pdf_path, output_dir, toc):
    """
    Split PDF into individual files based on table of contents.
    
    Args:
        pdf_path: Path to input PDF file
        output_dir: Directory to save output files
        toc: Table of contents list from PDF
    """
    doc = fitz.open(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing PDF: {pdf_path}")
    print(f"Found {len(toc)} ToC entries")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Process each ToC entry
    for i, entry in enumerate(toc):
        level, title, page_num = entry
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        if not safe_title:
            safe_title = f"Section_{i+1}"
        
        # Determine page range
        start_page = page_num - 1  # PyMuPDF uses 0-based indexing
        
        # Find end page (next entry's start page or end of document)
        if i + 1 < len(toc):
            end_page = toc[i + 1][2] - 1
        else:
            end_page = len(doc) - 1
        
        # Create new PDF for this section
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
        
        # Save the file
        output_file = output_path / f"{i+1:02d}_{safe_title}.pdf"
        new_doc.save(str(output_file))
        new_doc.close()
        
        print(f"Created: {output_file.name} (pages {start_page+1}-{end_page+1}, level {level})")
    
    doc.close()
    print("-" * 50)
    print(f"Successfully created {len(toc)} files in {output_dir}")


def main():
    """Main function."""
    input_pdf = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/SummarizeSynthesize/IndividualFiles"
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF not found: {input_pdf}")
        sys.exit(1)
    
    print("Extracting table of contents...")
    toc = extract_toc(input_pdf)
    
    if not toc:
        print("Warning: No table of contents found in PDF.")
        print("Attempting to extract from document structure...")
        # Fallback: try to extract from document outline
        doc = fitz.open(input_pdf)
        toc = doc.get_toc()
        doc.close()
        
        if not toc:
            print("Error: Could not extract table of contents.")
            sys.exit(1)
    
    print(f"Found {len(toc)} ToC entries:")
    for i, entry in enumerate(toc):
        level, title, page = entry
        indent = "  " * (level - 1)
        print(f"{indent}{i+1}. {title} (page {page})")
    print()
    
    split_pdf_by_toc(input_pdf, output_dir, toc)


if __name__ == "__main__":
    main()



