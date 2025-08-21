# 📝 **DeFi Data Snatcher v15 - Simple Text Export Version**

## 🎯 **Purpose**
Chrome extension for Butterswap tables that **bypasses complex CSV processing entirely** to avoid null reference errors. Uses simple text and JSON export instead.

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

### **📝 Simple Text Export**
- **No CSV processing**: Completely bypasses CSV generation
- **Simple text format**: Human-readable text output
- **JSON export**: Raw data export in JSON format
- **Error-free**: No complex string operations that can fail

## 🚀 **Installation**

### **1. Download Extension**
```bash
# Clone or download the v15 folder
cd defi-data-snatcher-v15
```

### **2. Load in Chrome**
1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `defi-data-snatcher-v15` folder
5. Extension should appear as **DeFi Data Snatcher v15**

### **3. Verify Installation**
- Extension icon should appear in Chrome toolbar
- Hover should show "DeFi Data Snatcher v15"

## 🧪 **Testing**

### **1. Test on Butterswap Explorer**
1. Go to [Butterswap Explorer](https://butterswap.com) or similar
2. Navigate to a page with transaction tables
3. Click the extension icon
4. Should show "Simple Text Export v15" UI

### **2. Test Table Scanning**
1. Click **"🔍 Scan Table & Extract Links"**
2. Extension should detect transaction table
3. Should show results with row count and link count

### **3. Test Simple Text Export**
1. Click **"📝 Export Simple Text"**
2. Should download a .txt file with readable data
3. **No CSV errors** - simple text format

### **4. Test Raw Data Export**
1. Click **"📄 Export Raw Data"**
2. Should download a .json file with raw data
3. **No CSV processing** - direct JSON export

## 📁 **File Structure**

```
defi-data-snatcher-v15/
├── manifest.json          # Extension configuration (v15)
├── background.js          # Service worker with simple text export
├── icons/                 # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
├── README_v15.md          # This documentation
└── install_v15.sh         # Installation script
```

## 🔧 **Technical Details**

### **Hyperlink Generation Logic**
- **Hash extraction**: Finds 0x... patterns in hash column
- **URL construction**: Builds links using detected domain
- **Multiple endpoints**: Tries /tx/, /transaction/, /hash/ patterns
- **Domain detection**: Automatically detects current site domain
- **Fallback URLs**: Multiple variations for reliability

### **Simple Text Export Logic**
- **No CSV processing**: Completely bypasses CSV generation
- **Simple concatenation**: Only basic string operations
- **Text formatting**: Human-readable text output
- **JSON export**: Raw data export without processing

## 📊 **Export Formats**

### **Simple Text Export (.txt)**
```
DeFi Data Snatcher v15 - Simple Text Export
=============================================

Scan Time: Aug 18, 2025, 12:00:00 PM
Timestamp: 2025-08-18T17:00:00.000Z

TABLE DATA:
===========

Row 1:
  Hash: 0xd12...55403
  From: 11USDC 0x32d...96cb6
  To: 10.51051USDC 0xFF0...900a5
  Fee: 0.00
  Status: ✅ Success
  Time: 2025-07-28 08:26:59(UTC)
  Link: https://butterswap.com/tx/0xd12...55403

TRANSACTION LINKS:
==================

Link 1:
  ID: 1
  Hash: 0xd12...55403
  Row: 1
  URL: https://butterswap.com/tx/0xd12...55403
```

### **Raw Data Export (.json)**
```json
{
  "version": "v15",
  "scanTime": {
    "human": "Aug 18, 2025, 12:00:00 PM",
    "timestamp": "2025-08-18T17:00:00.000Z"
  },
  "tableData": [
    {
      "rowIndex": 1,
      "isHeader": false,
      "hash": "0xd12...55403",
      "from": "11USDC 0x32d...96cb6",
      "to": "10.51051USDC 0xFF0...900a5",
      "fee": "0.00",
      "status": "✅ Success",
      "time": "2025-07-28 08:26:59(UTC)",
      "fullLink": "https://butterswap.com/tx/0xd12...55403"
    }
  ],
  "transactionLinks": [
    {
      "id": 1,
      "hash": "0xd12...55403",
      "fullLink": "https://butterswap.com/tx/0xd12...55403",
      "rowIndex": 1
    }
  ],
  "exportTime": "2025-08-18T17:00:00.000Z"
}
```

## 🎯 **Use Cases**

### **Primary Use Case**
- **Butterswap transaction tables** with abbreviated hashes
- **Automatic hyperlink generation** for full transaction details
- **Simple text export** without CSV processing errors
- **Raw data export** for data analysis

### **Secondary Use Cases**
- Other DeFi platforms with similar table structures
- Any transaction table with hash data
- Data analysis requiring full transaction links
- Avoiding CSV export errors

## 🚨 **Troubleshooting**

### **Extension Not Working**
1. Check Chrome console for errors
2. Verify extension is loaded in chrome://extensions/
3. Reload the extension if needed
4. Check if page has transaction tables

### **No Hyperlinks Generated**
1. Ensure table contains hash data (0x...)
2. Check if current domain is supported
3. Verify hash format in table

### **Export Issues**
1. Ensure table has been scanned first
2. Check browser download settings
3. Verify data is present in results section
4. **v15 advantage**: No CSV processing errors

## 🔄 **Version History**

### **v15 - Simple Text Export (Current)**
- ✅ **Guaranteed hyperlink generation**
- ✅ **Clean data processing**
- ✅ **Multiple URL patterns**
- ✅ **Domain detection**
- ✅ **Streamlined workflow**
- ✅ **Simple text export** (NEW!)
- ✅ **JSON raw data export** (NEW!)
- ✅ **No CSV processing errors** (NEW!)

### **Previous Versions**
- v14: Ultra-bulletproof but still had CSV issues
- v13: Hyperlink focused but export errors
- v12: Working but complex data format
- v11: Data separation improvements

## 📝 **Development Notes**

### **Architecture**
- **Service Worker**: background.js handles extension events
- **Content Script Injection**: UI and logic injected into page context
- **Global State**: window.defiDataV15 for data persistence
- **Simple Export**: Text and JSON export without CSV processing

### **Key Functions**
- `scanTableAndExtractLinks()`: Main scanning and link generation
- `generateTransactionLink()`: Creates full transaction URLs
- `exportSimpleText()`: **Simple text export** without CSV processing
- `exportRawData()`: **JSON export** of raw data

### **Export Strategy**
- **No CSV processing**: Completely bypasses CSV generation
- **Simple text**: Human-readable text output
- **JSON export**: Raw data export without processing
- **Error-free**: No complex string operations

## 🎉 **Success Criteria**

The extension is working correctly when:
1. **Table data is populated** with actual transaction information
2. **Full hyperlinks are generated** for every transaction hash
3. **Simple text export works** without any errors
4. **JSON export works** without any errors
5. **No CSV processing** - completely bypassed

## 🆕 **v15 New Features:**

### **Simple Text Export**
- **No CSV processing**: Completely bypasses CSV generation
- **Human-readable**: Simple text format for easy reading
- **Error-free**: No complex string operations that can fail
- **Reliable**: Always works regardless of data quality

### **JSON Raw Data Export**
- **Raw data**: Complete data structure without processing
- **No CSV**: Direct JSON export from data objects
- **Error-free**: No string processing or formatting
- **Data integrity**: Preserves all original data

---

**v15 is specifically designed to prioritize hyperlink generation while providing reliable export through simple text and JSON formats!**
