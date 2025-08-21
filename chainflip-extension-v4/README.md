# Chainflip Test Extension v4

A Chrome extension designed for **testing, page generation, and download capabilities** with a focus on comprehensive testing environments.

## 🎯 **What v4 Does**

### **🧪 Test Page Generation**
- **Create custom test pages** with comprehensive testing suites
- **Built-in test frameworks** for browser capabilities, performance, and UI
- **Automated test execution** with real-time results
- **Customizable test content** for specific testing needs

### **📥 Download Capabilities**
- **Download test pages** as HTML files
- **Batch download** all test pages at once
- **Download history tracking** with timestamps
- **Multiple export formats** (HTML, JSON)

### **🔧 Testing Features**
- **Browser capability testing** (User Agent, Platform, Features)
- **Performance metrics** (Load times, Memory usage, Network)
- **Storage testing** (LocalStorage, SessionStorage, IndexedDB)
- **UI interaction testing** (Events, DOM manipulation, CSS)

## 📁 File Structure

```
chainflip-extension-v4/
├── manifest.json          # Extension manifest (Manifest V3)
├── content.js            # Content script with test page generation
├── background.js         # Service worker with download management
├── popup.html           # Popup interface for test management
├── popup.js             # Popup functionality and UI logic
├── README.md            # This documentation
└── install.sh           # Installation helper script
```

## 🚀 **Quick Start**

### **Installation**
1. **Open Chrome** → `chrome://extensions/`
2. **Enable Developer mode** (toggle in top right)
3. **Click "Load unpacked"** → select `chainflip-extension-v4` folder
4. **Pin the extension** to your toolbar

### **First Test**
1. **Click extension icon** → opens popup
2. **Click "Create Test Page"** → generates comprehensive test page
3. **Click "Download Test Page"** → saves as HTML file
4. **Navigate to test page** → run automated tests

## 🎮 **Core Features**

### **1. Test Page Creation**
```javascript
// Create a test page with custom content
await chrome.runtime.sendMessage({
    action: 'create_test_page',
    title: 'My Custom Test',
    content: '<html>...</html>',
    metadata: { source: 'custom' }
});
```

### **2. Test Page Download**
```javascript
// Download a specific test page
await chrome.runtime.sendMessage({
    action: 'download_test_page',
    testPageId: 'test_1234567890_abc123'
});
```

### **3. Test History Management**
```javascript
// Get all test pages
const response = await chrome.runtime.sendMessage({
    action: 'get_test_history'
});
```

### **4. Data Management**
```javascript
// Clear all test data
await chrome.runtime.sendMessage({
    action: 'clear_test_data'
});
```

## 🧪 **Test Page Types**

### **Default Test Page**
- **Browser capabilities** testing
- **Performance metrics** collection
- **Basic functionality** verification
- **Auto-run** tests on page load

### **Custom Test Page**
- **User-defined content** and tests
- **Specific testing scenarios**
- **Custom metadata** and tracking
- **Flexible test frameworks**

### **Comprehensive Test Suite**
- **4 main test categories**:
  - 🔍 Browser Capabilities
  - 📊 Performance Metrics
  - 🌐 Network & Storage
  - 🎨 UI & Interaction

## 📊 **Test Results**

### **Browser Capabilities**
- User Agent information
- Platform details
- Cookie and online status
- Hardware specifications
- Touch and memory support

### **Performance Metrics**
- Page load times
- DOM content loading
- Memory usage statistics
- Navigation timing data

### **Storage Testing**
- LocalStorage functionality
- SessionStorage support
- IndexedDB availability
- Fetch API compatibility

### **UI Testing**
- Click event handling
- DOM manipulation
- CSS property support
- Element creation/removal

## 🔧 **API Reference**

### **Content Script API**
```javascript
// Access the extension instance
window.chainflipTestExtensionV4

// Run test page
chainflipTestExtensionV4.runTestPage()

// Download test page
chainflipTestExtensionV4.downloadTestPage()

// Generate test data
chainflipTestExtensionV4.generateTestData()
```

### **Background Script API**
```javascript
// Create test page
chrome.runtime.sendMessage({
    action: 'create_test_page',
    title: 'Test Title',
    content: 'HTML Content',
    metadata: {}
});

// Download test page
chrome.runtime.sendMessage({
    action: 'download_test_page',
    testPageId: 'test_id'
});

// Get test history
chrome.runtime.sendMessage({
    action: 'get_test_history'
});
```

## 📈 **Usage Examples**

### **Example 1: Create and Test**
```javascript
// 1. Create a test page
const response = await chrome.runtime.sendMessage({
    action: 'create_test_page',
    title: 'API Testing Page',
    content: '<html><body><h1>API Test</h1></body></html>'
});

// 2. Open the test page
if (response.success) {
    await chrome.runtime.sendMessage({
        action: 'open_test_page'
    });
}
```

