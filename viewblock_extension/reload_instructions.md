# ViewBlock THORChain Extension - Reload Instructions

## Recent Updates (Latest Version)

### ✅ Major UI and Functionality Fixes
- **Fixed white font issue** - All text now has proper contrast with dark text on light background
- **Fixed button functionality** - All buttons now work correctly with proper event handlers
- **Improved auto-paging timing** - Waits longer (5+ seconds) before switching pages to ensure data capture
- **Enhanced floating UI** - Better styling, persistent across page navigation, draggable interface
- **Better data management** - Improved download functionality and data persistence

### ✅ Enhanced User Experience
- **Persistent floating UI** - Interface stays visible and functional across page navigation
- **Real-time progress tracking** - Shows current page and total captured transactions
- **Better error handling** - Clear messages when on wrong page or encountering errors
- **Improved popup** - Clean interface with better navigation and feedback

### ✅ Technical Improvements
- **Chrome storage integration** - State persists across page reloads and navigation
- **Better page detection** - Only activates on correct ViewBlock THORChain pages
- **Enhanced navigation** - Both button clicking and URL manipulation for pagination
- **Improved data capture** - More robust table parsing and transaction extraction

## How to Reload the Extension

### Step 1: Open Chrome Extensions
1. Go to `chrome://extensions/`
2. Make sure "Developer mode" is enabled (toggle in top right)

### Step 2: Reload the Extension
1. Find "ViewBlock THORChain Scraper" in the list
2. Click the **🔄 Reload** button
3. You should see "Reloaded" confirmation

### Step 3: Navigate to ViewBlock
1. Go to: `https://viewblock.io/thorchain/txs?affiliate=ss`
2. Wait for the page to fully load

### Step 4: Open Extension
1. Click the extension icon in Chrome toolbar
2. Click "Open Floating Interface"
3. The floating UI should appear on the page

## How to Use the Extension

### Basic Usage
1. **Capture Current Page**: Click to capture transactions from the current page only
2. **Start Auto-Capture**: Automatically navigate through multiple pages and capture data
3. **Download Data**: Save all captured transactions as JSON file
4. **Debug Info**: View technical information about the current page

### Settings
- **Max Pages**: Set how many pages to capture (1-50)
- **Delay**: Time to wait between pages (500-10000ms, minimum 3000ms enforced)

### Auto-Capture Process
1. Set your desired max pages and delay
2. Click "Start Auto-Capture"
3. Extension will:
   - Capture current page data
   - Wait for specified delay (minimum 3 seconds)
   - Navigate to next page
   - Repeat until max pages reached
4. Click "Download Data" when complete

## Troubleshooting

### If the extension doesn't work:
1. **Check the page**: Make sure you're on `viewblock.io/thorchain/txs?affiliate=ss`
2. **Reload extension**: Follow reload steps above
3. **Refresh page**: Reload the ViewBlock page
4. **Check console**: Press F12 and look for errors in Console tab

### If auto-capture stops prematurely:
1. **Increase delay**: Try 5000-8000ms for slower connections
2. **Check progress**: Data is saved after each page
3. **Resume manually**: Click "Start Auto-Capture" again to continue

### If floating UI disappears:
1. **Click extension icon**: Reopen from popup
2. **Check page**: UI only appears on correct pages
3. **Reload extension**: If UI becomes unresponsive

## Data Format

The extension captures:
- Transaction hash (truncated)
- Block height
- Transaction type (Swap, Add, etc.)
- Action details (amounts and assets)
- Timestamp
- Status
- Affiliate address (ss)

Data is saved as JSON format compatible with your existing analysis tools.

## What's Fixed

1. ✅ **White font visibility** - All text now visible with proper contrast
2. ✅ **Button functionality** - All buttons work with proper event handlers
3. ✅ **Auto-paging timing** - Waits longer to ensure complete data capture
4. ✅ **Floating UI persistence** - Interface stays visible across page changes
5. ✅ **Data download** - Improved download functionality with proper file naming
6. ✅ **Settings persistence** - Max pages and delay settings are saved
7. ✅ **Progress tracking** - Real-time updates of capture progress
8. ✅ **Error handling** - Better messages and recovery options 