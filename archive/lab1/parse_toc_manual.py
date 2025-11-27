#!/usr/bin/env python3
"""
Script to manually parse table of contents and split PDF accordingly.
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


def extract_full_toc_page(doc, toc_page_num):
    """Extract full text from ToC page."""
    page = doc[toc_page_num]
    text = page.get_text()
    return text


def parse_toc_entries(text):
    """Parse ToC entries from text with better pattern matching."""
    lines = text.split('\n')
    toc_entries = []
    
    # Pattern to match: title followed by dots/leaders and page number
    # Examples:
    # "EDITORIAL ................ 5"
    # "NEWS, ETC 10"
    # "A NEW ARCHIVAL RESOURCE 15"
    
    current_title_parts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for page number at the end (1-3 digits)
        page_match = re.search(r'(\d{1,3})\s*$', line)
        
        if page_match:
            page_num = int(page_match.group(1))
            # Get everything before the page number
            title_part = line[:page_match.start()].strip()
            
            # Remove dots/leaders
            title_part = re.sub(r'[.\s]+$', '', title_part).strip()
            
            if title_part:
                # Combine with previous parts if any
                if current_title_parts:
                    title = ' '.join(current_title_parts) + ' ' + title_part
                    current_title_parts = []
                else:
                    title = title_part
                
                # Determine level (all caps might be main sections)
                level = 1
                if title.isupper() or title.istitle():
                    level = 1
                else:
                    level = 2
                
                toc_entries.append((level, title, page_num))
        else:
            # Might be a multi-line title, accumulate
            if line and not re.match(r'^\d+$', line):  # Not just a number
                current_title_parts.append(line)
    
    return toc_entries


def split_pdf_by_toc(pdf_path, output_dir, toc):
    """Split PDF into individual files based on table of contents."""
    doc = fitz.open(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nProcessing PDF: {pdf_path}")
    print(f"Found {len(toc)} ToC entries")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Process each ToC entry
    created_files = 0
    for i, entry in enumerate(toc):
        if len(entry) == 3:
            level, title, page_num = entry
        else:
            title = str(entry[0]) if entry else f"Section_{i+1}"
            page_num = entry[-1] if len(entry) > 1 and isinstance(entry[-1], int) else 1
            level = 1
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', ',')).strip()
        safe_title = safe_title.replace(' ', '_').replace(',', '')
        safe_title = safe_title[:60]  # Limit length
        if not safe_title:
            safe_title = f"Section_{i+1}"
        
        # Determine page range
        start_page = max(0, page_num - 1)  # PyMuPDF uses 0-based indexing
        
        # Find end page (next entry's start page or end of document)
        if i + 1 < len(toc):
            next_entry = toc[i + 1]
            next_page_num = next_entry[-1] if isinstance(next_entry[-1], int) else len(doc)
            end_page = max(start_page, next_page_num - 1)
        else:
            end_page = len(doc) - 1
        
        # Ensure valid page range
        if start_page >= len(doc):
            print(f"Warning: Start page {start_page+1} exceeds document length ({len(doc)}). Skipping: {title}")
            continue
        
        end_page = min(end_page, len(doc) - 1)
        
        if start_page > end_page:
            print(f"Warning: Invalid page range for {title}. Skipping.")
            continue
        
        # Create new PDF for this section
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            
            # Save the file
            output_file = output_path / f"{i+1:02d}_{safe_title}.pdf"
            new_doc.save(str(output_file))
            new_doc.close()
            
            print(f"✓ Created: {output_file.name} (pages {start_page+1}-{end_page+1})")
            created_files += 1
        except Exception as e:
            print(f"✗ Error creating file for '{title}': {e}")
    
    doc.close()
    print("-" * 50)
    print(f"Successfully created {created_files} files in {output_dir}")


def main():
    """Main function."""
    input_pdf = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/SummarizeSynthesize/IndividualFiles"
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF not found: {input_pdf}")
        sys.exit(1)
    
    doc = fitz.open(input_pdf)
    
    print("Extracting table of contents from page 2...")
    toc_text = extract_full_toc_page(doc, 1)  # Page 2 is index 1
    
    print("\n" + "="*70)
    print("FULL ToC PAGE TEXT:")
    print("="*70)
    print(toc_text)
    print("="*70 + "\n")
    
    print("Parsing ToC entries...")
    toc = parse_toc_entries(toc_text)
    doc.close()
    
    if not toc:
        print("Error: Could not extract table of contents entries.")
        print("Please check the ToC text above and verify the format.")
        sys.exit(1)
    
    print(f"\nExtracted {len(toc)} ToC entries:")
    for i, entry in enumerate(toc):
        if len(entry) == 3:
            level, title, page = entry
            indent = "  " * (level - 1)
            print(f"{indent}{i+1:2d}. {title:50s} (page {page})")
        else:
            print(f"{i+1:2d}. {entry}")
    print()
    
    # Auto-proceed (remove confirmation for automation)
    print("Proceeding with PDF splitting...\n")
    split_pdf_by_toc(input_pdf, output_dir, toc)


if __name__ == "__main__":
    main()








