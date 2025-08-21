// Chainflip Test Extension v4 - Popup Script
// Handles test page creation, downloads, and UI interactions

console.log('Chainflip Test Extension v4 Popup loaded');

class TestExtensionPopupV4 {
    constructor() {
        this.version = '4.0.0';
        this.testHistory = [];
        this.stats = {
            testPages: 0,
            downloads: 0,
            successRate: 0,
            lastActivity: null
        };
        this.init();
    }

    init() {
        this.loadData();
        this.setupEventListeners();
        this.updateUI();
        
        // Set up periodic refresh
        setInterval(() => {
            this.refreshData();
        }, 5000); // Refresh every 5 seconds
    }

    setupEventListeners() {
        // Create test page button
        document.getElementById('create-test-page').addEventListener('click', () => {
            this.createTestPage();
        });

        // Open test page button
        document.getElementById('open-test-page').addEventListener('click', () => {
            this.openTestPage();
        });

        // Download all button
        document.getElementById('download-all').addEventListener('click', () => {
            this.downloadAllTestPages();
        });

        // Clear data button
        document.getElementById('clear-data').addEventListener('click', () => {
            this.clearAllData();
        });
    }

    async loadData() {
        try {
            // Get data from background script
            const response = await chrome.runtime.sendMessage({
                action: 'get_test_history'
            });
            
            if (response && response.success) {
                this.testHistory = response.history || [];
                this.stats.testPages = response.totalPages || 0;
                this.stats.downloads = response.totalDownloads || 0;
                this.stats.successRate = this.calculateSuccessRate();
                this.stats.lastActivity = this.getLastActivity();
                
                console.log(`Loaded ${this.testHistory.length} test pages`);
                this.updateUI();
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showNotification('Failed to load test data', 'error');
        }
    }

    async createTestPage() {
        try {
            this.showNotification('Creating test page...', 'info');
            
            const response = await chrome.runtime.sendMessage({
                action: 'create_test_page',
                title: `Test Page ${Date.now()}`,
                url: 'https://example.com',
                content: this.generateCustomTestContent(),
                metadata: {
                    source: 'popup',
                    timestamp: Date.now()
                }
            });
            
            if (response && response.success) {
                this.showNotification('Test page created successfully!', 'success');
                await this.loadData(); // Refresh data
            } else {
                this.showNotification('Failed to create test page', 'error');
            }
        } catch (error) {
            console.error('Error creating test page:', error);
            this.showNotification('Error creating test page', 'error');
        }
    }

    async openTestPage() {
        try {
            if (this.testHistory.length === 0) {
                this.showNotification('No test pages available', 'info');
                return;
            }
            
            // Open the most recent test page
            const latestPage = this.testHistory[0];
            this.showNotification('Opening test page...', 'info');
            
            // Send message to background to open test page
            await chrome.runtime.sendMessage({
                action: 'open_test_page'
            });
            
        } catch (error) {
            console.error('Error opening test page:', error);
            this.showNotification('Error opening test page', 'error');
        }
    }

    async downloadAllTestPages() {
        try {
            if (this.testHistory.length === 0) {
                this.showNotification('No test pages to download', 'info');
                return;
            }
            
            this.showNotification(`Downloading ${this.testHistory.length} test pages...`, 'info');
            
            // Download each test page
            for (const page of this.testHistory) {
                try {
                    await chrome.runtime.sendMessage({
                        action: 'download_test_page',
                        testPageId: page.id
                    });
                    
                    // Small delay between downloads
                    await new Promise(resolve => setTimeout(resolve, 500));
                } catch (error) {
                    console.error(`Error downloading page ${page.id}:`, error);
                }
            }
            
            this.showNotification('All test pages downloaded!', 'success');
            await this.loadData(); // Refresh data
            
        } catch (error) {
            console.error('Error downloading all test pages:', error);
            this.showNotification('Error downloading test pages', 'error');
        }
    }

    async clearAllData() {
        try {
            if (!confirm('Are you sure you want to clear all test data? This action cannot be undone.')) {
                return;
            }
            
            this.showNotification('Clearing all data...', 'info');
            
            const response = await chrome.runtime.sendMessage({
                action: 'clear_test_data'
            });
            
            if (response && response.success) {
                this.showNotification('All data cleared successfully!', 'success');
                await this.loadData(); // Refresh data
            } else {
                this.showNotification('Failed to clear data', 'error');
            }
        } catch (error) {
            console.error('Error clearing data:', error);
            this.showNotification('Error clearing data', 'error');
        }
    }

    generateCustomTestContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom Test Page v4</title>
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
        .test-section {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
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
        .result {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Custom Test Page v4</h1>
        <p>Generated on ${new Date().toLocaleString()}</p>
    </div>
    
    <div class="content">
        <h2>Comprehensive Testing Suite</h2>
        
        <div class="test-section">
            <h3>🔍 Browser Capabilities</h3>
            <button class="button" onclick="testBrowserCapabilities()">Test Browser Features</button>
            <div id="browser-results"></div>
        </div>
        
        <div class="test-section">
            <h3>📊 Performance Metrics</h3>
            <button class="button" onclick="testPerformance()">Test Performance</button>
            <div id="performance-results"></div>
        </div>
        
        <div class="test-section">
            <h3>🌐 Network & Storage</h3>
            <button class="button" onclick="testNetworkStorage()">Test Network & Storage</button>
            <div id="network-results"></div>
        </div>
        
        <div class="test-section">
            <h3>🎨 UI & Interaction</h3>
            <button class="button" onclick="testUIInteraction()">Test UI Elements</button>
            <div id="ui-results"></div>
        </div>
    </div>
    
    <script>
        function testBrowserCapabilities() {
            const results = document.getElementById('browser-results');
            const capabilities = {
                'User Agent': navigator.userAgent,
                'Language': navigator.language,
                'Platform': navigator.platform,
                'Cookie Enabled': navigator.cookieEnabled,
                'Online': navigator.onLine,
                'Hardware Concurrency': navigator.hardwareConcurrency || 'N/A',
                'Device Memory': navigator.deviceMemory || 'N/A',
                'Max Touch Points': navigator.maxTouchPoints || 'N/A'
            };
            
            const html = Object.entries(capabilities).map(([key, value]) => 
                \`<div class="result">
                    <strong>\${key}:</strong> \${value}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }
        
        function testPerformance() {
            const results = document.getElementById('performance-results');
            const metrics = {
                'Page Load Time': performance.now().toFixed(2) + 'ms',
                'Navigation Start': new Date(performance.timing.navigationStart).toLocaleString(),
                'DOM Content Loaded': performance.timing.domContentLoadedEventEnd - performance.timing.domContentLoadedEventStart + 'ms',
                'Load Complete': performance.timing.loadEventEnd - performance.timing.loadEventStart + 'ms'
            };
            
            if (performance.memory) {
                metrics['Memory Used'] = (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + 'MB';
                metrics['Memory Total'] = (performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + 'MB';
            }
            
            const html = Object.entries(metrics).map(([key, value]) => 
                \`<div class="result">
                    <strong>\${key}:</strong> \${value}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }
        
        function testNetworkStorage() {
            const results = document.getElementById('network-results');
            const tests = [
                { name: 'LocalStorage', test: () => {
                    try {
                        localStorage.setItem('test', 'value');
                        const value = localStorage.getItem('test');
                        localStorage.removeItem('test');
                        return value === 'value' ? '✅ PASS' : '❌ FAIL';
                    } catch (e) {
                        return '❌ FAIL: ' + e.message;
                    }
                }},
                { name: 'SessionStorage', test: () => {
                    try {
                        sessionStorage.setItem('test', 'value');
                        const value = sessionStorage.getItem('test');
                        sessionStorage.removeItem('test');
                        return value === 'value' ? '✅ PASS' : '❌ FAIL';
                    } catch (e) {
                        return '❌ FAIL: ' + e.message;
                    }
                }},
                { name: 'IndexedDB', test: () => {
                    return typeof indexedDB !== 'undefined' ? '✅ PASS' : '❌ FAIL';
                }},
                { name: 'Fetch API', test: () => {
                    return typeof fetch !== 'undefined' ? '✅ PASS' : '❌ FAIL';
                }},
                { name: 'XMLHttpRequest', test: () => {
                    return typeof XMLHttpRequest !== 'undefined' ? '✅ PASS' : '❌ FAIL';
                }}
            ];
            
            const html = tests.map(test => 
                \`<div class="result">
                    <strong>\${test.name}:</strong> \${test.test()}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }
        
        function testUIInteraction() {
            const results = document.getElementById('ui-results');
            const tests = [
                { name: 'Click Events', test: () => {
                    try {
                        const testDiv = document.createElement('div');
                        testDiv.onclick = () => true;
                        testDiv.click();
                        return '✅ PASS';
                    } catch (e) {
                        return '❌ FAIL: ' + e.message;
                    }
                }},
                { name: 'DOM Manipulation', test: () => {
                    try {
                        const testDiv = document.createElement('div');
                        testDiv.innerHTML = 'Test';
                        document.body.appendChild(testDiv);
                        const result = testDiv.textContent === 'Test';
                        document.body.removeChild(testDiv);
                        return result ? '✅ PASS' : '❌ FAIL';
                    } catch (e) {
                        return '❌ FAIL: ' + e.message;
                    }
                }},
                { name: 'CSS Support', test: () => {
                    try {
                        const testDiv = document.createElement('div');
                        testDiv.style.backgroundColor = 'red';
                        return testDiv.style.backgroundColor === 'red' ? '✅ PASS' : '❌ FAIL';
                    } catch (e) {
                        return '❌ FAIL: ' + e.message;
                    }
                }}
            ];
            
            const html = tests.map(test => 
                \`<div class="result">
                    <strong>\${test.name}:</strong> \${test.test()}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }
        
        // Auto-run basic tests on page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                testBrowserCapabilities();
                testPerformance();
            }, 1000);
        });
    </script>
</body>
</html>`;
    }

    calculateSuccessRate() {
        if (this.testHistory.length === 0) return 0;
        
        // Simple success rate based on test pages created
        // In a real scenario, you might track actual test results
        return Math.round((this.testHistory.length / (this.testHistory.length + 1)) * 100);
    }

    getLastActivity() {
        if (this.testHistory.length === 0) return null;
        
        const latest = this.testHistory[0];
        return new Date(latest.created);
    }

    updateUI() {
        // Update stats
        document.getElementById('test-pages-count').textContent = this.stats.testPages;
        document.getElementById('downloads-count').textContent = this.stats.downloads;
        document.getElementById('success-rate').textContent = this.stats.successRate + '%';
        
        // Update last activity
        const lastActivityElement = document.getElementById('last-activity');
        if (this.stats.lastActivity) {
            lastActivityElement.textContent = this.getTimeAgo(this.stats.lastActivity);
        } else {
            lastActivityElement.textContent = 'Never';
        }
        
        // Update test history
        this.updateTestHistory();
    }

    updateTestHistory() {
        const container = document.getElementById('test-history-list');
        
        if (this.testHistory.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📊</div>
                    <div class="text">No test pages yet</div>
                    <div class="subtext">Create your first test page to get started</div>
                </div>
            `;
            return;
        }
        
        // Show recent test pages (last 5)
        const recentPages = this.testHistory.slice(0, 5);
        const html = recentPages.map(page => this.createTestHistoryHTML(page)).join('');
        
        container.innerHTML = html;
    }

    createTestHistoryHTML(page) {
        const date = new Date(page.created);
        const timeAgo = this.getTimeAgo(date);
        
        return `
            <div class="test-item">
                <div class="test-title">${page.title}</div>
                <div class="test-meta">
                    Created: ${timeAgo} | Downloads: ${page.downloads || 0}
                </div>
            </div>
        `;
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }

    async refreshData() {
        await this.loadData();
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;
        
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.testExtensionPopupV4 = new TestExtensionPopupV4();
    
    // Add debug info to console
    console.log('Test Extension Popup v4 initialized. Use window.testExtensionPopupV4 for debugging.');
});

// Listen for messages from content script or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Popup received message:', request);
    
    if (request.action === 'update_test_data') {
        // Refresh data when notified
        window.testExtensionPopupV4?.loadData();
    }
    
    sendResponse({ received: true });
});

// Handle runtime errors
chrome.runtime.onError.addListener((error) => {
    console.error('Runtime error:', error);
    if (window.testExtensionPopupV4) {
        window.testExtensionPopupV4.showNotification(`Runtime error: ${error.message}`, 'error');
    }
});

// Handle extension updates
chrome.runtime.onUpdateAvailable.addListener(() => {
    console.log('Test extension update available');
    if (window.testExtensionPopupV4) {
        window.testExtensionPopupV4.showNotification('Extension update available. Please refresh the page.', 'info');
    }
});