### **Example 2: Batch Download**
```javascript
// Download all test pages
const history = await chrome.runtime.sendMessage({
    action: 'get_test_history'
});

for (const page of history.history) {
    await chrome.runtime.sendMessage({
        action: 'download_test_page',
        testPageId: page.id
    });
}
```

### **Example 3: Custom Test Content**
```javascript
const customTestContent = `
<!DOCTYPE html>
<html>
<head>
    <title>Custom Test</title>
</head>
<body>
    <h1>Custom Test Page</h1>
    <script>
        // Your custom tests here
        console.log('Custom test running...');
    </script>
</body>
</html>
`;

await chrome.runtime.sendMessage({
    action: 'create_test_page',
    title: 'Custom Test',
    content: customTestContent
});
```

## 🎨 **UI Components**

### **Popup Interface**
- **Statistics dashboard** showing test pages and downloads
- **Action buttons** for creating, opening, and downloading
- **Test history** with recent activity
- **Real-time updates** every 5 seconds

### **Content Script Overlay**
- **Floating test panel** on web pages
- **Quick access** to test functions
- **Status indicators** for test operations
- **Notification system** for user feedback

### **Test Page Interface**
- **Modern design** with gradient backgrounds
- **Interactive test buttons** for each category
- **Real-time results** display
- **Responsive layout** for various screen sizes

## ⚙️ **Configuration**

### **Settings**
```javascript
{
    auto_test: true,              // Auto-run tests on page load
    download_notifications: true,  // Show download notifications
    test_data_retention: 7,       // Days to keep test data
    max_test_pages: 10            // Maximum test pages to store
}
```

### **Permissions**
- `activeTab` - Access to current tab
- `storage` - Store test data and settings
- `scripting` - Inject content scripts
- `tabs` - Manage browser tabs
- `downloads` - Download test pages
- `webRequest` - Monitor network requests

## 🔍 **Debugging**

### **Console Access**
```javascript
// In browser console
window.chainflipTestExtensionV4.showDebugInfo();

// In popup console
window.testExtensionPopupV4.showDebugInfo();
```

### **Test Mode**
- **Verbose logging** for all operations
- **Error tracking** with detailed messages
- **Performance monitoring** for operations
- **State inspection** for debugging

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Test Page Not Creating**
- Check extension permissions
- Verify background script is running
- Check console for error messages

#### **Download Fails**
- Verify download folder permissions
- Check if file already exists
- Ensure sufficient disk space

#### **Tests Not Running**
- Check if content script is injected
- Verify page URL matches permissions
- Check console for JavaScript errors

### **Debug Steps**
1. **Check extension status** in `chrome://extensions/`
2. **Review console logs** for error messages
3. **Verify permissions** are granted
4. **Test on different pages** to isolate issues

## 📚 **Advanced Usage**

### **Custom Test Frameworks**
```javascript
// Create a custom test framework
class CustomTestFramework {
    constructor() {
        this.tests = [];
        this.results = [];
    }
    
    addTest(name, testFunction) {
        this.tests.push({ name, test: testFunction });
    }
    
    async runTests() {
        for (const test of this.tests) {
            try {
                const result = await test.test();
                this.results.push({ name: test.name, passed: result, timestamp: Date.now() });
            } catch (error) {
                this.results.push({ name: test.name, passed: false, error: error.message });
            }
        }
        return this.results;
    }
}
```

### **Integration with External Tools**
```javascript
// Export test results to external systems
async function exportToExternalSystem(testResults) {
    const response = await fetch('https://api.example.com/tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testResults)
    });
    return response.json();
}
```

## 🔄 **Version History**

### **v4.0.0 (Current)**
- **Test page generation** with comprehensive testing suites
- **Download management** for all test pages
- **Custom test content** support
- **Advanced UI** with real-time updates
- **Performance monitoring** and metrics collection

### **Future Versions**
- **Test result analytics** and reporting
- **Integration with CI/CD** systems
- **Advanced test frameworks** (Jest, Mocha, etc.)
- **Cloud storage** for test pages and results

## 📞 **Support & Development**

### **Getting Help**
1. **Check this README** for common solutions
2. **Review console logs** for error details
3. **Test on different pages** to isolate issues
4. **Verify extension permissions** and settings

### **Contributing**
- **Report bugs** with detailed error messages
- **Suggest features** for future versions
- **Submit pull requests** for improvements
- **Test on various browsers** and platforms

---

**Note**: v4 is designed as a comprehensive testing and page generation tool. It's perfect for developers who need to quickly create test environments, validate browser capabilities, and download test pages for offline use or sharing.

