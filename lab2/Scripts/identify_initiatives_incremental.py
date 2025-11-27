#!/usr/bin/env python3
"""
Extract government initiatives from Policy Address 2025
IMPROVED VERSION: Saves to CSV incrementally (after each paragraph)
"""

import xml.etree.ElementTree as ET
import requests
import json
import csv
from pathlib import Path
from datetime import datetime
import time
import os

# Paths
XML_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/data/policyAddress/pa2025_english.xml')
API_KEY_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab1/APIkey.txt')
OUTPUT_CSV = Path('/Users/simonwang/Documents/Usage/ai7010/lab2/output/initiatives.csv')
LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab2/output/extraction_log.txt')

# API Settings
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen-2.5-72b-instruct"

def log(message):
    """Append message to log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{log_msg}\n")
    
    print(log_msg)

def init_log():
    """Initialize log file"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("INITIATIVES EXTRACTION - INCREMENTAL SAVE VERSION\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")

def init_csv():
    """Initialize CSV file with headers"""
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Paragraph_Number', 'Initiative', 'Context', 'Goal', 'Timeline'])
        writer.writeheader()
    log(f"✓ CSV file initialized: {OUTPUT_CSV}")

def append_to_csv(para_num, initiatives):
    """Append initiatives to CSV file"""
    if not initiatives or len(initiatives) == 0:
        return
    
    with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Paragraph_Number', 'Initiative', 'Context', 'Goal', 'Timeline'])
        
        for item in initiatives:
            writer.writerow({
                'Paragraph_Number': para_num,
                'Initiative': item.get('initiative', ''),
                'Context': item.get('context', ''),
                'Goal': item.get('goal', ''),
                'Timeline': item.get('timeline', 'Not specified')
            })

def read_api_key():
    """Read OpenRouter API key"""
    with open(API_KEY_FILE, 'r') as f:
        content = f.read().strip()
        if 'sk-or-v1-' in content:
            return content.split('=')[1].strip()
        else:
            return content.strip()

def extract_paragraphs():
    """Extract all paragraphs from XML file"""
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    namespace = {'': 'http://docbook.org/ns/docbook'}
    
    paragraphs = []
    for para in root.findall('.//para', namespace):
        if para.text:
            text = ' '.join(para.text.split())
            if len(text) > 50:
                paragraphs.append(text)
    
    return paragraphs

def ask_llm_for_initiatives(api_key, paragraph_text):
    """Send paragraph to LLM to identify government initiatives"""
    
    prompt = f"""Analyze the following paragraph from Hong Kong's 2025 Policy Address and identify ANY specific government initiatives announced.

For EACH initiative you find, extract:
1. Initiative Name (brief, clear title)
2. Context (background or reason for this initiative)
3. Goal (what the government aims to achieve)
4. Timeline (if mentioned - dates, years, or timeframes)

Paragraph:
{paragraph_text}

Respond in JSON format as an array of initiatives. If no initiatives found, return empty array [].

Example format:
[
  {{
    "initiative": "Light Public Housing Programme",
    "context": "Address public housing shortage and reduce waiting time",
    "goal": "Provide transitional housing for PRH applicants",
    "timeline": "Three years (2022-2025)"
  }}
]

Return ONLY the JSON array, no other text."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/simonwang/ai7010",
        "X-Title": "Policy Address Initiatives Extraction"
    }
    
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Extract JSON from response
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                initiatives = json.loads(content.strip())
                
                if isinstance(initiatives, list):
                    return initiatives
                        
        elif response.status_code == 429:
            log(f"  ⚠ Rate limited, waiting 5 seconds...")
            time.sleep(5)
            return None  # Retry signal
            
    except json.JSONDecodeError as e:
        log(f"  ⚠ JSON parse error: {str(e)[:100]}")
        return []
    except Exception as e:
        log(f"  ✗ Error: {str(e)[:100]}")
        return []
    
    return []

def main():
    """Main execution function"""
    
    init_log()
    log("Starting Incremental Extraction Process")
    log("="*80)
    
    try:
        # Read API key
        api_key = read_api_key()
        log(f"✓ API key loaded")
        
        # Extract paragraphs
        paragraphs = extract_paragraphs()
        log(f"✓ Extracted {len(paragraphs)} paragraphs from XML")
        log(f"Model: {MODEL}")
        
        # Initialize CSV
        init_csv()
        log("")
        
        # Process paragraphs
        log("="*80)
        log("Processing Paragraphs (Saving incrementally)")
        log("="*80)
        
        total_initiatives = 0
        
        for idx, para in enumerate(paragraphs, 1):
            log(f"\nParagraph {idx}/{len(paragraphs)}:")
            
            # Ask LLM
            result = ask_llm_for_initiatives(api_key, para)
            
            # Handle retry on rate limit
            if result is None:
                result = ask_llm_for_initiatives(api_key, para)
            
            if result and isinstance(result, list) and len(result) > 0:
                # Save to CSV immediately!
                append_to_csv(idx, result)
                total_initiatives += len(result)
                log(f"  ✓ Found {len(result)} initiative(s) - SAVED to CSV")
                log(f"  Total so far: {total_initiatives}")
            else:
                log(f"  - No initiatives found")
            
            # Delay to avoid rate limits
            time.sleep(0.5)
            
            # Progress checkpoint
            if idx % 10 == 0:
                log(f"\n{'='*80}")
                log(f"CHECKPOINT: {idx}/{len(paragraphs)} paragraphs processed")
                log(f"Total initiatives saved to CSV: {total_initiatives}")
                log(f"{'='*80}\n")
        
        # Final summary
        log("")
        log("="*80)
        log("EXTRACTION COMPLETE")
        log("="*80)
        log(f"Total paragraphs processed: {len(paragraphs)}")
        log(f"Total initiatives saved: {total_initiatives}")
        log(f"Output CSV: {OUTPUT_CSV}")
        log("="*80)
        
        print(f"\n✓✓✓ SUCCESS! {total_initiatives} initiatives saved to CSV")
        print(f"Output: {OUTPUT_CSV}")
        
    except KeyboardInterrupt:
        log("\n⚠ Processing interrupted by user")
        log(f"Initiatives saved so far: {total_initiatives}")
        log(f"Check CSV file: {OUTPUT_CSV}")
    except Exception as e:
        log(f"\n✗ ERROR: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    main()

