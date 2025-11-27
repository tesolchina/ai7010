#!/usr/bin/env python3
"""
Process vertical Chinese text using chineseocr_lite
Input: /Users/simonwang/Documents/Usage/ai7010/lab3/onePage/image.png
Output: Markdown file with extracted text
"""

import os
import sys
from datetime import datetime
from PIL import Image
import numpy as np

# Add the lab5 directory to path to import modules
lab5_path = "/Users/simonwang/Documents/Usage/ai7010/lab5"
sys.path.insert(0, lab5_path)

# Import the OCR model
from model import OcrHandle

def process_vertical_chinese_image(image_path, output_path):
    """
    Process a vertical Chinese text image and output to markdown
    
    Args:
        image_path: Path to input image
        output_path: Path to output markdown file
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting OCR processing...")
    print(f"Input image: {image_path}")
    print(f"Output file: {output_path}")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"ERROR: Image file not found: {image_path}")
        return
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loading image...")
    # Load image
    img = Image.open(image_path)
    print(f"Image size: {img.size[0]}x{img.size[1]} pixels")
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initializing OCR model...")
    # Initialize OCR handler
    ocr_handle = OcrHandle()
    print("OCR model loaded successfully!")
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running OCR detection and recognition...")
    # Process the image with different sizes to get best results
    # For vertical text, we might want to try a larger short_size
    short_size = 1024  # Adjust this based on image size
    
    result = ocr_handle.text_predict(img, short_size=short_size)
    print(f"Found {len(result)} text regions")
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing results...")
    
    # Prepare markdown content
    markdown_content = []
    markdown_content.append("# OCR Results - Vertical Chinese Text\n")
    markdown_content.append(f"**Source Image:** `{os.path.basename(image_path)}`\n")
    markdown_content.append(f"**Processing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    markdown_content.append(f"**Total Text Regions Detected:** {len(result)}\n")
    markdown_content.append("\n---\n\n")
    
    if len(result) == 0:
        markdown_content.append("⚠️ No text detected in the image.\n")
    else:
        markdown_content.append("## Extracted Text\n\n")
        
        # Sort results by position (top to bottom, then right to left for vertical text)
        # For vertical Chinese text, we typically read from right to left, top to bottom
        sorted_results = sorted(result, key=lambda x: (-x[0][0][0], x[0][0][1]))
        
        # Group by columns (vertical text is organized in columns)
        # We'll use x-coordinate to group text into columns
        columns = {}
        for box, text, score in sorted_results:
            # Get the average x-coordinate of the box
            x_center = np.mean([point[0] for point in box])
            
            # Group texts by columns (allow some tolerance)
            column_found = False
            for col_x in columns.keys():
                if abs(x_center - col_x) < 50:  # Tolerance for grouping
                    columns[col_x].append((box, text, score, x_center))
                    column_found = True
                    break
            
            if not column_found:
                columns[x_center] = [(box, text, score, x_center)]
        
        # Sort columns from right to left (typical for vertical Chinese)
        sorted_columns = sorted(columns.items(), key=lambda x: -x[0])
        
        print(f"Text organized into {len(sorted_columns)} columns")
        
        # Output text column by column
        for col_idx, (col_x, texts) in enumerate(sorted_columns, 1):
            markdown_content.append(f"### Column {col_idx}\n\n")
            
            # Sort texts within column from top to bottom
            texts.sort(key=lambda x: x[0][0][1])
            
            for box, text, score, _ in texts:
                # Remove the numbering prefix if present (e.g., "1、 ")
                clean_text = text
                if "、 " in text:
                    parts = text.split("、 ", 1)
                    if len(parts) > 1:
                        clean_text = parts[1]
                
                markdown_content.append(f"{clean_text}\n\n")
                print(f"  Column {col_idx}: {clean_text[:50]}{'...' if len(clean_text) > 50 else ''}")
        
        # Also add a continuous text version
        markdown_content.append("\n---\n\n")
        markdown_content.append("## Continuous Text (All Columns)\n\n")
        
        all_texts = []
        for col_idx, (col_x, texts) in enumerate(sorted_columns, 1):
            texts.sort(key=lambda x: x[0][0][1])
            for box, text, score, _ in texts:
                clean_text = text
                if "、 " in text:
                    parts = text.split("、 ", 1)
                    if len(parts) > 1:
                        clean_text = parts[1]
                all_texts.append(clean_text)
        
        markdown_content.append(" ".join(all_texts))
        markdown_content.append("\n")
    
    # Write to markdown file
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Writing output to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(markdown_content)
    
    print(f"\n✅ Processing complete! Output saved to: {output_path}")
    print(f"Total lines extracted: {len(result)}")

if __name__ == "__main__":
    # Input and output paths
    input_image = "/Users/simonwang/Documents/Usage/ai7010/lab3/onePage/image.png"
    output_markdown = "/Users/simonwang/Documents/Usage/ai7010/lab5/output_vertical_chinese.md"
    
    # Process the image
    process_vertical_chinese_image(input_image, output_markdown)





