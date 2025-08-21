# DeFi Data Snatcher 🚀

A clever Chrome extension for capturing crypto transaction tables from various DeFi platforms with intelligent parsing and export capabilities.

## ✨ Features

- **Smart Table Detection**: Automatically identifies transaction tables on any DeFi platform
- **Intelligent Parsing**: Parses complex transaction data including:
  - Platform names (ButterSwap, OKX, BlazPay, etc.)
  - Chain information and addresses
  - Token amounts and symbols
  - Transaction status and timing
- **Visual Feedback**: Highlights clickable tables with animated indicators
- **Data Preview**: Shows captured data in a beautiful preview window
- **CSV Export**: Export all captured transactions to CSV format
- **Cross-Platform**: Works on any website with transaction tables

## 🎯 How It Works

1. **Click the Extension Icon**: Opens the popup interface
2. **Start Capturing**: Click "Start Capturing" to activate table detection mode
3. **Select Table**: Click on any transaction table you want to capture
4. **Automatic Parsing**: The extension intelligently parses the table data
5. **Preview & Export**: Review captured data and export to CSV

## 🔧 Installation

### Method 1: Load Unpacked Extension (Recommended for Development)

1. Download or clone this repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the extension folder
5. The extension icon should appear in your toolbar

### Method 2: Convert SVGs to PNGs First

The extension requires PNG icons. Convert the SVG files to PNG:

```bash
# Using ImageMagick
convert icons/icon16.svg icons/icon16.png
convert icons/icon32.svg icons/icon32.png
convert icons/icon48.svg icons/icon48.png
convert icons/icon128.svg icons/icon128.png

# Or using online converters like:
# - https://convertio.co/svg-png/
# - https://cloudconvert.com/svg-to-png
```

## 📊 Supported Data Formats

The extension can parse transaction tables with various formats:

### Example Input:
```
Project     From                                    To                                      Status      Time
butterswap  chain 0xd57f...e1c9f token 0.1305 WETH chain 0xc510...b4089 token 0.713 BNB  Completed   1 minute
okx         chain 0x30b7...0c59f token 0.275 BNB   chain 0xf30d...3681d token 0.05 ETH     Completed   1 minute
```

### Parsed Output:
- **Platform**: butterswap, okx
- **From Chain**: 0xd57f...e1c9f, 0x30b7...0c59f
- **From Token**: 0.1305 WETH, 0.275 BNB
- **To Chain**: 0xc510...b4089, 0xf30d...3681d
- **To Token**: 0.713 BNB, 0.05 ETH
- **Status**: Completed
- **Time**: 1 minute

## 🎨 UI Features

- **Draggable Interface**: Move the floating UI anywhere on the page
- **Visual Indicators**: Tables are highlighted with green borders and "Click to capture!" indicators
- **Hover Effects**: Interactive feedback when hovering over tables
- **Data Preview**: Beautiful modal showing captured transaction data
- **Real-time Stats**: Live counter of captured transactions

## 🚀 Usage Examples

### ButterSwap Explorer
1. Navigate to [https://explorer.butterswap.io/en](https://explorer.butterswap.io/en)
2. Click the extension icon
3. Click "Start Capturing"
4. Click on the transaction table
5. Export the captured data

### Any DeFi Platform
The extension works on any website with transaction tables:
- Chainflip
- Thorchain
- CoW Swap
- 0x Protocol
- And many more!

## 🔍 Technical Details

- **Manifest Version**: 3 (Chrome Extension Manifest V3)
- **Permissions**: activeTab, scripting, storage
- **Content Scripts**: Automatically injected on all websites
- **Background Script**: Service worker for extension management
- **Popup Interface**: Clean, modern UI for extension controls

## 🛠️ Development

### File Structure
```
defi-data-snatcher/
├── manifest.json          # Extension configuration
├── background.js          # Background service worker
├── content.js            # Content script (main functionality)
├── popup.html            # Extension popup interface
├── popup.js              # Popup script logic
├── icons/                # Extension icons
│   ├── icon16.svg        # 16x16 icon
│   ├── icon32.svg        # 32x32 icon
│   ├── icon48.svg        # 48x48 icon
│   └── icon128.svg       # 128x128 icon
└── README_DEFI_SNATCHER.md
```

### Key Functions

- `startTableCapture()`: Activates table detection mode
- `parseTable()`: Intelligently parses table data
- `parseChainTokenData()`: Extracts chain, address, token, and amount info
- `exportData()`: Exports captured data to CSV
- `showDataPreview()`: Displays captured data in preview modal

## 🐛 Troubleshooting

### Extension Not Working
1. Make sure Developer mode is enabled in Chrome extensions
2. Check the browser console for error messages
3. Refresh the page and try again
4. Ensure all files are in the correct directory structure

### Tables Not Detected
1. The extension looks for `<table>`, `.table`, `[role="table"]` elements
2. Some sites use custom table implementations
3. Try refreshing the page or waiting for dynamic content to load

### Export Issues
1. Make sure you have captured some data first
2. Check browser permissions for file downloads
3. Try clearing browser cache and cookies

## 🔮 Future Enhancements

- **Multiple Export Formats**: JSON, Excel, Google Sheets
- **Data Filtering**: Filter transactions by platform, token, or status
- **Real-time Monitoring**: Continuous table monitoring and updates
- **Custom Parsing Rules**: User-defined parsing patterns
- **Data Validation**: Verify captured data accuracy
- **Batch Processing**: Capture multiple tables at once

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**DeFi Data Snatcher** - Making crypto data capture as easy as a right-click! 💎

