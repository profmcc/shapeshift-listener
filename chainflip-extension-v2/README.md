# Chainflip Affiliate Tracker v2

A Chrome extension to track ShapeShift affiliate transactions on the Chainflip protocol.

## 🚀 Features

- **Real-time Transaction Tracking**: Automatically detects and tracks transactions on Chainflip
- **Affiliate Detection**: Identifies ShapeShift affiliate transactions
- **Data Export**: Export transaction data in JSON or CSV format
- **Beautiful UI**: Modern, responsive popup interface with real-time statistics
- **Persistent Storage**: Saves transaction data locally using Chrome storage
- **Auto-cleanup**: Automatically removes old transactions to maintain performance

## 📁 File Structure

```
chainflip-extension-v2/
├── manifest.json          # Extension manifest (Manifest V3)
├── content.js            # Content script injected into Chainflip pages
├── background.js         # Service worker for background tasks
├── popup.html           # Extension popup interface
├── popup.js             # Popup functionality and UI logic
├── icons/               # Extension icons (16x16, 48x48, 128x128)
└── README.md            # This file
```

## 🔧 Installation

### Development Mode

1. **Clone or download** this extension folder
2. **Open Chrome** and navigate to `chrome://extensions/`
3. **Enable Developer mode** (toggle in top right)
4. **Click "Load unpacked"** and select the `chainflip-extension-v2` folder
5. **Pin the extension** to your toolbar for easy access

### Production Installation

1. **Package the extension** (optional - for distribution)
2. **Drag and drop** the `.crx` file into Chrome extensions page
3. **Confirm installation** when prompted

## 🎯 Usage

### Basic Tracking

1. **Navigate to** [app.chainflip.io](https://app.chainflip.io)
2. **Click the extension icon** to open the popup
3. **View real-time statistics** including:
   - Total transactions tracked
   - Total volume
   - Affiliate transaction count
   - Last update time

### Data Management

- **Export Data**: Click export buttons to download JSON or CSV files
- **Refresh Data**: Click refresh to get latest data from active tabs
- **Clear Data**: Remove all stored transaction data (irreversible)

### Affiliate Detection

The extension automatically detects ShapeShift affiliate transactions by:
- Monitoring transaction addresses
- Checking for affiliate address patterns
- Highlighting affiliate transactions in the UI

## ⚙️ Configuration

### Affiliate Address

Update the affiliate address in `content.js`:

```javascript
this.affiliateAddress = '0x0000000000000000000000000000000000000000'; // Replace with actual ShapeShift address
```

### Tracking Settings

Modify tracking behavior in `background.js`:

```javascript
'settings': {
    'auto_track': true,        // Enable/disable automatic tracking
    'notifications': true,     // Show affiliate transaction notifications
    'export_format': 'json'    // Default export format
}
```

## 🔍 How It Works

### Content Script (`content.js`)

- **Injected** into Chainflip pages
- **Monitors DOM changes** for new transaction data
- **Extracts transaction details** from page elements
- **Detects affiliate involvement** using address patterns
- **Saves data** to Chrome storage

### Background Service Worker (`background.js`)

- **Manages data storage** and retrieval
- **Handles export operations** (JSON/CSV)
- **Performs data cleanup** (removes old transactions)
- **Coordinates** between content script and popup

### Popup Interface (`popup.html` + `popup.js`)

- **Displays statistics** and transaction data
- **Provides user controls** for data management
- **Shows recent transactions** with affiliate badges
- **Handles user interactions** and data operations

## 📊 Data Structure

Each tracked transaction includes:

```javascript
{
    hash: "0x...",              // Transaction hash
    timestamp: 1234567890,      // Unix timestamp
    url: "https://...",         // Page URL when detected
    protocol: "Chainflip",      // Protocol identifier
    amount: "100.50",           // Transaction amount
    token: "USDC",              // Token symbol
    from: "0x...",              // Sender address
    to: "0x...",                // Recipient address
    status: "Confirmed",        // Transaction status
    isAffiliate: false,         // Affiliate flag
    // ... additional extracted data
}
```

## 🚨 Troubleshooting

### Extension Not Working

1. **Check console errors** in DevTools
2. **Verify permissions** in extension settings
3. **Reload the page** after installation
4. **Check manifest.json** for syntax errors

### No Transactions Detected

1. **Ensure you're on** [app.chainflip.io](https://app.chainflip.io)
2. **Check content script** is injected (console should show "Chainflip Affiliate Tracker v2 loaded")
3. **Verify page structure** matches expected selectors
4. **Check for JavaScript errors** in page console

### Data Export Issues

1. **Verify storage permissions** are granted
2. **Check download folder** permissions
3. **Ensure transactions exist** before exporting
4. **Try different export formats** (JSON vs CSV)

## 🔄 Version History

### v2.0.0 (Current)
- **Complete rewrite** with modern architecture
- **Manifest V3** compliance
- **Enhanced UI** with real-time statistics
- **Improved transaction detection** algorithms
- **Better error handling** and user feedback
- **Data export** in multiple formats
- **Auto-cleanup** for performance

### v1.x (Previous)
- Basic transaction tracking
- Simple popup interface
- Limited functionality

## 🛠️ Development

### Prerequisites

- **Chrome browser** (for testing)
- **Text editor** (VS Code recommended)
- **Basic knowledge** of JavaScript and Chrome Extensions

### Making Changes

1. **Edit source files** as needed
2. **Reload extension** in Chrome (`chrome://extensions/` → reload button)
3. **Test changes** on Chainflip pages
4. **Update version** in `manifest.json` and relevant files

### Testing

1. **Load extension** in development mode
2. **Navigate to** Chainflip application
3. **Check console** for extension messages
4. **Test popup functionality** and data export
5. **Verify transaction detection** works correctly

## 📝 License

This extension is provided as-is for educational and development purposes.

## 🤝 Contributing

To contribute improvements:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

## 📞 Support

For issues or questions:
- **Check console logs** for error messages
- **Review this README** for troubleshooting steps
- **Examine the code** for implementation details
- **Create an issue** with detailed problem description

---

**Note**: This extension is designed specifically for tracking ShapeShift affiliate transactions on Chainflip. Modify the affiliate detection logic and addresses as needed for your specific use case.


