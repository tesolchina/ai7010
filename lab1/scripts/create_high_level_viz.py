#!/usr/bin/env python3
"""
Create HIGH-LEVEL visualization based on LLM recommendations
Simple, clean diagram showing only main chapters with color coding
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime

# Paths
TOC_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/toc_pa2025.txt')
OUTPUT_IMAGE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/pa2025_high_level_viz.png')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/llm_generation_log.txt')

def log(message):
    """Append message to log file and print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    with open(LOG_FILE, 'a') as f:
        f.write(f"{log_msg}\n")
    print(log_msg)

def create_high_level_diagram():
    """
    Create high-level diagram based on Claude's suggestions:
    - Central box at top
    - Main chapters as boxes in rows
    - Color coded by theme
    """
    
    log("Creating high-level visualization based on LLM recommendations...")
    
    # Parse ToC to get main chapters
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    chapters = []
    for line in lines:
        if '●' in line and 'Chapter' in line:
            # Extract chapter title
            text = line.split('●')[1].strip()
            chapters.append(text)
    
    log(f"Found {len(chapters)} main chapters")
    
    # Color scheme from Claude's suggestion
    color_scheme = {
        0: ('#1565c0', 'Governance/Reform'),      # Blue - Chapter I
        1: ('#1565c0', 'Governance/Reform'),      # Blue - Chapter II
        2: ('#2e7d32', 'Development'),             # Green - Chapter III
        3: ('#2e7d32', 'Development'),             # Green - Chapter IV
        4: ('#2e7d32', 'Development'),             # Green - Chapter V
        5: ('#6a1b9a', 'International Hub'),       # Purple - Chapter VI
        6: ('#f57c00', 'Social/Cultural'),         # Orange - Chapter VII
        7: ('#f57c00', 'Social/Cultural'),         # Orange - Chapter VIII
        8: ('#f57c00', 'Social/Cultural'),         # Orange - Chapter IX
        9: ('#f57c00', 'Social/Community'),        # Orange - Chapter X
        10: ('#5d4037', 'Environment'),            # Brown - Chapter XI
        11: ('#757575', 'Conclusion')              # Gray - Conclusion
    }
    
    # Image settings
    img_width = 2400
    img_height = 1800
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        chapter_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        chapter_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw title box at top
    title_box_height = 150
    draw.rectangle([(0, 0), (img_width, title_box_height)], fill='#0d47a1')
    
    title_text = "2025 HONG KONG POLICY ADDRESS"
    subtitle_text = "High-Level Structure Overview"
    
    # Center title
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_width) // 2, 40), title_text, fill='white', font=title_font)
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((img_width - subtitle_width) // 2, 95), subtitle_text, fill='#bbdefb', font=subtitle_font)
    
    # Draw chapter boxes in grid
    box_width = 520
    box_height = 200
    padding = 60
    gap_x = 80
    gap_y = 60
    
    start_y = title_box_height + 100
    boxes_per_row = 4
    
    for idx, chapter in enumerate(chapters):
        row = idx // boxes_per_row
        col = idx % boxes_per_row
        
        # Calculate position
        x = padding + col * (box_width + gap_x)
        y = start_y + row * (box_height + gap_y)
        
        # Get color
        color_info = color_scheme.get(idx, ('#757575', 'Other'))
        box_color = color_info[0]
        category = color_info[1]
        
        # Draw shadow
        shadow_offset = 8
        draw.rectangle(
            [(x + shadow_offset, y + shadow_offset), 
             (x + box_width + shadow_offset, y + box_height + shadow_offset)],
            fill='#cccccc'
        )
        
        # Draw box
        draw.rectangle([(x, y), (x + box_width, y + box_height)],
                      fill='white', outline=box_color, width=4)
        
        # Draw colored header bar
        header_height = 45
        draw.rectangle([(x, y), (x + box_width, y + header_height)],
                      fill=box_color)
        
        # Draw chapter number
        chapter_num = f"CHAPTER {idx + 1}" if idx < len(chapters) - 1 else "CONCLUSION"
        draw.text((x + 15, y + 12), chapter_num, fill='white', font=small_font)
        
        # Draw chapter title (wrap text)
        title = chapter.replace(f'Chapter {["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"][idx] if idx < 11 else ""}', '').strip()
        
        # Simple text wrapping
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=chapter_font)
            if bbox[2] - bbox[0] < box_width - 30:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw wrapped text
        text_y = y + header_height + 30
        for line in lines[:4]:  # Max 4 lines
            draw.text((x + 15, text_y), line, fill='#333333', font=chapter_font)
            text_y += 25
        
        # Draw category tag
        tag_y = y + box_height - 35
        draw.rectangle([(x + 15, tag_y), (x + 15 + 150, tag_y + 25)],
                      fill=box_color, outline=box_color)
        draw.text((x + 25, tag_y + 5), category, fill='white', font=small_font)
    
    # Draw legend
    legend_y = img_height - 80
    legend_x = padding
    
    draw.text((legend_x, legend_y), "Categories:", fill='#666666', font=subtitle_font)
    legend_x += 150
    
    categories = [
        ('#1565c0', 'Governance'),
        ('#2e7d32', 'Development'),
        ('#6a1b9a', 'International'),
        ('#f57c00', 'Social/Cultural'),
        ('#5d4037', 'Environment'),
        ('#757575', 'Conclusion')
    ]
    
    for color, label in categories:
        draw.rectangle([(legend_x, legend_y + 5), (legend_x + 20, legend_y + 25)],
                      fill=color)
        draw.text((legend_x + 30, legend_y + 5), label, fill='#666666', font=small_font)
        legend_x += 200
    
    # Save image
    img.save(OUTPUT_IMAGE, quality=95, optimize=True)
    log(f"✓ High-level visualization created: {OUTPUT_IMAGE}")
    log(f"✓ Image dimensions: {img_width}x{img_height}px")
    log(f"✓ Chapters visualized: {len(chapters)}")
    
    return OUTPUT_IMAGE

if __name__ == "__main__":
    log("")
    log("="*80)
    log("CREATING HIGH-LEVEL VISUALIZATION")
    log("Based on recommendations from Claude 3.5 Sonnet")
    log("="*80)
    log("")
    
    try:
        result = create_high_level_diagram()
        log("")
        log("="*80)
        log("✓✓✓ HIGH-LEVEL VISUALIZATION COMPLETED!")
        log(f"Output file: {result}")
        log("="*80)
    except Exception as e:
        log(f"✗ ERROR: {e}")
        import traceback
        log(traceback.format_exc())

