#!/bin/bash

# DeFi Data Snatcher v14 - Hyperlink Focused Installation Script with Null-Safe Export
echo "🔗 Installing DeFi Data Snatcher v14 - Hyperlink Focused Version with Null-Safe Export"
echo "=================================================================================="

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "❌ Error: manifest.json not found. Please run this script from the defi-data-snatcher-v14 directory."
    exit 1
fi

# Check if manifest.json has v14
if ! grep -q '"name": "DeFi Data Snatcher v14"' manifest.json; then
    echo "❌ Error: This doesn't appear to be v14. Please check your directory."
    exit 1
fi

echo "✅ Found v14 extension files"
echo ""

# Display extension information
echo "📋 Extension Details:"
echo "   Name: DeFi Data Snatcher v14"
echo "   Version: 14.0.0"
echo "   Description: Hyperlink focused version for Butterswap tables with guaranteed transaction link generation and null-safe export"
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
echo "5. Extension should appear as 'DeFi Data Snatcher v14'"
echo ""

# Testing instructions
echo "🧪 Testing Instructions:"
echo "========================"
echo ""
echo "1. Go to Butterswap explorer or similar DeFi platform"
echo "2. Navigate to a page with transaction tables"
echo "3. Click the extension icon (should show 'Hyperlink Focused v14')"
echo "4. Click '🔍 Scan Table & Extract Links' to detect table"
echo "5. Click '🔗 Extract All Transaction Links' to generate links"
echo "6. Click '📊 Export Clean CSV with Links' to download data"
echo "7. **v14 FIX**: Export should work without errors - null-safe handling"
echo ""

# Expected results
echo "🎯 Expected Results:"
echo "===================="
echo ""
echo "✅ Table data populated with actual transaction information"
echo "✅ Full hyperlinks generated for every transaction hash"
echo "✅ CSV export contains clean data and working links"
echo "✅ No weird formatting - just clean, usable data"
echo "✅ **v14 NEW**: Export never fails - null-safe handling prevents errors"
echo ""

# v14 specific features
echo "🆕 v14 New Features:"
echo "===================="
echo ""
echo "🔗 Hyperlink Focused: Guaranteed transaction link generation"
echo "🛡️ Null-Safe Export: No more 'Cannot read properties of null' errors"
echo "📊 Clean Data: Normalized text and structured output"
echo "🚀 Streamlined: Single scan button with automatic link extraction"
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
echo "  - Verify hash format in table"
echo ""
echo "If CSV export fails (v14 should fix this):"
echo "  - Ensure table has been scanned first"
echo "  - Check browser download settings"
echo "  - Verify data is present in results section"
echo "  - **v14 fixes**: No more null reference errors"
echo ""

echo "🔗 v14 is specifically designed to prioritize hyperlink generation while maintaining clean, readable data format AND providing error-free CSV export!"
echo ""
echo "Installation script complete. Follow the instructions above to install and test the extension."
