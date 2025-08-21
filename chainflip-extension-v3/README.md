# Chainflip Affiliate Tracker v3

A Chrome extension to track ShapeShift affiliate transactions on the Chainflip protocol with **improved connection handling and error recovery**.

## 🚀 **What's New in v3**

### **🔧 Connection Issues Fixed**
- **"Receiving end does not exist" error resolved**
- **Automatic connection recovery** with retry mechanism
- **Fallback to local mode** when background script unavailable
- **Persistent connection monitoring** with periodic health checks

### **🛡️ Enhanced Error Handling**
- **Graceful degradation** when background script fails
- **Local storage fallback** for data persistence
- **Automatic retry logic** for failed connections
- **User-friendly error messages** and status indicators

### **📱 Improved UI/UX**
- **Real-time connection status** display
- **Better transaction detection** with enhanced selectors
- **Responsive design** for various screen sizes
- **Smooth animations** and visual feedback

## 📁 File Structure

```
chainflip-extension-v3/
├── manifest.json          # Extension manifest (Manifest V3)
├── content.js            # Enhanced content script with connection handling
├── background.js         # Improved service worker with error recovery
├── popup.html           # Modern popup interface
├── popup.js             # Enhanced popup functionality
├── icons/               # Extension icons
├── README.md            # This documentation
└── install.sh           # Installation helper script
```

## 🔧 Installation

### **Quick Install**
```bash
cd chainflip-extension-v3
chmod +x install.sh
./install.sh
```

### **Manual Installation**
1. **Open Chrome** → `chrome://extensions/`
2. **Enable Developer mode** (toggle in top right)
3. **Click "Load unpacked"** → select `chainflip-extension-v3` folder
4. **Pin the extension** to your toolbar

## 🎯 **Key Features**

### **🔌 Smart Connection Management**
- **Automatic connection establishment** to background script
- **Connection health monitoring** every 30 seconds
- **Automatic reconnection** with exponential backoff
- **Local mode fallback** when background unavailable

### **📊 Enhanced Transaction Tracking**
- **Multiple detection methods** for transaction data
- **Improved selectors** for various page structures
- **Real-time DOM monitoring** with MutationObserver
- **Enhanced data extraction** from transaction elements

### **💾 Robust Data Storage**
- **Dual storage strategy** (background + local)
- **Automatic data synchronization** when connection restored
- **Data export** in JSON/CSV formats
- **Automatic cleanup** of old transactions

## 🚨 **Troubleshooting v3**

### **Connection Issues**

#### **"Receiving end does not exist" Error**
**Problem**: Content script can't communicate with background script

**Solutions**:
1. **Reload the extension** in `chrome://extensions/`
2. **Check console** for connection status
3. **Verify background script** is running
4. **Clear browser cache** and restart Chrome

#### **Background Script Not Responding**
**Problem**: Background service worker is inactive

**Solutions**:
1. **Check extension permissions** in `chrome://extensions/`
2. **Verify manifest.json** syntax
3. **Reload the extension**
4. **Check for JavaScript errors** in background console

### **Transaction Detection Issues**

#### **No Transactions Found**
**Problem**: Extension not detecting transactions on Chainflip pages

**Solutions**:
1. **Verify page URL** includes `app.chainflip.io`
2. **Check content script** injection in console
3. **Refresh the page** after extension installation
4. **Verify page structure** matches expected selectors

#### **Missing Transaction Data**
**Problem**: Transactions detected but missing details

**Solutions**:
1. **Check page structure** for transaction elements
2. **Verify data attributes** on transaction elements
3. **Check console** for parsing errors
4. **Update selectors** if page structure changed

### **Data Export Issues**

#### **Export Fails**
**Problem**: Can't export transaction data

**Solutions**:
1. **Check storage permissions** are granted
2. **Verify transactions exist** before exporting
3. **Check download folder** permissions
4. **Try different export formats** (JSON vs CSV)

## 🔍 **Debug Mode**

