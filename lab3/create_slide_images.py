"""
Create slide images programmatically based on Gemini's redesign specifications
Uses PIL (Pillow) to generate actual slide images
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime

OUTPUT_DIR = "/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides"
PROGRESS_LOG = os.path.join(OUTPUT_DIR, "slide_creation_log.txt")

# Slide dimensions (16:9 widescreen)
SLIDE_WIDTH = 1920
SLIDE_HEIGHT = 1080

def log_progress(message):
    """Log progress to both console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(PROGRESS_LOG, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_slide_1():
    """
    Create Slide 1: AI Agents for Research
    Based on Gemini's redesign specifications
    """
    log_progress("Creating Slide 1: AI Agents for Research")
    
    # Create image with gradient background
    img = Image.new('RGB', (SLIDE_WIDTH, SLIDE_HEIGHT))
    draw = ImageDraw.Draw(img)
    
    # Create subtle gradient background
    for y in range(SLIDE_HEIGHT):
        ratio = y / SLIDE_HEIGHT
        r = int(248 + (238 - 248) * ratio)
        g = int(248 + (238 - 248) * ratio)
        b = int(248 + (238 - 248) * ratio)
        draw.rectangle([(0, y), (SLIDE_WIDTH, y + 1)], fill=(r, g, b))
    
    # Try to load fonts (fallback to default if not available)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        author_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
        affil_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        log_progress("  Using default fonts (TrueType fonts not found)")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        affil_font = ImageFont.load_default()
    
    # Colors (from Gemini spec)
    title_color = hex_to_rgb("#333333")  # Deep charcoal grey
    subtitle_color = hex_to_rgb("#666666")  # Medium grey
    accent_color = hex_to_rgb("#00CBA7")  # Teal accent
    
    # Draw abstract AI patterns in background (subtle circles/nodes)
    for i in range(10):
        x = i * 200 + 100
        y = 200 + (i % 3) * 300
        draw.ellipse([x, y, x+30, y+30], fill=(220, 235, 240, 128), outline=(200, 215, 220))
    
    # Main title
    title_text = "AI Agents for Research"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (SLIDE_WIDTH - title_width) // 2
    draw.text((title_x, 150), title_text, fill=title_color, font=title_font)
    
    # Subtitle
    subtitle_text = "Transforming Research Workflows for PhD students in\nPhilosophy and Religion"
    subtitle_lines = subtitle_text.split('\n')
    y_offset = 320
    for line in subtitle_lines:
        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        line_width = bbox[2] - bbox[0]
        line_x = (SLIDE_WIDTH - line_width) // 2
        draw.text((line_x, y_offset), line, fill=subtitle_color, font=subtitle_font)
        y_offset += 60
    
    # Draw a stylized "QR code" placeholder (geometric pattern)
    qr_size = 250
    qr_x = 400
    qr_y = 550
    draw.rectangle([qr_x, qr_y, qr_x+qr_size, qr_y+qr_size], fill="white", outline=title_color, width=3)
    # Add some geometric patterns inside
    for i in range(5):
        for j in range(5):
            if (i + j) % 2 == 0:
                x1 = qr_x + i * 50 + 10
                y1 = qr_y + j * 50 + 10
                draw.rectangle([x1, y1, x1+40, y1+40], fill=title_color)
    
    # Author information (right side)
    author_x = 1100
    author_y = 600
    
    draw.text((author_x, author_y), "Dr Simon Wang", fill=subtitle_color, font=author_font)
    draw.text((author_x, author_y + 60), "Lecturer & Innovation Officer", fill=subtitle_color, font=affil_font)
    draw.text((author_x, author_y + 105), "The Language Centre", fill=subtitle_color, font=affil_font)
    draw.text((author_x, author_y + 145), "HKBU", fill=subtitle_color, font=affil_font)
    
    # Add subtle accent line
    draw.rectangle([100, 500, 1820, 505], fill=accent_color)
    
    # Save image
    output_path = os.path.join(OUTPUT_DIR, "slide_1_new.png")
    img.save(output_path, 'PNG', quality=95)
    log_progress(f"✓ Slide 1 saved to: {output_path}")
    
    return output_path

def create_slide_2():
    """
    Create Slide 2: Two Ways to Communicate with AI
    Based on Gemini's redesign specifications
    """
    log_progress("Creating Slide 2: Two Ways to Communicate with AI")
    
    # Create image with dark background (tech-inspired)
    bg_color = hex_to_rgb("#1a1a2e")  # Deep navy/charcoal
    img = Image.new('RGB', (SLIDE_WIDTH, SLIDE_HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 96)
        section_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
        bullet_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except:
        log_progress("  Using default fonts (TrueType fonts not found)")
        title_font = ImageFont.load_default()
        section_font = ImageFont.load_default()
        bullet_font = ImageFont.load_default()
    
    # Colors
    text_color = (255, 255, 255)  # White
    accent_color = hex_to_rgb("#00CBA7")  # Teal/cyan accent
    box_color = hex_to_rgb("#2a2a3e")  # Slightly lighter for boxes
    
    # Main title
    title_text = "Two Ways to Communicate with AI"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (SLIDE_WIDTH - title_width) // 2
    draw.text((title_x, 80), title_text, fill=accent_color, font=title_font)
    
    # Draw two boxes for sections
    box_padding = 40
    box_width = 750
    box_height = 700
    left_box_x = 100
    right_box_x = 1070
    box_y = 250
    
    # Left box (Browser)
    draw.rounded_rectangle(
        [left_box_x, box_y, left_box_x + box_width, box_y + box_height],
        radius=20,
        fill=box_color,
        outline=accent_color,
        width=3
    )
    
    # Right box (IDE)
    draw.rounded_rectangle(
        [right_box_x, box_y, right_box_x + box_width, box_y + box_height],
        radius=20,
        fill=box_color,
        outline=accent_color,
        width=3
    )
    
    # Left section: Browser
    draw.text((left_box_x + box_padding, box_y + box_padding), "Browser", fill=accent_color, font=section_font)
    
    browser_bullets = [
        "• More intuitive",
        "• Natural language",
        "• Context switching",
        "• Time-consuming",
        "• AI can only produce",
        "  textual responses"
    ]
    
    y_offset = box_y + box_padding + 100
    for bullet in browser_bullets:
        draw.text((left_box_x + box_padding, y_offset), bullet, fill=text_color, font=bullet_font)
        y_offset += 70
    
    # Right section: IDE
    draw.text((right_box_x + box_padding, box_y + box_padding), "IDE", fill=accent_color, font=section_font)
    
    ide_bullets = [
        "• Learning curve",
        "• Some setup",
        "• Natural language +...",
        "• AI embedded in context",
        "• AI agents can read/edit",
        "  files, search web, and",
        "  run scripts"
    ]
    
    y_offset = box_y + box_padding + 100
    for bullet in ide_bullets:
        draw.text((right_box_x + box_padding, y_offset), bullet, fill=text_color, font=bullet_font)
        y_offset += 70
    
    # Draw connection line between "Natural language" items
    draw.line([(left_box_x + box_width, box_y + 280), (right_box_x, box_y + 280)], fill=accent_color, width=2)
    
    # Save image
    output_path = os.path.join(OUTPUT_DIR, "slide_2_new.png")
    img.save(output_path, 'PNG', quality=95)
    log_progress(f"✓ Slide 2 saved to: {output_path}")
    
    return output_path

def main():
    """Main function"""
    
    # Initialize log
    with open(PROGRESS_LOG, 'w', encoding='utf-8') as f:
        f.write("")
    
    log_progress("="*60)
    log_progress("Starting Programmatic Slide Creation")
    log_progress("Using Gemini's redesign specifications")
    log_progress("="*60)
    
    # Create slides
    slide1_path = create_slide_1()
    slide2_path = create_slide_2()
    
    log_progress("="*60)
    log_progress("Slide creation complete!")
    log_progress(f"Slide 1: {slide1_path}")
    log_progress(f"Slide 2: {slide2_path}")
    log_progress("="*60)

if __name__ == "__main__":
    main()

