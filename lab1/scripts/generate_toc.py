#!/usr/bin/env python3
"""
Generate Table of Contents from Policy Address 2025 XML file
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Paths
XML_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/data/policyAddress/pa2025_english.xml')
OUTPUT_TOC = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/toc_pa2025.txt')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/process_log.txt')

def log(message):
    """Append message to log file"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{message}\n")
    print(message)

def parse_section(section, level=0, namespace={'': 'http://docbook.org/ns/docbook'}):
    """
    Recursively parse section elements and extract titles
    
    Args:
        section: XML section element
        level: Current hierarchy level
        namespace: XML namespace
    
    Returns:
        List of tuples (level, title)
    """
    toc_entries = []
    
    # Get title of current section (direct child only, not nested)
    title_elem = section.find('./title', namespace)
    if title_elem is not None and title_elem.text:
        # Clean up the title text
        title = ' '.join(title_elem.text.split())
        toc_entries.append((level, title))
    
    # Find all direct child sections
    for child_section in section.findall('./section', namespace):
        child_entries = parse_section(child_section, level + 1, namespace)
        toc_entries.extend(child_entries)
    
    return toc_entries

def generate_toc():
    """Generate Table of Contents from XML file"""
    log("[Step 1] Parsing XML file structure...")
    
    try:
        # Parse XML
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        
        # Define namespace
        namespace = {'': 'http://docbook.org/ns/docbook'}
        
        # Get document title
        info = root.find('.//info', namespace)
        doc_title = None
        if info is not None:
            title_elem = info.find('.//title', namespace)
            if title_elem is not None:
                doc_title = ' '.join(title_elem.text.split())
        
        log(f"[Step 1] Document title: {doc_title}")
        
        # Find all top-level sections (direct children of root article element)
        toc_entries = []
        
        for section in root.findall('./section', namespace):
            entries = parse_section(section, 0, namespace)
            toc_entries.extend(entries)
        
        log(f"[Step 1] Found {len(toc_entries)} ToC entries")
        
        # Generate formatted ToC
        log("[Step 2] Generating formatted Table of Contents...")
        
        toc_lines = []
        toc_lines.append("=" * 80)
        toc_lines.append("TABLE OF CONTENTS")
        toc_lines.append("2025 Policy Address - Hong Kong Chief Executive")
        toc_lines.append("=" * 80)
        toc_lines.append("")
        
        for level, title in toc_entries:
            # Create indentation based on hierarchy level
            indent = "  " * level
            # Add level markers
            if level == 0:
                marker = "■"
            elif level == 1:
                marker = "●"
            elif level == 2:
                marker = "○"
            else:
                marker = "▪"
            
            toc_lines.append(f"{indent}{marker} {title}")
        
        toc_lines.append("")
        toc_lines.append("=" * 80)
        toc_lines.append(f"Total sections: {len(toc_entries)}")
        toc_lines.append("=" * 80)
        
        # Save ToC to file
        toc_content = "\n".join(toc_lines)
        with open(OUTPUT_TOC, 'w', encoding='utf-8') as f:
            f.write(toc_content)
        
        log(f"[Step 2] ✓ Table of Contents saved to: {OUTPUT_TOC}")
        log(f"[Step 2] ✓ Total entries: {len(toc_entries)}")
        
        return OUTPUT_TOC, len(toc_entries)
        
    except Exception as e:
        log(f"[ERROR] Failed to generate ToC: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_toc()

