#!/usr/bin/env python3
"""
Download 2025 Policy Address XML files (English and Traditional Chinese)
from Hong Kong Government Open Data Portal
"""

import requests
import os
from pathlib import Path

# Define URLs for 2025 Policy Address XML files
DOWNLOAD_URLS = {
    'english': 'https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Fwww.ceo.gov.hk%2Fpublic%2Fopen-data%2Fen%2Fpolicy_address%2Fpa2025.xml',
    'traditional_chinese': 'https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Fwww.ceo.gov.hk%2Fpublic%2Fopen-data%2Ftc%2Fpolicy_address%2Fpa2025.xml'
}

# Output directory
OUTPUT_DIR = Path('/Users/simonwang/Documents/Usage/ai7010/data/policyAddress')

def download_file(url, filename):
    """
    Download a file from the given URL and save it to the output directory
    
    Args:
        url (str): URL to download from
        filename (str): Name to save the file as
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Save the file
        output_path = OUTPUT_DIR / filename
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content) / 1024  # Size in KB
        print(f"✓ Successfully downloaded {filename} ({file_size:.2f} KB)")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading {filename}: {e}")
        return False
    except IOError as e:
        print(f"✗ Error saving {filename}: {e}")
        return False

def main():
    """Main function to download all Policy Address XML files"""
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    
    # Download files
    results = {}
    
    # English version
    results['english'] = download_file(
        DOWNLOAD_URLS['english'],
        'pa2025_english.xml'
    )
    
    # Traditional Chinese version
    results['traditional_chinese'] = download_file(
        DOWNLOAD_URLS['traditional_chinese'],
        'pa2025_traditional_chinese.xml'
    )
    
    # Summary
    print("=" * 60)
    print("Download Summary:")
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Successfully downloaded: {successful}/{total} files")
    
    if successful == total:
        print("\n✓ All files downloaded successfully!")
        print(f"Files saved to: {OUTPUT_DIR}")
    else:
        print("\n⚠ Some files failed to download. Please check the errors above.")

if __name__ == "__main__":
    main()

