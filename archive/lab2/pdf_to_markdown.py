#!/usr/bin/env python3
"""
Convert PDF to Markdown format preserving all content.
"""

import sys
import os
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not installed. Install with: pip install PyMuPDF")
    sys.exit(1)


def pdf_to_markdown(pdf_path, output_path):
    """
    Convert PDF to Markdown format.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output Markdown file
    """
    doc = fitz.open(pdf_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting PDF to Markdown...")
    print(f"Input: {pdf_path}")
    print(f"Output: {output_path}")
    print(f"Total pages: {len(doc)}")
    print("-" * 70)
    
    markdown_content = []
    
    # Add document metadata as header
    metadata = doc.metadata
    if metadata:
        markdown_content.append("# Document\n\n")
        if metadata.get('title'):
            markdown_content.append(f"**Title:** {metadata['title']}\n\n")
        if metadata.get('author'):
            markdown_content.append(f"**Author:** {metadata['author']}\n\n")
        if metadata.get('subject'):
            markdown_content.append(f"**Subject:** {metadata['subject']}\n\n")
        markdown_content.append("---\n\n")
    
    # Process each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Add page break
        markdown_content.append(f"\n## Page {page_num + 1}\n\n")
        
        # Extract text blocks with position information for better formatting
        blocks = page.get_text("dict")
        
        page_has_content = False
        
        # Process text blocks to preserve structure
        if blocks.get("blocks"):
            for block in blocks["blocks"]:
                if "lines" in block:  # Text block
                    paragraph_lines = []
                    for line in block["lines"]:
                        line_text = []
                        for span in line["spans"]:
                            text_content = span["text"]
                            # Preserve formatting
                            flags = span.get("flags", 0)
                            if flags & 16:  # Bold
                                text_content = f"**{text_content}**"
                            if flags & 2:  # Italic
                                text_content = f"*{text_content}*"
                            line_text.append(text_content)
                        
                        if line_text:
                            line_content = "".join(line_text).strip()
                            if line_content:
                                paragraph_lines.append(line_content)
                    
                    # Join lines into paragraph, preserving structure
                    if paragraph_lines:
                        # Check if lines should be separate (for lists, addresses, etc.)
                        # If lines are short and similar length, might be a list
                        if len(paragraph_lines) > 1 and all(len(line) < 80 for line in paragraph_lines):
                            # Might be a list or structured content
                            paragraph = "\n".join(paragraph_lines)
                        else:
                            # Regular paragraph
                            paragraph = " ".join(paragraph_lines)
                        
                        if paragraph.strip():
                            markdown_content.append(f"{paragraph}\n\n")
                            page_has_content = True
                            
                elif "image" in block:  # Image block
                    # Note: Images are referenced but not embedded
                    markdown_content.append(f"![Image on page {page_num + 1}]\n\n")
                    page_has_content = True
        
        # Fallback: if block processing didn't work well, use simple text extraction
        if not page_has_content:
            # Use simple text extraction
            text = page.get_text()
            if text.strip():
                # Preserve the text as-is, maintaining line breaks for structure
                # Split into paragraphs (double newlines indicate paragraph breaks)
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        # For single-line paragraphs, join with space
                        # For multi-line paragraphs, preserve line breaks
                        lines = para.split('\n')
                        if len(lines) > 1:
                            # Multi-line: preserve structure
                            markdown_content.append(f"{para}\n\n")
                        else:
                            # Single line: just the text
                            markdown_content.append(f"{para}\n\n")
                        page_has_content = True
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(markdown_content))
    
    doc.close()
    
    print(f"✅ Successfully converted PDF to Markdown")
    print(f"   Output file: {output_path}")
    print(f"   File size: {output_file.stat().st_size / 1024:.2f} KB")


def main():
    """Main function."""
    input_pdf = "/Users/simonwang/Documents/Usage/ai7010/data/bulletin-144-min may2024.pdf"
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/lab2/Files"
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF not found: {input_pdf}")
        sys.exit(1)
    
    # Create output filename
    pdf_name = Path(input_pdf).stem
    output_md = os.path.join(output_dir, f"{pdf_name}.md")
    
    pdf_to_markdown(input_pdf, output_md)


if __name__ == "__main__":
    main()

