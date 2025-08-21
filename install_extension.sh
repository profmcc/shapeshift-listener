#!/bin/bash

# DeFi Data Snatcher Extension Installer
echo "🚀 DeFi Data Snatcher Extension Installer"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "manifest.json" ] || [ ! -f "content.js" ]; then
    echo "❌ Error: Please run this script from the extension directory"
    echo "   Make sure manifest.json and content.js are present"
    exit 1
fi

# Check if icons directory exists
if [ ! -d "icons" ]; then
    echo "❌ Error: Icons directory not found"
    echo "   Please run create_icons.py first to generate icons"
    exit 1
fi

# Check for required files
required_files=("manifest.json" "background.js" "content.js" "popup.html" "popup.js")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Error: Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Check for PNG icons
png_icons=("icons/icon16.png" "icons/icon32.png" "icons/icon48.png" "icons/icon128.png")
svg_icons=("icons/icon16.svg" "icons/icon32.svg" "icons/icon48.svg" "icons/icon128.svg")
missing_png=()
has_svg=false

for icon in "${png_icons[@]}"; do
    if [ ! -f "$icon" ]; then
        missing_png+=("$icon")
    fi
done

for icon in "${svg_icons[@]}"; do
    if [ -f "$icon" ]; then
        has_svg=true
        break
    fi
done

if [ ${#missing_png[@]} -ne 0 ]; then
    echo "⚠️  Warning: Some PNG icons are missing:"
    for icon in "${missing_png[@]}"; do
        echo "   - $icon"
    done
    
    if [ "$has_svg" = true ]; then
        echo ""
        echo "📝 You have SVG icons. To convert them to PNG:"
        echo "   1. Use online converters like:"
        echo "      - https://convertio.co/svg-png/"
        echo "      - https://cloudconvert.com/svg-to-png"
        echo "   2. Or use command line tools:"
        echo "      - ImageMagick: convert icon.svg icon.png"
        echo "      - Inkscape: inkscape icon.svg --export-png=icon.png"
        echo ""
        echo "   After converting, run this script again."
        exit 1
    else
        echo "❌ No SVG icons found either. Please run create_icons.py first."
        exit 1
    fi
fi

echo "✅ All required files found!"
echo ""

# Show installation instructions
echo "📋 Installation Instructions:"
echo "1. Open Chrome and go to chrome://extensions/"
echo "2. Enable 'Developer mode' in the top right corner"
echo "3. Click 'Load unpacked'"
echo "4. Select this directory: $(pwd)"
echo "5. The extension should appear in your toolbar"
echo ""

# Check if we can open Chrome
if command -v google-chrome &> /dev/null; then
    echo "🌐 Would you like to open Chrome extensions page now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        google-chrome chrome://extensions/
        echo "✅ Chrome extensions page opened!"
    fi
elif command -v open &> /dev/null; then
    echo "🌐 Would you like to open Chrome extensions page now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        open -a "Google Chrome" chrome://extensions/
        echo "✅ Chrome extensions page opened!"
    fi
fi

echo ""
echo "🎉 Extension installation guide complete!"
echo "💡 Tip: After loading the extension, visit any DeFi platform and click the extension icon to start capturing transaction tables!"

