#!/bin/bash

# DeFi Data Snatcher v15 - Simple Text Export Installation Script
echo "📝 Installing DeFi Data Snatcher v15 - Simple Text Export Version"
echo "================================================================="

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "❌ Error: manifest.json not found. Please run this script from the defi-data-snatcher-v15 directory."
    exit 1
fi

# Check if manifest.json has v15
if ! grep -q '"name": "DeFi Data Snatcher v15"' manifest.json; then
    echo "❌ Error: This doesn't appear to be v15. Please check your directory."
    exit 1
fi

echo "✅ Found v15 extension files"
echo ""

# Display extension information
echo "📋 Extension Details:"
echo "   Name: DeFi Data Snatcher v15"
echo "   Version: 15.0.0"
echo "   Description: Simple text-based export version that bypasses complex CSV processing to avoid null reference errors"
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
echo "5. Extension should appear as 'DeFi Data Snatcher v15'"
echo ""

# Testing instructions
echo "🧪 Testing Instructions:"
echo "========================"
echo ""
echo "1. Go to Butterswap explorer or similar DeFi platform"
echo "2. Navigate to a page with transaction tables"
echo "3. Click the extension icon (should show 'Simple Text Export v15')"
echo "4. Click '🔍 Scan Table & Extract Links' to detect table"
echo "5. Click '📝 Export Simple Text' to download .txt file"
echo "6. Click '📄 Export Raw Data' to download .json file"
echo "7. **v15 ADVANTAGE**: No CSV processing errors!"
echo ""

# Expected results
echo "🎯 Expected Results:"
echo "===================="
echo ""
echo "✅ Table data populated with actual transaction information"
echo "✅ Full hyperlinks generated for every transaction hash"
echo "✅ Simple text export works without any errors"
echo "✅ JSON export works without any errors"
echo "✅ No CSV processing - completely bypassed"
echo ""

# v15 specific features
echo "🆕 v15 New Features:"
echo "===================="
echo ""
echo "📝 Simple Text Export: Human-readable text format without CSV processing"
echo "📄 JSON Raw Data Export: Complete data structure without processing"
echo "🔗 Hyperlink Generation: Guaranteed transaction link creation"
echo "🚫 No CSV Errors: Completely bypasses CSV generation"
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
echo "  - Check if current domain is supported"
echo "  - Verify hash format in table"
echo ""
echo "If export fails (v15 should fix this):"
echo "  - Ensure table has been scanned first"
echo "  - Check browser download settings"
echo "  - Verify data is present in results section"
echo "  - **v15 advantage**: No CSV processing errors"
echo ""

echo "📝 v15 is specifically designed to prioritize hyperlink generation while providing reliable export through simple text and JSON formats!"
echo ""
echo "Installation script complete. Follow the instructions above to install and test the extension."
