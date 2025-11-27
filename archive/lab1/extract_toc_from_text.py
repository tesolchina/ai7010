#!/usr/bin/env python3
"""
Script to extract table of contents from PDF text and split PDF accordingly.
"""

import sys
import os
import re
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not installed. Install with: pip install PyMuPDF")
    sys.exit(1)


def find_toc_page(doc):
    """Find the page containing the table of contents."""
    toc_keywords = ['table of contents', 'contents', 'table des matières']
    
    for page_num in range(min(10, len(doc))):  # Check first 10 pages
        page = doc[page_num]
        text = page.get_text().lower()
        
        for keyword in toc_keywords:
            if keyword in text:
                print(f"Found ToC on page {page_num + 1}")
                return page_num
    
    return None


def extract_toc_from_text(doc, toc_page_num):
    """Extract table of contents entries from text."""
    page = doc[toc_page_num]
    text = page.get_text()
    
    print(f"\nToC Page Text (first 2000 chars):")
    print(text[:2000])
    print("\n" + "="*50 + "\n")
    
    # Pattern to match ToC entries: title followed by page number
    # Common patterns:
    # - "Title ................ 5"
    # - "Title 5"
    # - "1. Title 5"
    
    lines = text.split('\n')
    toc_entries = []
    
    # Look for lines with page numbers at the end
    page_num_pattern = re.compile(r'(\d+)\s*$')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line ends with a page number
        match = page_num_pattern.search(line)
        if match:
            page_num = int(match.group(1))
            # Remove the page number and dots/leaders
            title = line[:match.start()].strip()
            title = re.sub(r'\.+', '', title).strip()
            
            if title and page_num > 0:
                # Try to determine level (indentation or numbering)
                level = 1
                if re.match(r'^\d+\.', title):
                    level = 1
                elif re.match(r'^\s+[a-z]', title, re.IGNORECASE):
                    level = 2
                
                toc_entries.append((level, title, page_num))
    
    return toc_entries


def split_pdf_by_toc(pdf_path, output_dir, toc):
    """Split PDF into individual files based on table of contents."""
    doc = fitz.open(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing PDF: {pdf_path}")
    print(f"Found {len(toc)} ToC entries")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Process each ToC entry
    for i, entry in enumerate(toc):
        if len(entry) == 3:
            level, title, page_num = entry
        else:
            # Handle different entry formats
            title = entry[0] if isinstance(entry[0], str) else str(entry[0])
            page_num = entry[-1] if isinstance(entry[-1], int) else 1
            level = 1
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        safe_title = safe_title[:50]  # Limit length
        if not safe_title:
            safe_title = f"Section_{i+1}"
        
        # Determine page range
        start_page = max(0, page_num - 1)  # PyMuPDF uses 0-based indexing
        
        # Find end page (next entry's start page or end of document)
        if i + 1 < len(toc):
            next_page_num = toc[i + 1][-1] if isinstance(toc[i + 1][-1], int) else len(doc)
            end_page = max(start_page, next_page_num - 1)
        else:
            end_page = len(doc) - 1
        
        # Ensure valid page range
        if start_page >= len(doc):
            print(f"Warning: Start page {start_page+1} exceeds document length. Skipping: {title}")
            continue
        
        end_page = min(end_page, len(doc) - 1)
        
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
    
    doc = fitz.open(input_pdf)
    
    print("Searching for table of contents...")
    toc_page = find_toc_page(doc)
    
    if toc_page is None:
        print("Could not find ToC page automatically.")
        print("Please check the image to see the ToC structure.")
        print("\nFirst few pages of the document:")
        for i in range(min(5, len(doc))):
            text = doc[i].get_text()[:500]
            print(f"\n--- Page {i+1} ---")
            print(text)
        doc.close()
        sys.exit(1)
    
    print(f"\nExtracting ToC from page {toc_page + 1}...")
    toc = extract_toc_from_text(doc, toc_page)
    doc.close()
    
    if not toc:
        print("Error: Could not extract table of contents from text.")
        print("You may need to manually specify the ToC entries.")
        sys.exit(1)
    
    print(f"\nExtracted {len(toc)} ToC entries:")
    for i, entry in enumerate(toc):
        if len(entry) == 3:
            level, title, page = entry
            indent = "  " * (level - 1)
            print(f"{indent}{i+1}. {title} (page {page})")
        else:
            print(f"{i+1}. {entry}")
    print()
    
    # Ask for confirmation
    response = input("Proceed with splitting? (y/n): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        sys.exit(0)
    
    split_pdf_by_toc(input_pdf, output_dir, toc)


if __name__ == "__main__":
    main()