### **Enable Debug Logging**
```javascript
// In browser console on Chainflip page
window.chainflipAffiliateTrackerV3.showDebugInfo();

// In popup console
window.popupManagerV3.showDebugInfo();
```

### **Check Connection Status**
```javascript
// Check if background script is responding
chrome.runtime.sendMessage({action: 'connection_test'})
  .then(response => console.log('Connected:', response))
  .catch(error => console.log('Disconnected:', error));
```

### **Monitor Content Script**
```javascript
// Check if content script is active
console.log('Tracker active:', window.chainflipAffiliateTrackerV3 !== undefined);
```

## ⚙️ **Configuration**

### **Affiliate Address**
Update the affiliate address in `content.js`:
```javascript
this.affiliateAddress = '0x0000000000000000000000000000000000000000'; // Replace with actual ShapeShift address
```

### **Connection Settings**
Modify connection behavior in `background.js`:
```javascript
this.settings = {
    auto_track: true,
    notifications: true,
    export_format: 'json',
    connection_timeout: 5000,    // 5 seconds
    max_retries: 5               // Max reconnection attempts
};
```

### **Scanning Frequency**
Adjust transaction scanning in `content.js`:
```javascript
// Check every 3 seconds (default)
setInterval(() => {
    this.scanForTransactions();
}, 3000);
```

## 📊 **Data Structure**

Each tracked transaction includes:
```javascript
{
    hash: "0x...",              // Transaction hash
    timestamp: 1234567890,      // Unix timestamp
    url: "https://...",         // Page URL when detected
    protocol: "Chainflip",      // Protocol identifier
    pageTitle: "Page Title",    // Page title
    amount: "100.50",           // Transaction amount
    token: "USDC",              // Token symbol
    from: "0x...",              // Sender address
    to: "0x...",                // Recipient address
    status: "Confirmed",        // Transaction status
    blockNumber: "12345",       // Block number (if available)
    isAffiliate: false,         // Affiliate flag
    // ... additional extracted data
}
```

## 🔄 **Version History**

### **v3.0.0 (Current)**
- **Connection error handling** completely rewritten
- **Automatic retry mechanism** with exponential backoff
- **Local storage fallback** when background unavailable
- **Enhanced transaction detection** with improved selectors
- **Real-time connection status** display
- **Better error messages** and user feedback
- **Improved UI/UX** with modern design

### **v2.0.0**
- Basic transaction tracking
- Simple popup interface
- Limited error handling

### **v1.x**
- Basic functionality
- No error recovery

## 🛠️ **Development**

### **Testing Connection Issues**
1. **Simulate background failure**: Disable extension in `chrome://extensions/`
2. **Test reconnection**: Re-enable extension
3. **Verify fallback**: Check local storage functionality
4. **Monitor console**: Watch for connection messages

### **Adding New Transaction Sources**
1. **Update selectors** in `scanForTransactions()`
2. **Add parsing logic** in extraction methods
3. **Test on target pages** with various structures
4. **Update documentation** with new capabilities

## 📞 **Support & Issues**

### **Common Issues**
- **Extension not loading**: Check manifest.json syntax
- **No transactions**: Verify page structure and selectors
- **Export fails**: Check permissions and storage
- **Connection errors**: Reload extension and check console

### **Getting Help**
1. **Check console logs** for error messages
2. **Review this README** for troubleshooting steps
3. **Test on different pages** to isolate issues
4. **Check extension permissions** and settings

## 🎉 **Success Indicators**

### **Working Correctly**
- ✅ Console shows "Chainflip Affiliate Tracker v3 loaded"
- ✅ Connection status shows "Connected"
- ✅ Transactions are detected and stored
- ✅ Data exports successfully
- ✅ UI updates in real-time

### **Needs Attention**
- ⚠️ Connection status shows "Disconnected"
- ⚠️ Console shows connection errors
- ⚠️ No transactions detected
- ⚠️ Export operations fail

---

**Note**: v3 specifically addresses the "Receiving end does not exist" error by implementing robust connection handling, automatic retry logic, and local storage fallbacks. If you continue to experience issues, the extension will automatically fall back to local mode to ensure data persistence.


