#!/usr/bin/env python3
"""
Extract initiatives from incomplete processing run
Parse the log file and create CSV with current results
"""

import re
import csv
from pathlib import Path

LOG_FILE = Path('/Users/simonwang/Documents/Usage/ai7010/lab2/output/progress_log.txt')
OUTPUT_CSV = Path('/Users/simonwang/Documents/Usage/ai7010/lab2/output/initiatives_partial.csv')

# Read log file
print("Reading log file...")
with open(LOG_FILE, 'r', encoding='utf-8') as f:
    log_content = f.read()

# Extract total initiatives count
match = re.search(r'Total initiatives so far: (\d+)', log_content)
if match:
    total_found = match.group(1)
    print(f"Total initiatives mentioned in log: {total_found}")

# Find paragraphs processed
processed_match = re.findall(r'Paragraph (\d+)/470', log_content)
if processed_match:
    last_para = max([int(x) for x in processed_match])
    print(f"Last paragraph processed: {last_para}")

print(f"\nSince the log shows initiatives were found but script terminated,")
print(f"we'll create a summary CSV based on what was processed.")
print(f"\nNote: The actual initiative details are in the LLM responses,")
print(f"which would need to be re-extracted by rerunning the script.")

# Create summary CSV
summary_data = [
    {
        'Status': 'Incomplete Processing',
        'Paragraphs Processed': f'{last_para}/470 ({last_para/470*100:.1f}%)',
        'Initiatives Found': f'~{total_found} (approximate)',
        'Next Steps': 'Rerun script to complete extraction or process remaining paragraphs'
    }
]

with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Status', 'Paragraphs Processed', 'Initiatives Found', 'Next Steps']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(summary_data[0])

print(f"\n✓ Summary CSV created: {OUTPUT_CSV}")

