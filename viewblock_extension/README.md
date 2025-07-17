# ViewBlock THORChain Data Capture Extension

A Chrome extension that captures THORChain affiliate transaction data from ViewBlock, including full text from hover tooltips.

## Features

- **Hover Tooltip Capture**: Extracts full text from hover tooltips that show abbreviated data
- **Table Data Extraction**: Captures all transaction data from ViewBlock tables
- **Multi-page Support**: Can capture data from multiple pages automatically
- **Data Export**: Downloads captured data as JSON files
- **Progress Tracking**: Shows real-time progress during multi-page captures

## Installation

### Method 1: Load as Unpacked Extension

1. Download or clone this extension folder
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked" and select the `viewblock_extension` folder
5. The extension should now appear in your extensions list

### Method 2: Build and Install

1. Create the extension folder structure:
   ```
   viewblock_extension/
   ├── manifest.json
   ├── popup.html
   ├── popup.js
   ├── content.js
   ├── background.js
   ├── icon16.png
   ├── icon48.png
   └── icon128.png
   ```

2. Add icon files (you can create simple 16x16, 48x48, and 128x128 pixel PNG files)
3. Follow Method 1 to load the extension

## Usage

1. **Navigate to ViewBlock**: Go to https://viewblock.io/thorchain/txs?affiliate=ss
2. **Open Extension**: Click the extension icon in your Chrome toolbar
3. **Capture Data**:
   - **Capture Current Page**: Extracts data from the current page only
   - **Capture All Pages**: Automatically navigates through all available pages
4. **Download Data**: Click "Download Data" to save as JSON file

## How It Works

### Hover Tooltip Extraction

The extension uses several methods to capture full text from abbreviated data:

1. **Title Attribute**: Checks for `title` attributes on elements
2. **Data Attributes**: Looks for `data-full` or `data-tooltip` attributes
3. **Mouse Events**: Triggers `mouseover` events to show tooltips
4. **Tooltip Detection**: Searches for visible tooltip elements and extracts their text

### Data Processing

The extension processes captured data to extract:

- **Transaction Hash**: Full hash from tooltip
- **Block Height**: Complete block number
- **Timestamp**: Full timestamp information
- **Addresses**: Complete from/to addresses
- **Amounts**: Parsed asset amounts and symbols
- **Affiliate Info**: Automatically set to "ss" for ShapeShift

## Data Format

Captured data is stored in JSON format with the following structure:

```json
{
  "tx_hash": "full_transaction_hash",
  "block_height": "12345678",
  "timestamp": "2025-07-09 10:30:45",
  "from_address": "thor1...",
  "to_address": "thor1...",
  "amount": "1.234 BTC → 0.567 ETH",
  "from_asset": "BTC",
  "to_asset": "ETH",
  "from_amount": 1.234,
  "to_amount": 0.567,
  "affiliate_address": "ss",
  "captured_at": "2025-07-09T10:30:45.123Z",
  "raw_row_text": "original row text"
}
```

## Troubleshooting

### Extension Not Working

1. **Check Permissions**: Ensure the extension has permission to access ViewBlock
2. **Refresh Page**: Reload the ViewBlock page after installing the extension
3. **Check Console**: Open Chrome DevTools (F12) and check for errors in the Console tab

### No Data Captured

1. **Verify Page**: Make sure you're on the correct ViewBlock THORChain page
2. **Wait for Load**: Ensure the page has fully loaded before capturing
3. **Check Table**: Verify that the transaction table is visible on the page

### Tooltips Not Captured

1. **Hover Manually**: Try hovering over abbreviated text to see if tooltips appear
2. **Check Network**: Ensure the page has loaded completely
3. **Try Different Elements**: Some tooltips may be implemented differently

## Development

### Adding New Features

1. **Modify Content Script**: Edit `content.js` to change data extraction logic
2. **Update Popup**: Modify `popup.html` and `popup.js` for UI changes
3. **Test Changes**: Reload the extension in Chrome after making changes

### Debugging

1. **Console Logs**: Check the browser console for debug information
2. **Storage Inspection**: Use Chrome DevTools > Application > Storage to inspect captured data
3. **Network Tab**: Monitor network requests to understand page loading

## Limitations

- **Anti-bot Protection**: ViewBlock may implement anti-bot measures that could affect the extension
- **Page Structure Changes**: If ViewBlock changes their HTML structure, the extension may need updates
- **Rate Limiting**: Capturing many pages quickly may trigger rate limiting

## License

This extension is part of the ShapeShift affiliate tracker project and follows the same licensing terms. 