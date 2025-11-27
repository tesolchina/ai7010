#!/usr/bin/env python3
"""
Use OpenRouter API to correct OCR errors and add punctuation to Chinese text
Input: /Users/simonwang/Documents/Usage/ai7010/lab5/output_vertical_chinese.md
Output: Corrected markdown file with proper punctuation
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Add parent directory to path to import api_key_loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_key_loader import load_api_key

def read_ocr_output(file_path):
    """Read the OCR output file and extract the text content"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Reading OCR output from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the continuous text section (this is the main text we want to correct)
    if "## Continuous Text (All Columns)" in content:
        parts = content.split("## Continuous Text (All Columns)")
        if len(parts) > 1:
            text = parts[1].strip()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracted {len(text)} characters of text")
            return text
    
    # Fallback: return the whole content
    return content

def correct_text_with_llm(text, api_key):
    """Send text to OpenRouter API for correction with retry logic"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sending text to OpenRouter API for correction...")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Chinese OCR Text Correction"
    }
    
    prompt = f"""你是一位精通中文的文字編輯專家。請幫我修正以下從舊文獻OCR識別出來的繁體中文文本。

這段文本存在以下問題：
1. OCR識別錯誤（將相似字誤認）
2. 缺少標點符號
3. 可能有一些繁體字識別錯誤

請你：
1. 根據上下文修正OCR錯誤的字詞
2. 添加適當的標點符號（句號、逗號、頓號等）
3. 保持原文的意思和順序
4. 如果有明顯的繁簡混用，請統一為繁體中文
5. 修正後的文本應該通順易讀

原始OCR文本：

{text}

請只返回修正後的文本，不要加任何說明或註解。"""

    # Try different models (avoiding OpenAI for Hong Kong)
    models = [
        "x-ai/grok-beta",  # Grok model
        "anthropic/claude-3-5-sonnet",  # Claude 3.5 Sonnet
        "anthropic/claude-3-haiku",  # Claude 3 Haiku (cheaper)
        "google/gemini-pro-1.5",  # Gemini Pro
        "google/gemini-2.0-flash-exp:free",  # Free Gemini
        "meta-llama/llama-3.2-3b-instruct:free",  # Free Llama
    ]
    
    for model in models:
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Trying model: {model}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                corrected_text = result['choices'][0]['message']['content'].strip()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Success with {model}!")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Received corrected text ({len(corrected_text)} characters)")
                return corrected_text
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Unexpected response format from {model}")
                continue
                
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 429:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {model} rate-limited, trying next model...")
                elif status_code == 402:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {model} requires payment, trying next model...")
                elif status_code == 403:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {model} forbidden (insufficient credits), trying next model...")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error with {model}: {e}")
                time.sleep(2)  # Brief delay before trying next model
                continue
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error with {model}: {e}")
                continue
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ All models failed or rate-limited")
    return None

def save_corrected_text(corrected_text, output_path, original_path):
    """Save the corrected text to a new markdown file"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Saving corrected text to: {output_path}")
    
    markdown_content = []
    markdown_content.append("# 修正後的文本 - Corrected OCR Text\n\n")
    markdown_content.append(f"**原始檔案 / Original File:** `{os.path.basename(original_path)}`\n\n")
    markdown_content.append(f"**修正日期 / Correction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    markdown_content.append(f"**處理方式 / Processing:** OpenRouter API (LLM correction)\n\n")
    markdown_content.append("---\n\n")
    markdown_content.append("## 修正後的文本 / Corrected Text\n\n")
    markdown_content.append(corrected_text)
    markdown_content.append("\n")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(markdown_content)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Corrected text saved successfully!")
    print(f"\nOutput file: {output_path}")

def main():
    """Main processing function"""
    print("="*70)
    print("OCR Text Correction with LLM (OpenRouter API)")
    print("="*70)
    
    # Configuration
    input_file = "/Users/simonwang/Documents/Usage/ai7010/lab5/output_vertical_chinese.md"
    output_file = "/Users/simonwang/Documents/Usage/ai7010/lab5/output_corrected.md"
    
    # Load API key from central APIkey.md file
    try:
        api_key = load_api_key("openRouter")
        print(f"✓ API key loaded from APIkey.md")
    except Exception as e:
        print(f"✗ Error loading API key: {e}")
        return
    
    # Step 1: Read OCR output
    text = read_ocr_output(input_file)
    
    if not text:
        print("❌ Error: No text found in input file")
        return
    
    print(f"\n{'='*70}")
    print(f"Preview of text to be corrected (first 200 chars):")
    print(f"{'='*70}")
    print(text[:200] + "...")
    print(f"{'='*70}\n")
    
    # Step 2: Correct text with LLM
    corrected_text = correct_text_with_llm(text, api_key)
    
    if not corrected_text:
        print("\n❌ Error: Failed to get corrected text from API")
        return
    
    print(f"\n{'='*70}")
    print(f"Preview of corrected text (first 200 chars):")
    print(f"{'='*70}")
    print(corrected_text[:200] + "...")
    print(f"{'='*70}\n")
    
    # Step 3: Save corrected text
    save_corrected_text(corrected_text, output_file, input_file)
    
    print(f"\n{'='*70}")
    print("✅ Processing Complete!")
    print(f"{'='*70}")
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

