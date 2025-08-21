#!/bin/bash

# DeFi Data Snatcher v13 - Hyperlink Focused Installation Script
echo "🔗 Installing DeFi Data Snatcher v13 - Hyperlink Focused Version"
echo "================================================================"

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "❌ Error: manifest.json not found. Please run this script from the defi-data-snatcher-v13 directory."
    exit 1
fi

# Check if manifest.json has v13
if ! grep -q '"name": "DeFi Data Snatcher v13"' manifest.json; then
    echo "❌ Error: This doesn't appear to be v13. Please check your directory."
    exit 1
fi

echo "✅ Found v13 extension files"
echo ""

# Display extension information
echo "📋 Extension Details:"
echo "   Name: DeFi Data Snatcher v13"
echo "   Version: 13.0.0"
echo "   Description: Hyperlink focused version for Butterswap tables with guaranteed transaction link generation"
echo ""

# Check for required files
echo "🔍 Checking required files..."
required_files=("manifest.json" "background.js" "icons/icon16.png" "icons/icon32.png" "icons/icon48.png" "icons/icon128.png")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
        missing_files=true
    fi
done

if [ "$missing_files" = true ]; then
    echo ""
    echo "❌ Some required files are missing. Please ensure all files are present."
    exit 1
fi

echo ""
echo "✅ All required files found"
echo ""

# Installation instructions
echo "🚀 Installation Instructions:"
echo "=============================="
echo ""
echo "1. Open Chrome and go to: chrome://extensions/"
echo "2. Enable 'Developer mode' (toggle in top right)"
echo "3. Click 'Load unpacked'"
echo "4. Select this directory: $(pwd)"
echo "5. Extension should appear as 'DeFi Data Snatcher v13'"
echo ""

# Testing instructions
echo "🧪 Testing Instructions:"
echo "========================"
echo ""
echo "1. Go to Butterswap explorer or similar DeFi platform"
echo "2. Navigate to a page with transaction tables"
echo "3. Click the extension icon (should show 'Hyperlink Focused v13')"
echo "4. Click '🔍 Scan Table & Extract Links' to detect table"
echo "5. Click '🔗 Extract All Transaction Links' to generate links"
echo "6. Click '📊 Export Clean CSV with Links' to download data"
echo ""

# Expected results
echo "🎯 Expected Results:"
echo "===================="
echo ""
echo "✅ Table data populated with actual transaction information"
echo "✅ Full hyperlinks generated for every transaction hash"
echo "✅ CSV export contains clean data and working links"
echo "✅ No weird formatting - just clean, usable data"
echo ""

# Troubleshooting
echo "🚨 Troubleshooting:"
echo "==================="
echo ""
echo "If extension doesn't work:"
echo "  - Check Chrome console for errors"
echo "  - Verify extension is loaded in chrome://extensions/"
echo "  - Reload the extension if needed"
echo "  - Ensure page has transaction tables"
echo ""
echo "If no hyperlinks generated:"
echo "  - Ensure table contains hash data (0x...)"
echo "  - Try 'Extract All Transaction Links' button"
echo "  - Check if current domain is supported"
echo ""

echo "🔗 v13 is specifically designed to prioritize hyperlink generation while maintaining clean, readable data format!"
echo ""
echo "Installation script complete. Follow the instructions above to install and test the extension."
