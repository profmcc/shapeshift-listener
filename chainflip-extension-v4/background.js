// Chainflip Test Extension v4 - Background Service Worker
// Handles test page management, downloads, and background tasks

console.log('Chainflip Test Extension v4 Background Service Worker loaded');

class TestExtensionBackgroundV4 {
    constructor() {
        this.version = '4.0.0';
        this.testPages = new Map();
        this.downloadHistory = [];
        this.settings = {
            auto_test: true,
            download_notifications: true,
            test_data_retention: 7, // days
            max_test_pages: 10
        };
        this.init();
    }

    init() {
        console.log(`Initializing Test Extension Background v${this.version}`);
        
        // Load existing data
        this.loadData();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up periodic cleanup
        this.setupPeriodicCleanup();
        
        console.log('Test Extension Background initialized successfully');
    }

    setupEventListeners() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            console.log('Test Extension installed:', details.reason);
            
            if (details.reason === 'install') {
                this.initializeStorage();
            } else if (details.reason === 'update') {
                this.handleUpdate();
            }
        });

        // Handle messages from content scripts
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            console.log('Background received message:', request);
            this.handleMessage(request, sender, sendResponse);
            return true; // Keep message channel open for async response
        });

        // Handle tab updates
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && tab.url) {
                this.handleTabUpdate(tabId, tab);
            }
        });

        // Handle extension icon click
        chrome.action.onClicked.addListener((tab) => {
            console.log('Test Extension icon clicked');
            this.openTestPage(tab);
        });

        // Handle downloads
        chrome.downloads.onChanged.addListener((downloadDelta) => {
            this.handleDownloadChange(downloadDelta);
        });
    }

    handleMessage(request, sender, sendResponse) {
        switch (request.action) {
            case 'test':
                this.handleTestMessage(request, sendResponse);
                break;
            case 'create_test_page':
                this.handleCreateTestPage(request, sendResponse);
                break;
            case 'download_test_page':
                this.handleDownloadTestPage(request, sendResponse);
                break;
            case 'get_test_history':
                this.handleGetTestHistory(sendResponse);
                break;
            case 'clear_test_data':
                this.handleClearTestData(sendResponse);
                break;
            case 'get_settings':
                this.handleGetSettings(sendResponse);
                break;
            case 'update_settings':
                this.handleUpdateSettings(request.settings, sendResponse);
                break;
            default:
                sendResponse({ error: 'Unknown action' });
        }
    }

    handleTestMessage(request, sendResponse) {
        console.log('Test message received:', request);
        sendResponse({ 
            success: true, 
            message: 'Test message received successfully',
            timestamp: Date.now(),
            version: this.version
        });
    }

    async handleCreateTestPage(request, sendResponse) {
        try {
            const testPageId = this.generateTestPageId();
            const testPage = {
                id: testPageId,
                url: request.url || 'https://example.com',
                title: request.title || 'Test Page',
                created: Date.now(),
                content: request.content || this.generateDefaultTestContent(),
                metadata: request.metadata || {}
            };

            this.testPages.set(testPageId, testPage);
            await this.saveData();

            sendResponse({ 
                success: true, 
                testPageId: testPageId,
                message: 'Test page created successfully'
            });
        } catch (error) {
            console.error('Error creating test page:', error);
            sendResponse({ error: 'Failed to create test page' });
        }
    }

    async handleDownloadTestPage(request, sendResponse) {
        try {
            const testPageId = request.testPageId;
            const testPage = this.testPages.get(testPageId);
            
            if (!testPage) {
                sendResponse({ error: 'Test page not found' });
                return;
            }

            // Download the test page
            const filename = `test-page-${testPageId}.html`;
            const content = testPage.content;
            
            await this.downloadFile(filename, content, 'text/html');
            
            // Record download
            this.downloadHistory.push({
                testPageId: testPageId,
                filename: filename,
                timestamp: Date.now()
            });
            
            await this.saveData();
            
            sendResponse({ 
                success: true, 
                message: 'Test page downloaded successfully',
                filename: filename
            });
        } catch (error) {
            console.error('Error downloading test page:', error);
            sendResponse({ error: 'Failed to download test page' });
        }
    }

    async handleGetTestHistory(sendResponse) {
        try {
            const history = Array.from(this.testPages.values()).map(page => ({
                id: page.id,
                title: page.title,
                url: page.url,
                created: page.created,
                downloads: this.downloadHistory.filter(d => d.testPageId === page.id).length
            }));
            
            sendResponse({ 
                success: true, 
                history: history,
                totalPages: this.testPages.size,
                totalDownloads: this.downloadHistory.length
            });
        } catch (error) {
            console.error('Error getting test history:', error);
            sendResponse({ error: 'Failed to get test history' });
        }
    }

    async handleClearTestData(sendResponse) {
        try {
            this.testPages.clear();
            this.downloadHistory = [];
            await this.saveData();
            
            sendResponse({ 
                success: true, 
                message: 'All test data cleared successfully'
            });
        } catch (error) {
            console.error('Error clearing test data:', error);
            sendResponse({ error: 'Failed to clear test data' });
        }
    }

    async handleGetSettings(sendResponse) {
        try {
            sendResponse({ 
                success: true, 
                settings: this.settings
            });
        } catch (error) {
            console.error('Error getting settings:', error);
            sendResponse({ error: 'Failed to get settings' });
        }
    }

    async handleUpdateSettings(newSettings, sendResponse) {
        try {
            this.settings = { ...this.settings, ...newSettings };
            await this.saveData();
            
            sendResponse({ 
                success: true, 
                settings: this.settings,
                message: 'Settings updated successfully'
            });
        } catch (error) {
            console.error('Error updating settings:', error);
            sendResponse({ error: 'Failed to update settings' });
        }
    }

    handleTabUpdate(tabId, tab) {
        // Check if this is a test page
        if (tab.url && tab.url.includes('data:text/html')) {
            console.log('Test page tab updated:', tabId);
            this.recordTestPageVisit(tabId, tab);
        }
    }

    async openTestPage(tab) {
        try {
            // Create a default test page
            const testPageId = this.generateTestPageId();
            const testPage = {
                id: testPageId,
                url: 'https://example.com',
                title: 'Default Test Page',
                created: Date.now(),
                content: this.generateDefaultTestContent(),
                metadata: { source: 'icon_click' }
            };

            this.testPages.set(testPageId, testPage);
            await this.saveData();

            // Open the test page in a new tab
            const testPageUrl = 'data:text/html;charset=utf-8,' + encodeURIComponent(testPage.content);
            await chrome.tabs.create({ url: testPageUrl });

            console.log('Default test page opened');
        } catch (error) {
            console.error('Error opening test page:', error);
        }
    }

    generateDefaultTestContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Default Test Page v4</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .content {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 16px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .test-info {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 14px;
        }
        .button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Default Test Page v4</h1>
        <p>This is a default test page generated by the Chainflip Test Extension</p>
    </div>
    
    <div class="content">
        <h2>Test Information</h2>
        <div class="test-info">
            <strong>Extension Version:</strong> ${this.version}<br>
            <strong>Generated:</strong> ${new Date().toLocaleString()}<br>
            <strong>Page ID:</strong> ${this.generateTestPageId()}<br>
            <strong>User Agent:</strong> ${navigator.userAgent}
        </div>
        
        <h2>Quick Tests</h2>
        <button class="button" onclick="testBasicFunctionality()">Test Basic Functionality</button>
        <button class="button" onclick="testDOMAccess()">Test DOM Access</button>
        <button class="button" onclick="testJavaScript()">Test JavaScript</button>
        
        <div id="test-results" style="margin-top: 20px;"></div>
    </div>
    
    <script>
        function testBasicFunctionality() {
            const results = document.getElementById('test-results');
            const tests = [
                { name: 'Document Ready', result: !!document.body, expected: true },
                { name: 'Console Available', result: typeof console !== 'undefined', expected: true },
                { name: 'JSON Support', result: typeof JSON !== 'undefined', expected: true }
            ];
            
            const html = tests.map(test => 
                \`<div style="margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 8px; border-left: 4px solid \${test.result === test.expected ? '#4CAF50' : '#f44336'};">
                    <strong>\${test.name}:</strong> \${test.result ? '✅ PASS' : '❌ FAIL'}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }
        
        function testDOMAccess() {
            const results = document.getElementById('test-results');
            const elements = document.querySelectorAll('*');
            const elementCount = elements.length;
            
            results.innerHTML = \`<div style="margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 8px; border-left: 4px solid #2196F3;">
                <strong>DOM Access Test:</strong> ✅ PASS<br>
                <strong>Total Elements:</strong> \${elementCount}
            </div>\`;
        }
        
        function testJavaScript() {
            const results = document.getElementById('test-results');
            const tests = [
                { name: 'LocalStorage', result: typeof localStorage !== 'undefined', expected: true },
                { name: 'Fetch API', result: typeof fetch !== 'undefined', expected: true },
                { name: 'Performance API', result: typeof performance !== 'undefined', expected: true }
            ];
            
            const html = tests.map(test => 
                \`<div style="margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 8px; border-left: 4px solid \${test.result === test.expected ? '#4CAF50' : '#f44336'};">
                    <strong>\${test.name}:</strong> \${test.result ? '✅ PASS' : '❌ FAIL'}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }
        
        // Auto-run basic test on page load
        window.addEventListener('load', () => {
            setTimeout(testBasicFunctionality, 1000);
        });
    </script>
</body>
</html>`;
    }

    generateTestPageId() {
        return 'test_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    recordTestPageVisit(tabId, tab) {
        console.log('Test page visit recorded:', { tabId, url: tab.url });
        // Could store analytics here
    }

    async downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        try {
            await chrome.downloads.download({
                url: url,
                filename: filename,
                saveAs: true
            });
        } finally {
            URL.revokeObjectURL(url);
        }
    }

    handleDownloadChange(downloadDelta) {
        if (downloadDelta.state && downloadDelta.state.current === 'complete') {
            console.log('Download completed:', downloadDelta.id);
        }
    }

    async initializeStorage() {
        try {
            await chrome.storage.local.set({
                'test_extension_v4': {
                    version: this.version,
                    testPages: {},
                    downloadHistory: [],
                    settings: this.settings,
                    created: Date.now()
                }
            });
            console.log('Test extension storage initialized successfully');
        } catch (error) {
            console.error('Failed to initialize storage:', error);
        }
    }

    async loadData() {
        try {
            const result = await chrome.storage.local.get(['test_extension_v4']);
            const data = result.test_extension_v4 || {};
            
            if (data.testPages) {
                this.testPages = new Map(Object.entries(data.testPages));
            }
            
            this.downloadHistory = data.downloadHistory || [];
            this.settings = { ...this.settings, ...data.settings };
            
            console.log(`Loaded ${this.testPages.size} test pages and ${this.downloadHistory.length} downloads`);
        } catch (error) {
            console.error('Failed to load data:', error);
        }
    }

    async saveData() {
        try {
            const testPagesObj = Object.fromEntries(this.testPages);
            await chrome.storage.local.set({
                'test_extension_v4': {
                    version: this.version,
                    testPages: testPagesObj,
                    downloadHistory: this.downloadHistory,
                    settings: this.settings,
                    lastUpdated: Date.now()
                }
            });
        } catch (error) {
            console.error('Failed to save data:', error);
        }
    }

    handleUpdate() {
        console.log('Test extension updated, checking for data migration...');
        // Handle any necessary data migrations here
    }

    setupPeriodicCleanup() {
        // Clean up old test pages and downloads every day
        setInterval(async () => {
            try {
                const now = Date.now();
                const retentionMs = this.settings.test_data_retention * 24 * 60 * 60 * 1000;
                
                // Clean up old test pages
                for (const [id, page] of this.testPages.entries()) {
                    if (now - page.created > retentionMs) {
                        this.testPages.delete(id);
                        console.log(`Cleaned up old test page: ${id}`);
                    }
                }
                
                // Clean up old downloads
                this.downloadHistory = this.downloadHistory.filter(d => 
                    now - d.timestamp < retentionMs
                );
                
                // Limit test pages
                if (this.testPages.size > this.settings.max_test_pages) {
                    const sortedPages = Array.from(this.testPages.entries())
                        .sort((a, b) => a[1].created - b[1].created);
                    
                    const toRemove = sortedPages.slice(0, this.testPages.size - this.settings.max_test_pages);
                    toRemove.forEach(([id]) => {
                        this.testPages.delete(id);
                        console.log(`Removed excess test page: ${id}`);
                    });
                }
                
                await this.saveData();
                console.log('Periodic cleanup completed');
            } catch (error) {
                console.error('Periodic cleanup failed:', error);
            }
        }, 24 * 60 * 60 * 1000); // Run once per day
    }
}

// Initialize the background service worker
const testExtensionBackground = new TestExtensionBackgroundV4();

// Handle service worker lifecycle
self.addEventListener('install', (event) => {
    console.log('Test Extension Service Worker installing...');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('Test Extension Service Worker activating...');
    event.waitUntil(self.clients.claim());
});

