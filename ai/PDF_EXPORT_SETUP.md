# PDF Export Setup Guide

## Overview

The PDF export now uses **LibreOffice headless mode** to convert PPTX to PDF, which preserves:
- ✅ Template designs and themes
- ✅ All formatting (fonts, colors, styles)
- ✅ Image positioning and sizing
- ✅ Slide layouts
- ✅ Everything exactly as it appears in PPTX

## Installation

### Option 1: LibreOffice (Recommended - Preserves Templates)

**Windows:**
1. Download LibreOffice from https://www.libreoffice.org/download/
2. Install LibreOffice (default installation path is fine)
3. The system will automatically detect it

**Linux:**
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**macOS:**
```bash
brew install --cask libreoffice
```

### Option 2: Fallback (ReportLab - Loses Template)

If LibreOffice is not available, the system will automatically fall back to ReportLab, but this will:
- ❌ Lose template designs
- ❌ Lose custom formatting
- ❌ Only preserve text content and basic layout

To install ReportLab fallback:
```bash
pip install reportlab pillow
```

## How It Works

1. **PPTX Generation**: The system first generates the PPTX file with all templates and formatting
2. **LibreOffice Conversion**: Uses LibreOffice headless mode to convert PPTX → PDF
3. **Fallback**: If LibreOffice is not found, falls back to ReportLab (with warning)

## Verification

To verify LibreOffice is installed and working:

**Windows:**
```cmd
"C:\Program Files\LibreOffice\program\soffice.exe" --version
```

**Linux/Mac:**
```bash
soffice --version
```

## Troubleshooting

### Error: "LibreOffice not found"

**Solution:** Install LibreOffice (see Installation section above)

### Error: "LibreOffice conversion timed out"

**Solution:** 
- Check if LibreOffice is running (close any open LibreOffice windows)
- Try again - the conversion should complete in < 60 seconds

### Error: "LibreOffice conversion failed"

**Solution:**
- Check LibreOffice installation
- Ensure you have write permissions in temp directory
- Check system logs for detailed error messages

### PDF doesn't match PPTX exactly

**Possible causes:**
1. LibreOffice is not installed - system is using ReportLab fallback
2. LibreOffice version is outdated - update to latest version
3. Template uses features not supported by LibreOffice (rare)

## API Usage

The export endpoint automatically uses the best available method:

```python
# Export as PDF (will use LibreOffice if available)
POST /slides/{deck_id}/export
{
  "format": "pdf",
  "user_name": "user"
}
```

The system will:
1. Try LibreOffice first (preserves template)
2. Fall back to ReportLab if LibreOffice unavailable (loses template)
3. Return appropriate error if both fail

