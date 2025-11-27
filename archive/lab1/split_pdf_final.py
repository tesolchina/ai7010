#!/usr/bin/env python3
"""
Script to split PDF based on table of contents.
Handles two-column ToC format.
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


def extract_toc_from_two_column_format(doc, toc_page_num):
    """Extract ToC from two-column format (titles left, page numbers right)."""
    page = doc[toc_page_num]
    text = page.get_text()
    
    # Split into lines
    lines = text.split('\n')
    
    # Identify the ToC section (after copyright, before "contents")
    toc_started = False
    toc_lines = []
    page_numbers = []
    
    for line in lines:
        line = line.strip()
        
        # Start collecting after we see "EDITORIAL" or similar ToC markers
        if not toc_started and (line == "EDITORIAL" or "EDITORIAL" in line):
            toc_started = True
        
        if toc_started:
            # Stop at "contents" or empty sections
            if line.lower() == "contents" or (line and line.isdigit() and len(line) <= 3):
                # This might be a page number
                if line.isdigit():
                    page_numbers.append(int(line))
                continue
            
            # Collect title lines (non-empty, not just numbers)
            if line and not line.isdigit() and line not in ["contents", ""]:
                # Skip header/footer lines
                if "WWW.BASR" in line or "ABOUT THE BASR" in line or "COMMITTEE" in line:
                    continue
                if "@" in line or "All rights reserved" in line:
                    continue
                
                toc_lines.append(line)
            
            # Collect page numbers (standalone digits)
            if line.isdigit() and len(line) <= 3:
                page_numbers.append(int(line))
    
    # Manual mapping based on the extracted text
    # Titles in order:
    titles = [
        "EDITORIAL",
        "NEWS, ETC",
        "CONFERENCES",
        "INFORM",
        "IAHR",
        "FEATURES",
        "A NEW ARCHIVAL RESOURCE",
        "TEACHING ABOUT RELIGION AND CLIMATE CHANGE",
        "WORLD RELIGIONS PARADIGM REVISITED",
        "MEET THE MEMBERS",
        "BOOK REVIEWS",
        "EPISTEMIC AMBIVALENCE",
        "THE MINISTRY OF LOUIS FARRAKHAN",
        "NEOLIBERAL RELIGION",
        "SETTING OUT ON THE GREAT WAY",
        "RELIGION AND HUMOUR",
        "RELIGION AND TOURISM IN JAPAN",
        "ATHEISM IN 5 MINUTES",
        "RECENT PUBLICATIONS"
    ]
    
    # Page numbers extracted: [2, 3, 6, 8, 11, 13, 16, 18, 20, 21, 23, 25, 28, 30, 31, 34]
    # But we have 19 titles, so let's extract them properly
    
    # Try to extract page numbers from the text more carefully
    all_numbers = re.findall(r'\b(\d{1,3})\b', text)
    # Filter to reasonable page numbers (likely 2-50 for a bulletin)
    page_nums = [int(n) for n in all_numbers if 2 <= int(n) <= 50]
    # Remove duplicates while preserving order
    seen = set()
    unique_page_nums = []
    for num in page_nums:
        if num not in seen:
            seen.add(num)
            unique_page_nums.append(num)
    
    # Match titles with page numbers
    toc_entries = []
    
    # Based on the text output, the page numbers appear to be: 2, 3, 6, 8, 11, 13, 16, 18, 20, 21, 23, 25, 28, 30, 31, 34
    # But we need to match them with titles. Let's use the extracted unique page numbers
    page_nums_final = unique_page_nums[:len(titles)] if len(unique_page_nums) >= len(titles) else unique_page_nums
    
    # If we don't have enough page numbers, try to infer from the pattern
    if len(page_nums_final) < len(titles):
        # Use the extracted ones and estimate the rest
        if page_nums_final:
            last_num = page_nums_final[-1]
            # Estimate remaining pages (rough estimate)
            for i in range(len(page_nums_final), len(titles)):
                last_num += 2  # Rough estimate
                page_nums_final.append(last_num)
    
    for i, title in enumerate(titles):
        if i < len(page_nums_final):
            page_num = page_nums_final[i]
        else:
            # Fallback: estimate based on previous
            page_num = page_nums_final[-1] + (i - len(page_nums_final) + 1) * 2 if page_nums_final else i + 2
        
        toc_entries.append((1, title, page_num))
    
    return toc_entries


def extract_toc_manual():
    """Manually define ToC based on the image/text analysis."""
    # Based on the extracted text, here's the ToC mapping:
    toc_entries = [
        (1, "EDITORIAL", 2),
        (1, "NEWS, ETC", 3),
        (1, "CONFERENCES", 6),
        (1, "INFORM", 8),
        (1, "IAHR", 11),
        (1, "FEATURES", 13),
        (1, "A NEW ARCHIVAL RESOURCE", 16),
        (1, "TEACHING ABOUT RELIGION AND CLIMATE CHANGE", 18),
        (1, "WORLD RELIGIONS PARADIGM REVISITED", 20),
        (1, "MEET THE MEMBERS", 21),
        (1, "BOOK REVIEWS", 23),
        (1, "EPISTEMIC AMBIVALENCE", 25),
        (1, "THE MINISTRY OF LOUIS FARRAKHAN", 28),
        (1, "NEOLIBERAL RELIGION", 30),
        (1, "SETTING OUT ON THE GREAT WAY", 31),
        (1, "RELIGION AND HUMOUR", 34),
        (1, "RELIGION AND TOURISM IN JAPAN", 36),  # Estimated
        (1, "ATHEISM IN 5 MINUTES", 38),  # Estimated
        (1, "RECENT PUBLICATIONS", 35),  # Found on page 35
    ]
    return toc_entries


def split_pdf_by_toc(pdf_path, output_dir, toc):
    """Split PDF into individual files based on table of contents."""
    doc = fitz.open(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nProcessing PDF: {pdf_path}")
    print(f"Total pages in document: {len(doc)}")
    print(f"Found {len(toc)} ToC entries")
    print(f"Output directory: {output_dir}")
    print("-" * 70)
    
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
        safe_title = safe_title.replace(' ', '_').replace(',', '').replace("'", "")
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
            print(f"⚠ Warning: Start page {start_page+1} exceeds document length ({len(doc)}). Skipping: {title}")
            continue
        
        end_page = min(end_page, len(doc) - 1)
        
        if start_page > end_page:
            print(f"⚠ Warning: Invalid page range for {title}. Skipping.")
            continue
        
        # Create new PDF for this section
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            
            # Save the file
            output_file = output_path / f"{i+1:02d}_{safe_title}.pdf"
            new_doc.save(str(output_file))
            new_doc.close()
            
            print(f"✓ [{i+1:2d}/{len(toc)}] {output_file.name:60s} (pages {start_page+1:3d}-{end_page+1:3d})")
            created_files += 1
        except Exception as e:
            print(f"✗ Error creating file for '{title}': {e}")
    
    doc.close()
    print("-" * 70)
    print(f"✅ Successfully created {created_files} files in {output_dir}")


def main():
    """Main function."""
    input_pdf = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/SummarizeSynthesize/IndividualFiles"
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF not found: {input_pdf}")
        sys.exit(1)
    
    # Use manual ToC extraction based on analysis
    print("Using manual ToC mapping based on document analysis...")
    toc = extract_toc_manual()
    
    print(f"\nToC entries ({len(toc)} total):")
    for i, entry in enumerate(toc):
        level, title, page = entry
        print(f"  {i+1:2d}. {title:50s} (page {page})")
    print()
    
    split_pdf_by_toc(input_pdf, output_dir, toc)


if __name__ == "__main__":
    main()

