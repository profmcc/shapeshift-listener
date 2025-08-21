# 🔗 **DeFi Data Snatcher v13 - Hyperlink Focused Version**

## 🎯 **Purpose**
Specialized Chrome extension for Butterswap tables that **guarantees full transaction hyperlink generation** while maintaining clean, readable data format.

## ✨ **Key Features**

### **🔍 Smart Table Detection**
- **Flexible scanning**: Finds any table with transaction-like data
- **Fallback detection**: Uses first table if specific one not found
- **Better parsing**: Handles various table structures

### **🔗 Guaranteed Hyperlink Generation**
- **Multiple URL patterns**: `/tx/`, `/transaction/`, `/hash/` endpoints
- **Domain detection**: Automatically detects butterswap.com, butter.network, etc.
- **Fallback URLs**: Multiple endpoint variations for reliability
- **Hash cleaning**: Extracts clean hashes from mixed text

### **📊 Clean Data Processing**
- **Normalized text**: Removes extra whitespace and newlines
- **Simple structure**: Focuses on essential transaction data
- **Clean columns**: Hash, From, To, Fee, Status, Time, Full Link

## 🚀 **Installation**

### **1. Download Extension**
```bash
# Clone or download the v13 folder
cd defi-data-snatcher-v13
```

### **2. Load in Chrome**
1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `defi-data-snatcher-v13` folder
5. Extension should appear with **DeFi Data Snatcher v13**

### **3. Verify Installation**
- Extension icon should appear in Chrome toolbar
- Hover should show "DeFi Data Snatcher v13"

## 🧪 **Testing**

### **1. Test on Butterswap Explorer**
1. Go to [Butterswap Explorer](https://butterswap.com) or similar
2. Navigate to a page with transaction tables
3. Click the extension icon
4. Should show "Hyperlink Focused v13" UI

### **2. Test Table Scanning**
1. Click **"🔍 Scan Table & Extract Links"**
2. Extension should detect transaction table
3. Should show results with row count and link count

### **3. Test Link Extraction**
1. Click **"🔗 Extract All Transaction Links"**
2. Should generate full transaction hyperlinks
3. Check results section for sample links

### **4. Test CSV Export**
1. Click **"📊 Export Clean CSV with Links"**
2. Should download CSV with transaction data and links
3. Verify links are clickable and functional

## 📁 **File Structure**

```
defi-data-snatcher-v13/
├── manifest.json          # Extension configuration (v13)
├── background.js          # Service worker with hyperlink logic
├── icons/                 # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
├── README_v13.md          # This documentation
└── install_v13.sh         # Installation script
```

## 🔧 **Technical Details**

### **Hyperlink Generation Logic**
- **Hash extraction**: Finds 0x... patterns in hash column
- **URL construction**: Builds links using detected domain
- **Multiple endpoints**: Tries /tx/, /transaction/, /hash/ patterns
- **Domain detection**: Automatically detects current site domain
- **Fallback URLs**: Multiple variations for reliability

### **Data Processing**
- **Clean text**: Removes whitespace and normalizes
- **Structured output**: Organized columns with clear data
- **Link integration**: Full hyperlinks in separate column

## 📊 **CSV Output Format**

```csv
Row Index,Hash,From,To,Fee($),Status,Time,Full Transaction Link
1,"0xd12...55403","11USDC 0x32d...96cb6","10.51051USDC 0xFF0...900a5","0.00","✅ Success","2025-07-28 08:26:59(UTC)","https://butterswap.com/tx/0xd12...55403"
2,"0x348...29efa","0.0034ETH 0x32d...96cb6","53.51709POL 0xFF0...900a5","0.00","✅ Success","2025-07-28 07:53:02(UTC)","https://butterswap.com/tx/0x348...29efa"

Transaction Links Section
Link ID,Hash,Row Index,Full Transaction Link
1,"0xd12...55403",1,"https://butterswap.com/tx/0xd12...55403"
2,"0x348...29efa",2,"https://butterswap.com/tx/0x348...29efa"
```

## 🎯 **Use Cases**

### **Primary Use Case**
- **Butterswap transaction tables** with abbreviated hashes
- **Automatic hyperlink generation** for full transaction details
- **Clean CSV export** with working transaction links

### **Secondary Use Cases**
- Other DeFi platforms with similar table structures
- Any transaction table with hash data
- Data analysis requiring full transaction links

## 🚨 **Troubleshooting**

### **Extension Not Working**
1. Check Chrome console for errors
2. Verify extension is loaded in chrome://extensions/
3. Reload the extension if needed
4. Check if page has transaction tables

### **No Hyperlinks Generated**
1. Ensure table contains hash data (0x...)
2. Try "Extract All Transaction Links" button
3. Check if current domain is supported
4. Verify hash format in table

### **CSV Export Issues**
1. Ensure table has been scanned first
2. Check browser download settings
3. Verify data is present in results section

## 🔄 **Version History**

### **v13 - Hyperlink Focused (Current)**
- ✅ **Guaranteed hyperlink generation**
- ✅ **Clean data processing**
- ✅ **Multiple URL patterns**
- ✅ **Domain detection**
- ✅ **Streamlined workflow**

### **Previous Versions**
- v12: Working but complex data format
- v11: Data separation improvements
- v10: Working MVP with basic functionality
- v9: Fixed UI persistence issues

## 📝 **Development Notes**

### **Architecture**
- **Service Worker**: background.js handles extension events
- **Content Script Injection**: UI and logic injected into page context
- **Global State**: window.defiDataV13 for data persistence

### **Key Functions**
- `scanTableAndExtractLinks()`: Main scanning and link generation
- `generateTransactionLink()`: Creates full transaction URLs
- `exportCleanCSVWithLinks()`: Exports data with working links

## 🎉 **Success Criteria**

The extension is working correctly when:
1. **Table data is populated** with actual transaction information
2. **Full hyperlinks are generated** for every transaction hash
3. **CSV export contains** clean data and working links
4. **No weird formatting** - just clean, usable data

---

**v13 is specifically designed to prioritize hyperlink generation while maintaining clean, readable data format!**
