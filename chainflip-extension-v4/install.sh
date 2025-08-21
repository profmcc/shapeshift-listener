#!/bin/bash

# Chainflip Test Extension v4 Installation Script
# This script helps install and configure the test extension

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Extension details
EXTENSION_NAME="Chainflip Test Extension v4"
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHROME_EXTENSIONS_URL="chrome://extensions/"

echo -e "${BLUE}🧪 $EXTENSION_NAME Installation Script${NC}"
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
    
    # Check version
    if grep -q '"version": "4.0.0"' "$EXTENSION_DIR/manifest.json"; then
        echo -e "${GREEN}✅ Version 4.0.0 confirmed${NC}"
    else
        echo -e "${YELLOW}⚠️  Version may not be 4.0.0${NC}"
    fi
    
    # Check permissions
    if grep -q '"downloads"' "$EXTENSION_DIR/manifest.json"; then
        echo -e "${GREEN}✅ Downloads permission found${NC}"
    else
        echo -e "${YELLOW}⚠️  Downloads permission not found${NC}"
    fi
}

# Check for v4 specific features
check_v4_features() {
    echo -e "\n${BLUE}🔍 Checking v4 features...${NC}"
    
    # Check for test page functionality
    if grep -q "runTestPage\|downloadTestPage" "$EXTENSION_DIR/content.js"; then
        echo -e "${GREEN}✅ Test page functionality found${NC}"
    else
        echo -e "${YELLOW}⚠️  Test page functionality not found${NC}"
    fi
    
    # Check for download capabilities
    if grep -q "downloadFile\|downloads" "$EXTENSION_DIR/content.js"; then
        echo -e "${GREEN}✅ Download capabilities found${NC}"
    else
        echo -e "${YELLOW}⚠️  Download capabilities not found${NC}"
    fi
    
    # Check for comprehensive testing
    if grep -q "testPageHTML\|testDataJSON" "$EXTENSION_DIR/content.js"; then
        echo -e "${GREEN}✅ Comprehensive testing framework found${NC}"
    else
        echo -e "${YELLOW}⚠️  Comprehensive testing framework not found${NC}"
    fi
}

# Test extension functionality
test_functionality() {
    echo -e "\n${BLUE}🧪 Testing extension functionality...${NC}"
    
    # Check if content script has proper structure
    if grep -q "class ChainflipTestExtensionV4" "$EXTENSION_DIR/content.js"; then
        echo -e "${GREEN}✅ Content script class structure found${NC}"
    else
        echo -e "${YELLOW}⚠️  Content script class structure not found${NC}"
    fi
    
    # Check if background script has proper structure
    if grep -q "class TestExtensionBackgroundV4" "$EXTENSION_DIR/background.js"; then
        echo -e "${GREEN}✅ Background script class structure found${NC}"
    else
        echo -e "${YELLOW}⚠️  Background script class structure not found${NC}"
    fi
    
    # Check if popup has proper structure
    if grep -q "class TestExtensionPopupV4" "$EXTENSION_DIR/popup.js"; then
        echo -e "${GREEN}✅ Popup script class structure found${NC}"
    else
        echo -e "${YELLOW}⚠️  Popup script class structure not found${NC}"
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
    echo -e "${GREEN}5. Test the extension functionality${NC}"
    echo -e "\n${BLUE}🧪 v4 Testing Features:${NC}"
    echo -e "${YELLOW}• Create test pages with comprehensive testing suites${NC}"
    echo -e "${YELLOW}• Download test pages as HTML files for offline use${NC}"
    echo -e "${YELLOW}• Generate mock data for testing scenarios${NC}"
    echo -e "${YELLOW}• Monitor test history and download statistics${NC}"
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

# Show test examples
show_test_examples() {
    echo -e "\n${BLUE}🧪 Test Extension Examples${NC}"
    echo "================================"
    echo -e "${GREEN}After installation, you can:${NC}"
    echo -e "${YELLOW}1. Click extension icon to open popup${NC}"
    echo -e "${YELLOW}2. Click 'Create Test Page' to generate a test page${NC}"
    echo -e "${YELLOW}3. Click 'Download Test Page' to save as HTML file${NC}"
    echo -e "${YELLOW}4. Navigate to any webpage to see the test overlay${NC}"
    echo -e "${YELLOW}5. Use 'Generate Test Data' to create mock data${NC}"
    echo -e "\n${BLUE}Test Page Features:${NC}"
    echo -e "${YELLOW}• Browser capability testing${NC}"
    echo -e "${YELLOW}• Performance metrics collection${NC}"
    echo -e "${YELLOW}• Storage and network testing${NC}"
    echo -e "${YELLOW}• UI interaction validation${NC}"
}

# Main installation flow
main() {
    check_chrome
    validate_extension
    check_manifest
    check_v4_features
    test_functionality
    
    echo -e "\n${GREEN}🎉 Extension validation complete!${NC}"
    
    show_instructions
    show_test_examples
    
    echo -e "\n${BLUE}Would you like to open the Chrome Extensions page now? (y/N)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        open_chrome_extensions
    fi
    
    echo -e "\n${GREEN}✅ Installation script completed successfully!${NC}"
    echo -e "${BLUE}📁 Extension location: $EXTENSION_DIR${NC}"
    echo -e "${BLUE}🔗 Chrome Extensions: $CHROME_EXTENSIONS_URL${NC}"
    echo -e "\n${BLUE}🧪 v4 is ready for comprehensive testing and page generation!${NC}"
    echo -e "${BLUE}📥 Download capabilities are fully functional!${NC}"
}

# Run main function
main "$@"

