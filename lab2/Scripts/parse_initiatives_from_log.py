#!/usr/bin/env python3
"""
Parse the log file to extract all initiatives found by the LLM
Create a proper CSV with one initiative per row
"""

import re
import json
import csv
from pathlib import Path

LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab2/output/progress_log.txt')
OUTPUT_CSV = Path('/Users/simonwang/Documents/Usage/ai7010/lab2/output/initiatives.csv')

def extract_initiatives_from_log():
    """Parse log file and extract all initiatives"""
    
    print("Reading log file...")
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    # The initiatives would be in the API responses
    # Let's look for patterns where initiatives were found
    
    # Since the actual JSON responses might not be in the log,
    # let's try a different approach - look for the response content
    # that would have been saved during processing
    
    # Actually, I realize the script processes and stores in memory,
    # but the log only shows counts. We need to re-extract from the
    # paragraphs ourselves OR modify the script to save intermediate results.
    
    # For now, let's create a note about this limitation
    print("\nIMPORTANT DISCOVERY:")
    print("The log file shows that 138 initiatives were FOUND,")
    print("but the actual initiative data (JSON responses) were stored")
    print("in memory during script execution, not written to the log.")
    print("\nThe script was designed to save all initiatives to CSV at the END,")
    print("but it terminated early due to broken pipe error.")
    print("\nSOLUTION: We need to rerun the script to extract the initiatives.")
    print("\nHowever, I can create a MODIFIED script that saves incrementally...")
    
    return []

if __name__ == "__main__":
    initiatives = extract_initiatives_from_log()
    print(f"\nInitiatives that could be extracted: {len(initiatives)}")

