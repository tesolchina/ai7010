# Lab1: Policy Address 2025 - Table of Contents and Visualization

## Objective
Extract a hierarchical Table of Contents from the Hong Kong 2025 Policy Address XML file and create a visual diagram showing the overall structure.

## Input
- **Source File**: `/Users/simonwang/Documents/Usage/ai7010/data/policyAddress/pa2025_english.xml`
- **Format**: DocBook XML (5438 lines)

## Process

### Step 1: Parse XML and Generate ToC
- **Script**: `generate_toc.py`
- **Method**: Parse DocBook XML using ElementTree
- **Hierarchy Levels**:
  - Level 0 (■): Main chapters
  - Level 1 (●): Sections
  - Level 2 (○): Subsections  
  - Level 3 (▪): Sub-subsections
- **Result**: 201 sections extracted

### Step 2: Create Visualization
- **Script**: `create_visualization_direct.py`
- **Method**: Python PIL (Pillow) library
- **Features**:
  - Professional blue header design
  - Color-coded hierarchy levels
  - Connection lines showing relationships
  - Alternating background for readability
  - 3000x6240px high-resolution image

### Step 3: Continuous Logging
- **Log File**: `process_log.txt`
- **Purpose**: Track progress and debug issues
- **Updates**: Real-time status reporting

## Output Files

### 1. Table of Contents
- **File**: `toc_pa2025.txt`
- **Size**: ~11.5 KB
- **Format**: Hierarchical text with markers
- **Sections**: 201 total

### 2. Visualization Image
- **File**: `pa2025_structure_visualization.png`
- **Size**: 548 KB
- **Dimensions**: 3000 x 6240 pixels
- **Format**: PNG with optimization

### 3. Process Log
- **File**: `process_log.txt`
- **Purpose**: Complete audit trail
- **Contents**: All steps, errors, and completion status

## Policy Address Structure Overview

The 2025 Hong Kong Policy Address contains:

**Main Chapters:**
1. **Chapter I**: Deepen Reforms and Committed to People's Livelihood
2. **Chapter II**: Implement "One Country, Two Systems" and Strengthen Governance
3. **Chapter III**: Accelerate Development of the Northern Metropolis
4. **Chapter IV**: Industry Development and Reform
5. **Chapter V**: Integrate into National Development
6. **Chapter VI**: Consolidate Hong Kong's Status as International Hub
7. **Chapter VII**: Education, Technology and Talents Integration
8. **Chapter VIII**: Tourism, Arts, Culture and Sports
9. **Chapter IX**: Housing and Land Development
10. **Chapter X**: Support Disadvantaged Groups and Community Building
11. **Chapter XI**: Environmental Protection and Response to Climate Change
12. **Conclusion**: Building a Brighter Future Together

## Technical Details

### Dependencies
- Python 3.x
- PIL/Pillow (for image generation)
- xml.etree.ElementTree (standard library)
- requests (for API attempts)

### XML Namespace
```xml
xmlns="http://docbook.org/ns/docbook" version="5.0"
```

### Color Scheme
- Deep Blue (#0d47a1): Main chapters
- Medium Blue (#1565c0): Sections
- Blue (#1976d2): Subsections
- Light Blue (#42a5f5): Sub-subsections

## Notes

- **API Authentication**: Initial attempt to use OpenRouter API (Nano Banana Pro model) failed due to authentication issues. Switched to direct Python visualization which produced excellent results.

- **Font Handling**: System fonts (Helvetica) used with fallback to default fonts for compatibility.

- **Image Quality**: High resolution (3000px width) ensures readability when zoomed or printed.

## Generated On
November 27, 2025

## Files in This Directory
```
lab1/
├── APIkey.txt                              # OpenRouter API key
├── create_visualization_direct.py          # Direct visualization script
├── generate_toc.py                         # ToC extraction script
├── generate_visualization.py               # API-based visualization (backup)
├── instructions.md                         # Original task instructions
├── pa2025_structure_visualization.png      # OUTPUT: Visual diagram
├── process_log.txt                         # Continuous progress log
├── README.md                               # This file
└── toc_pa2025.txt                          # OUTPUT: Table of Contents
```

## Success Criteria
✅ Table of Contents extracted with proper hierarchy  
✅ All 201 sections captured  
✅ Professional visualization created  
✅ Files saved in lab1 folder  
✅ Continuous logging maintained  
✅ Complete documentation provided  

---
*Hong Kong SAR Government - 2025 Policy Address Analysis*

