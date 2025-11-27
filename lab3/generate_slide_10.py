#!/usr/bin/env python3
"""Generate slide 10 only"""

import requests, json, base64
from pathlib import Path
from datetime import datetime

API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
OUTPUT_DIR = Path('/Users/simonwang/Documents/Usage/ai7010/lab3/newSlides')

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

api_key = open(API_KEY_FILE).read().split('=')[1].strip()

prompt = """Generate a professional presentation slide image:

TITLE: "Lab 2: Screening & Synthesis with IPO Model"

Show three boxes side-by-side:

Box 1 - INPUT (📥 icon):
• CSV file with abstracts from Lab 1
• Screening criteria  
• Research questions

Box 2 - PROCESS (⚙️ icon):
• Use AI to screen abstracts
• Filter relevant articles
• Extract key findings
• Synthesize results

Box 3 - OUTPUT (📤 icon):
• Screened article list
• Synthesis summary
• Structured findings report

Design: Modern, professional, three-column layout with emoji icons. Use teal accents. 16:9 widescreen.
Footer: "© 2024 AI Research Institute | Date: 27 Nov 2025"
"""

log("Requesting Gemini to generate slide 10...")

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "google/gemini-3-pro-image-preview",
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "max_tokens": 2000
    },
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    if result.get("choices", [{}])[0].get("message", {}).get("images"):
        image_url = result["choices"][0]["message"]["images"][0].get("image_url", {}).get("url", "")
        if image_url.startswith("data:image"):
            img_data = base64.b64decode(image_url.split(',')[1])
            output = OUTPUT_DIR / "slide_10_gemini.png"
            open(output, 'wb').write(img_data)
            log(f"✓ SUCCESS! Slide 10 saved: {len(img_data)} bytes")
            log(f"  File: {output}")
        else:
            log("✗ No valid image URL")
    else:
        log("✗ No images in response")
        log(f"Content: {result.get('choices', [{}])[0].get('message', {}).get('content', 'None')[:200]}")
else:
    log(f"✗ Failed: {response.status_code}")

