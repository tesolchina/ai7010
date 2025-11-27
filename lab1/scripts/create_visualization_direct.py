#!/usr/bin/env python3
"""
Create visualization of Policy Address 2025 structure directly using Python
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Paths
TOC_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/toc_pa2025.txt')
OUTPUT_IMAGE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/pa2025_structure_visualization.png')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/process_log.txt')

def log(message):
    """Append message to log file and print"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{message}\n")
    print(message)

def create_visualization():
    """Create a professional visualization of the Policy Address structure"""
    
    log("[Step 5] Creating visualization image...")
    
    # Read ToC file
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        toc_content = f.read()
    
    # Parse ToC lines
    lines = toc_content.split('\n')
    toc_items = []
    
    for line in lines:
        if line.strip() and len(line.strip()) > 0:
            # Check for markers
            if '■' in line:
                level = 0
                text = line.split('■', 1)[1].strip()
            elif '●' in line:
                level = 1
                text = line.split('●', 1)[1].strip()
            elif '○' in line:
                level = 2
                text = line.split('○', 1)[1].strip()
            elif '▪' in line:
                level = 3
                text = line.split('▪', 1)[1].strip()
            else:
                continue
            
            if text:
                toc_items.append((level, text))
    
    log(f"[Step 5] Parsed {len(toc_items)} items from ToC")
    
    # Image dimensions
    img_width = 3000
    line_height = 30
    padding = 60
    header_space = 150
    img_height = len(toc_items) * line_height + header_space + padding
    
    # Create image with gradient background
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw subtle background gradient rectangles
    for i in range(0, img_height, 100):
        alpha = 245 + (i % 10)
        draw.rectangle([(0, i), (img_width, i + 50)], fill=(alpha, alpha, 250))
    
    # Try to use system fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        # Fallback
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors for different levels
    level_colors = {
        0: '#0d47a1',  # Deep blue for main chapters
        1: '#1565c0',  # Medium blue for sections  
        2: '#1976d2',  # Blue for subsections
        3: '#42a5f5'   # Light blue for sub-subsections
    }
    
    box_colors = {
        0: '#e3f2fd',  # Very light blue
        1: '#f5f5f5',  # Light gray
        2: '#fafafa',  # Very light gray
        3: '#ffffff'   # White
    }
    
    # Draw header
    draw.rectangle([(0, 0), (img_width, header_space)], fill='#0d47a1')
    
    title = "2025 HONG KONG POLICY ADDRESS"
    subtitle = "Hierarchical Structure Overview"
    
    # Center title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (img_width - title_width) // 2
    draw.text((title_x, 30), title, fill='white', font=title_font)
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (img_width - subtitle_width) // 2
    draw.text((subtitle_x, 80), subtitle, fill='#e3f2fd', font=subtitle_font)
    
    # Draw legend
    legend_y = header_space + 20
    legend_x = padding
    draw.text((legend_x, legend_y), "■ Main Chapter  ● Section  ○ Subsection  ▪ Sub-subsection", 
             fill='#666666', font=small_font)
    
    # Draw ToC items
    y = header_space + 60
    current_chapter = 0
    
    for level, text in toc_items:
        # Calculate indentation
        indent = padding + (level * 50)
        
        # Track chapters for alternating backgrounds
        if level == 0:
            current_chapter += 1
            
        # Draw background box for better readability
        if level == 0:
            # Draw chapter box
            draw.rectangle([(padding - 10, y - 5), (img_width - padding, y + line_height - 5)],
                          fill=box_colors[0], outline=level_colors[0], width=2)
        elif level == 1:
            # Draw section indicator line
            draw.line([(indent - 30, y + 8), (indent - 10, y + 8)], 
                     fill=level_colors[1], width=3)
        
        # Draw connection lines for hierarchy
        if level > 0:
            parent_indent = padding + ((level - 1) * 50)
            draw.line([(parent_indent + 5, y - 15), (indent - 5, y + 8)],
                     fill='#cccccc', width=1)
        
        # Draw bullet/marker
        marker_sizes = {0: 12, 1: 10, 2: 8, 3: 6}
        marker_size = marker_sizes.get(level, 6)
        
        draw.ellipse([(indent, y + 6), (indent + marker_size, y + 6 + marker_size)],
                    fill=level_colors[level], outline=level_colors[level])
        
        # Select font based on level
        if level == 0:
            font = header_font
            text_color = level_colors[0]
            text = text.upper()[:100]  # Limit length and uppercase
        elif level == 1:
            font = normal_font
            text_color = '#1a1a1a'
            text = text[:120]
        else:
            font = small_font if level >= 2 else normal_font
            text_color = '#333333'
            text = text[:100]
        
        # Draw text
        text_x = indent + marker_size + 15
        draw.text((text_x, y + 2), text, fill=text_color, font=font)
        
        y += line_height
    
    # Draw footer
    footer_text = f"Generated: {len(toc_items)} sections | Hong Kong SAR Government"
    draw.text((padding, img_height - 40), footer_text, fill='#999999', font=small_font)
    
    # Save image
    img.save(OUTPUT_IMAGE, quality=95, optimize=True)
    log(f"[Step 5] ✓ Visualization image created: {OUTPUT_IMAGE}")
    log(f"[Step 5] ✓ Image dimensions: {img_width}x{img_height}px")
    log(f"[Step 5] ✓ Total items visualized: {len(toc_items)}")
    
    return OUTPUT_IMAGE

if __name__ == "__main__":
    try:
        img_path = create_visualization()
        log("=" * 80)
        log("[COMPLETE] Visualization successfully created!")
        log(f"[COMPLETE] Image file: {img_path}")
        log("=" * 80)
    except Exception as e:
        log(f"[ERROR] Failed to create visualization: {e}")
        import traceback
        log(f"[TRACEBACK] {traceback.format_exc()}")

