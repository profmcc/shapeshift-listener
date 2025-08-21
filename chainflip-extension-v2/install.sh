#!/bin/bash

# Chainflip Extension v2 Installation Script
# This script helps install and configure the extension

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Extension details
EXTENSION_NAME="Chainflip Affiliate Tracker v2"
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHROME_EXTENSIONS_URL="chrome://extensions/"

echo -e "${BLUE}🔄 $EXTENSION_NAME Installation Script${NC}"
echo "=========================================="

# Check if we're in the right directory
if [[ ! -f "$EXTENSION_DIR/manifest.json" ]]; then
    echo -e "${RED}❌ Error: manifest.json not found in $EXTENSION_DIR${NC}"
    echo "Please run this script from the extension directory"
    exit 1
fi

echo -e "${GREEN}✅ Extension directory found: $EXTENSION_DIR${NC}"

# Check Chrome installation
check_chrome() {
    if command -v google-chrome &> /dev/null; then
        CHROME_CMD="google-chrome"
        echo -e "${GREEN}✅ Google Chrome found${NC}"
    elif command -v chromium-browser &> /dev/null; then
        CHROME_CMD="chromium-browser"
        echo -e "${GREEN}✅ Chromium found${NC}"
    elif command -v chromium &> /dev/null; then
        CHROME_CMD="chromium"
        echo -e "${GREEN}✅ Chromium found${NC}"
    else
        echo -e "${RED}❌ Chrome/Chromium not found${NC}"
        echo "Please install Google Chrome or Chromium first"
        exit 1
    fi
}

# Validate extension files
validate_extension() {
    echo -e "\n${BLUE}🔍 Validating extension files...${NC}"
    
    required_files=("manifest.json" "content.js" "background.js" "popup.html" "popup.js")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [[ -f "$EXTENSION_DIR/$file" ]]; then
            echo -e "${GREEN}✅ $file${NC}"
        else
            echo -e "${RED}❌ $file (missing)${NC}"
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "\n${RED}❌ Missing required files: ${missing_files[*]}${NC}"
        echo "Please ensure all required files are present"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All required files present${NC}"
}

# Check manifest.json syntax
check_manifest() {
    echo -e "\n${BLUE}🔍 Checking manifest.json...${NC}"
    
    if command -v python3 &> /dev/null; then
        if python3 -m json.tool "$EXTENSION_DIR/manifest.json" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ manifest.json is valid JSON${NC}"
        else
            echo -e "${RED}❌ manifest.json has invalid JSON syntax${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Python3 not available, skipping JSON validation${NC}"
    fi
}

# Create placeholder icons if missing
create_icons() {
    echo -e "\n${BLUE}🎨 Checking icons...${NC}"
    
    if [[ ! -d "$EXTENSION_DIR/icons" ]]; then
        mkdir -p "$EXTENSION_DIR/icons"
        echo -e "${YELLOW}⚠️  Created icons directory${NC}"
    fi
    
    # Check if icons exist
    icon_files=("icon16.png" "icon48.png" "icon128.png")
    missing_icons=()
    
    for icon in "${icon_files[@]}"; do
        if [[ -f "$EXTENSION_DIR/icons/$icon" ]]; then
            echo -e "${GREEN}✅ $icon${NC}"
        else
            echo -e "${YELLOW}⚠️  $icon (missing - will use default)${NC}"
            missing_icons+=("$icon")
        fi
    done
    
    if [[ ${#missing_icons[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}⚠️  Some icons are missing. The extension will work but may show default icons.${NC}"
        echo "You can add custom icons to the icons/ directory:"
        echo "  - icon16.png (16x16 pixels)"
        echo "  - icon48.png (48x48 pixels)"
        echo "  - icon128.png (128x128 pixels)"
    fi
}

# Installation instructions
show_instructions() {
    echo -e "\n${BLUE}📋 Installation Instructions${NC}"
    echo "================================"
    echo -e "${GREEN}1. Open Chrome and go to: ${CHROME_EXTENSIONS_URL}${NC}"
    echo -e "${GREEN}2. Enable 'Developer mode' (toggle in top right)${NC}"
    echo -e "${GREEN}3. Click 'Load unpacked' and select:${NC}"
    echo -e "${YELLOW}   $EXTENSION_DIR${NC}"
    echo -e "${GREEN}4. Pin the extension to your toolbar${NC}"
    echo -e "${GREEN}5. Navigate to https://app.chainflip.io to test${NC}"
}

# Open Chrome extensions page
open_chrome_extensions() {
    echo -e "\n${BLUE}🚀 Opening Chrome Extensions page...${NC}"
    
    if [[ -n "$CHROME_CMD" ]]; then
        echo -e "${GREEN}Opening Chrome extensions page...${NC}"
        "$CHROME_CMD" "$CHROME_EXTENSIONS_URL" &
    else
        echo -e "${YELLOW}Please manually open: $CHROME_EXTENSIONS_URL${NC}"
    fi
}

# Main installation flow
main() {
    check_chrome
    validate_extension
    check_manifest
    create_icons
    
    echo -e "\n${GREEN}🎉 Extension validation complete!${NC}"
    
    show_instructions
    
    echo -e "\n${BLUE}Would you like to open the Chrome Extensions page now? (y/N)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        open_chrome_extensions
    fi
    
    echo -e "\n${GREEN}✅ Installation script completed successfully!${NC}"
    echo -e "${BLUE}📁 Extension location: $EXTENSION_DIR${NC}"
    echo -e "${BLUE}🔗 Chrome Extensions: $CHROME_EXTENSIONS_URL${NC}"
}

# Run main function
main "$@"


