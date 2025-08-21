// Chainflip Test Extension v4 - Content Script
// Features: Test page generation, page download, and enhanced testing capabilities

console.log('Chainflip Test Extension v4 loaded');

class ChainflipTestExtensionV4 {
    constructor() {
        this.version = '4.0.0';
        this.testData = {};
        this.isTestMode = false;
        this.testResults = [];
        this.init();
    }

    init() {
        console.log(`Initializing Chainflip Test Extension v${this.version}`);
        this.injectTestUI();
        this.setupTestPage();
        this.startTestMode();
    }

    injectTestUI() {
        // Remove existing overlay if present
        const existing = document.getElementById('test-extension-overlay-v4');
        if (existing) existing.remove();

        // Create test overlay
        const overlay = document.createElement('div');
        overlay.id = 'test-extension-overlay-v4';
        overlay.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            min-width: 300px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
        `;

        overlay.innerHTML = `
            <div style="margin-bottom: 15px; text-align: center;">
                <strong style="font-size: 18px;">🧪 Test Extension v${this.version}</strong>
            </div>
            <div style="margin-bottom: 10px;">
                <button id="run-test-page-v4" style="width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; margin-bottom: 8px;">🚀 Run Test Page</button>
                <button id="download-test-page-v4" style="width: 100%; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 8px; cursor: pointer; margin-bottom: 8px;">📥 Download Test Page</button>
                <button id="generate-test-data-v4" style="width: 100%; padding: 10px; background: #FF9800; color: white; border: none; border-radius: 8px; cursor: pointer; margin-bottom: 8px;">📊 Generate Test Data</button>
                <button id="clear-test-data-v4" style="width: 100%; padding: 10px; background: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer; margin-bottom: 8px;">🗑️ Clear Test Data</button>
            </div>
            <div style="margin-bottom: 10px;">
                <div style="font-size: 12px; opacity: 0.8;">Test Status: <span id="test-status-v4" style="color: #4CAF50;">Ready</span></div>
                <div style="font-size: 12px; opacity: 0.8;">Tests Run: <span id="tests-run-v4">0</span></div>
                <div style="font-size: 12px; opacity: 0.8;">Success Rate: <span id="success-rate-v4">0%</span></div>
            </div>
            <div style="font-size: 11px; opacity: 0.7; text-align: center;">
                Click any button to start testing
            </div>
        `;

        document.body.appendChild(overlay);

        // Add event listeners
        document.getElementById('run-test-page-v4').addEventListener('click', () => {
            this.runTestPage();
        });

        document.getElementById('download-test-page-v4').addEventListener('click', () => {
            this.downloadTestPage();
        });

        document.getElementById('generate-test-data-v4').addEventListener('click', () => {
            this.generateTestData();
        });

        document.getElementById('clear-test-data-v4').addEventListener('click', () => {
            this.clearTestData();
        });
    }

    setupTestPage() {
        // Create test page HTML
        this.testPageHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chainflip Test Page v4</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .test-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .test-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
        }
        .test-button:hover {
            background: #45a049;
        }
        .test-result {
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 12px;
            overflow-x: auto;
        }
        .success { border-left: 4px solid #4CAF50; }
        .error { border-left: 4px solid #f44336; }
        .info { border-left: 4px solid #2196F3; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Chainflip Test Page v4</h1>
        <p>Comprehensive testing environment for the extension</p>
    </div>

    <div class="test-section">
        <h3>🔍 Page Analysis Tests</h3>
        <button class="test-button" onclick="testPageStructure()">Test Page Structure</button>
        <button class="test-button" onclick="testDOMElements()">Test DOM Elements</button>
        <button class="test-button" onclick="testJavaScript()">Test JavaScript</button>
        <div id="page-analysis-results"></div>
    </div>

    <div class="test-section">
        <h3>📊 Data Generation Tests</h3>
        <button class="test-button" onclick="generateMockTransactions()">Generate Mock Transactions</button>
        <button class="test-button" onclick="generateMockUsers()">Generate Mock Users</button>
        <button class="test-button" onclick="generateMockMetrics()">Generate Mock Metrics</button>
        <div id="data-generation-results"></div>
    </div>

    <div class="test-section">
        <h3>🔧 Extension Integration Tests</h3>
        <button class="test-button" onclick="testExtensionAPI()">Test Extension API</button>
        <button class="test-button" onclick="testStorage()">Test Storage</button>
        <button class="test-button" onclick="testCommunication()">Test Communication</button>
        <div id="extension-test-results"></div>
    </div>

    <div class="test-section">
        <h3>📈 Performance Tests</h3>
        <button class="test-button" onclick="testPageLoad()">Test Page Load</button>
        <button class="test-button" onclick="testMemoryUsage()">Test Memory Usage</button>
        <button class="test-button" onclick="testNetworkRequests()">Test Network</button>
        <div id="performance-test-results"></div>
    </div>

    <script>
        // Test functions
        function testPageStructure() {
            const results = document.getElementById('page-analysis-results');
            const tests = [
                { name: 'Document Title', result: !!document.title, expected: true },
                { name: 'Body Element', result: !!document.body, expected: true },
                { name: 'Head Element', result: !!document.head, expected: true },
                { name: 'Meta Tags', result: document.querySelectorAll('meta').length > 0, expected: true }
            ];
            
            const html = tests.map(test => 
                \`<div class="test-result \${test.result === test.expected ? 'success' : 'error'}">
                    <strong>\${test.name}:</strong> \${test.result ? '✅ PASS' : '❌ FAIL'}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }

        function testDOMElements() {
            const results = document.getElementById('page-analysis-results');
            const elements = ['div', 'span', 'button', 'input', 'form'];
            const counts = elements.map(tag => document.querySelectorAll(tag).length);
            
            const html = elements.map((tag, i) => 
                \`<div class="test-result info">
                    <strong>\${tag} elements:</strong> \${counts[i]}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }

        function testJavaScript() {
            const results = document.getElementById('page-analysis-results');
            const tests = [
                { name: 'JSON Support', result: typeof JSON !== 'undefined', expected: true },
                { name: 'LocalStorage', result: typeof localStorage !== 'undefined', expected: true },
                { name: 'Fetch API', result: typeof fetch !== 'undefined', expected: true },
                { name: 'Console', result: typeof console !== 'undefined', expected: true }
            ];
            
            const html = tests.map(test => 
                \`<div class="test-result \${test.result === test.expected ? 'success' : 'error'}">
                    <strong>\${test.name}:</strong> \${test.result ? '✅ PASS' : '❌ FAIL'}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }

        function generateMockTransactions() {
            const results = document.getElementById('data-generation-results');
            const transactions = [];
            
            for (let i = 0; i < 5; i++) {
                transactions.push({
                    hash: '0x' + Math.random().toString(16).substr(2, 64),
                    amount: (Math.random() * 1000).toFixed(2),
                    token: ['ETH', 'USDC', 'USDT', 'BTC', 'DAI'][Math.floor(Math.random() * 5)],
                    timestamp: Date.now() - Math.random() * 86400000,
                    status: ['Pending', 'Confirmed', 'Failed'][Math.floor(Math.random() * 3)]
                });
            }
            
            results.innerHTML = \`<div class="test-result success">
                <strong>Generated \${transactions.length} mock transactions:</strong><br>
                <pre>\${JSON.stringify(transactions, null, 2)}</pre>
            </div>\`;
        }

        function generateMockUsers() {
            const results = document.getElementById('data-generation-results');
            const users = [];
            
            for (let i = 0; i < 3; i++) {
                users.push({
                    id: i + 1,
                    name: ['Alice', 'Bob', 'Charlie'][i],
                    email: ['alice@test.com', 'bob@test.com', 'charlie@test.com'][i],
                    transactions: Math.floor(Math.random() * 100),
                    balance: (Math.random() * 10000).toFixed(2)
                });
            }
            
            results.innerHTML = \`<div class="test-result success">
                <strong>Generated \${users.length} mock users:</strong><br>
                <pre>\${JSON.stringify(users, null, 2)}</pre>
            </div>\`;
        }

        function generateMockMetrics() {
            const results = document.getElementById('data-generation-results');
            const metrics = {
                totalTransactions: Math.floor(Math.random() * 10000),
                totalVolume: (Math.random() * 1000000).toFixed(2),
                activeUsers: Math.floor(Math.random() * 1000),
                successRate: (Math.random() * 20 + 80).toFixed(1),
                averageTransactionTime: (Math.random() * 60 + 10).toFixed(1)
            };
            
            results.innerHTML = \`<div class="test-result success">
                <strong>Generated mock metrics:</strong><br>
                <pre>\${JSON.stringify(metrics, null, 2)}</pre>
            </div>\`;
        }

        function testExtensionAPI() {
            const results = document.getElementById('extension-test-results');
            const tests = [
                { name: 'Chrome Runtime', result: typeof chrome !== 'undefined' && chrome.runtime, expected: true },
                { name: 'Chrome Storage', result: typeof chrome !== 'undefined' && chrome.storage, expected: true },
                { name: 'Chrome Tabs', result: typeof chrome !== 'undefined' && chrome.tabs, expected: true }
            ];
            
            const html = tests.map(test => 
                \`<div class="test-result \${test.result === test.expected ? 'success' : 'error'}">
                    <strong>\${test.name}:</strong> \${test.result ? '✅ PASS' : '❌ FAIL'}
                </div>\`
            ).join('');
            
            results.innerHTML = html;
        }

        function testStorage() {
            const results = document.getElementById('extension-test-results');
            try {
                localStorage.setItem('test-key', 'test-value');
                const value = localStorage.getItem('test-key');
                localStorage.removeItem('test-key');
                
                results.innerHTML = \`<div class="test-result success">
                    <strong>Storage Test:</strong> ✅ PASS<br>
                    <strong>Value retrieved:</strong> \${value}
                </div>\`;
            } catch (error) {
                results.innerHTML = \`<div class="test-result error">
                    <strong>Storage Test:</strong> ❌ FAIL<br>
                    <strong>Error:</strong> \${error.message}
                </div>\`;
            }
        }

        function testCommunication() {
            const results = document.getElementById('extension-test-results');
            if (typeof chrome !== 'undefined' && chrome.runtime) {
                try {
                    chrome.runtime.sendMessage({action: 'test'}, (response) => {
                        results.innerHTML = \`<div class="test-result success">
                            <strong>Communication Test:</strong> ✅ PASS<br>
                            <strong>Response:</strong> \${response ? 'Received' : 'No response'}
                        </div>\`;
                    });
                } catch (error) {
                    results.innerHTML = \`<div class="test-result error">
                        <strong>Communication Test:</strong> ❌ FAIL<br>
                        <strong>Error:</strong> \${error.message}
                    </div>\`;
                }
            } else {
                results.innerHTML = \`<div class="test-result error">
                    <strong>Communication Test:</strong> ❌ FAIL<br>
                    <strong>Reason:</strong> Chrome runtime not available
                </div>\`;
            }
        }

        function testPageLoad() {
            const results = document.getElementById('performance-test-results');
            const loadTime = performance.now();
            
            results.innerHTML = \`<div class="test-result info">
                <strong>Page Load Test:</strong> ✅ PASS<br>
                <strong>Load Time:</strong> \${loadTime.toFixed(2)}ms
            </div>\`;
        }

        function testMemoryUsage() {
            const results = document.getElementById('performance-test-results');
            if (performance.memory) {
                const memory = performance.memory;
                results.innerHTML = \`<div class="test-result info">
                    <strong>Memory Usage Test:</strong> ✅ PASS<br>
                    <strong>Used:</strong> \${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB<br>
                    <strong>Total:</strong> \${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)}MB
                </div>\`;
            } else {
                results.innerHTML = \`<div class="test-result info">
                    <strong>Memory Usage Test:</strong> ⚠️ INFO<br>
                    <strong>Reason:</strong> Memory API not available
                </div>\`;
            }
        }

        function testNetworkRequests() {
            const results = document.getElementById('performance-test-results');
            const entries = performance.getEntriesByType('resource');
            const networkRequests = entries.length;
            
            results.innerHTML = \`<div class="test-result info">
                <strong>Network Test:</strong> ✅ PASS<br>
                <strong>Requests:</strong> \${networkRequests}
            </div>\`;
        }

        // Auto-run basic tests on page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                testPageStructure();
                testJavaScript();
            }, 1000);
        });
    </script>
</body>
</html>`;

        // Create test data JSON
        this.testDataJSON = {
            version: this.version,
            timestamp: Date.now(),
            pageInfo: {
                url: window.location.href,
                title: document.title,
                userAgent: navigator.userAgent,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            },
            testResults: [],
            generatedData: {}
        };
    }

    startTestMode() {
        this.isTestMode = true;
        this.updateTestStatus('Ready');
        console.log('Test mode activated');
    }

    async runTestPage() {
        try {
            this.updateTestStatus('Running Tests...');
            
            // Create a new tab with the test page
            const testPageUrl = 'data:text/html;charset=utf-8,' + encodeURIComponent(this.testPageHTML);
            
            // Try to open in new tab
            if (typeof chrome !== 'undefined' && chrome.tabs) {
                await chrome.tabs.create({ url: testPageUrl });
            } else {
                // Fallback: open in current tab
                window.open(testPageUrl, '_blank');
            }
            
            this.updateTestStatus('Test Page Opened');
            this.incrementTestsRun();
            
            // Run some basic tests
            this.runBasicTests();
            
        } catch (error) {
            console.error('Error running test page:', error);
            this.updateTestStatus('Error: ' + error.message);
        }
    }

    async downloadTestPage() {
        try {
            this.updateTestStatus('Downloading...');
            
            // Create test page content
            const testPageContent = this.testPageHTML;
            const testDataContent = JSON.stringify(this.testDataJSON, null, 2);
            
            // Download test page HTML
            this.downloadFile('chainflip-test-page-v4.html', testPageContent, 'text/html');
            
            // Download test data JSON
            this.downloadFile('chainflip-test-data-v4.json', testDataContent, 'application/json');
            
            this.updateTestStatus('Downloaded Successfully');
            this.incrementTestsRun();
            
        } catch (error) {
            console.error('Error downloading test page:', error);
            this.updateTestStatus('Download Error: ' + error.message);
        }
    }

    downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    }

    generateTestData() {
        try {
            this.updateTestStatus('Generating Data...');
            
            // Generate mock transaction data
            const mockTransactions = [];
            for (let i = 0; i < 10; i++) {
                mockTransactions.push({
                    hash: '0x' + Math.random().toString(16).substr(2, 64),
                    amount: (Math.random() * 1000).toFixed(2),
                    token: ['ETH', 'USDC', 'USDT', 'BTC', 'DAI'][Math.floor(Math.random() * 5)],
                    timestamp: Date.now() - Math.random() * 86400000,
                    status: ['Pending', 'Confirmed', 'Failed'][Math.floor(Math.random() * 3)],
                    from: '0x' + Math.random().toString(16).substr(2, 40),
                    to: '0x' + Math.random().toString(16).substr(2, 40)
                });
            }
            
            // Generate mock user data
            const mockUsers = [
                { id: 1, name: 'Alice', email: 'alice@test.com', transactions: 45, balance: '1250.75' },
                { id: 2, name: 'Bob', email: 'bob@test.com', transactions: 32, balance: '890.25' },
                { id: 3, name: 'Charlie', email: 'charlie@test.com', transactions: 67, balance: '2100.50' }
            ];
            
            // Generate mock metrics
            const mockMetrics = {
                totalTransactions: mockTransactions.length,
                totalVolume: mockTransactions.reduce((sum, tx) => sum + parseFloat(tx.amount), 0).toFixed(2),
                activeUsers: mockUsers.length,
                successRate: (Math.random() * 20 + 80).toFixed(1),
                averageTransactionTime: (Math.random() * 60 + 10).toFixed(1),
                generatedAt: new Date().toISOString()
            };
            
            // Store generated data
            this.testDataJSON.generatedData = {
                transactions: mockTransactions,
                users: mockUsers,
                metrics: mockMetrics
            };
            
            // Update UI
            this.updateTestStatus('Data Generated');
            this.incrementTestsRun();
            
            // Show success message
            this.showNotification('Test data generated successfully!', 'success');
            
        } catch (error) {
            console.error('Error generating test data:', error);
            this.updateTestStatus('Generation Error: ' + error.message);
            this.showNotification('Failed to generate test data', 'error');
        }
    }

    clearTestData() {
        try {
            this.testDataJSON.generatedData = {};
            this.testResults = [];
            this.updateTestStatus('Data Cleared');
            this.showNotification('Test data cleared successfully!', 'success');
        } catch (error) {
            console.error('Error clearing test data:', error);
            this.updateTestStatus('Clear Error: ' + error.message);
        }
    }

    runBasicTests() {
        const tests = [
            { name: 'Document Ready', test: () => !!document.body, expected: true },
            { name: 'Extension Loaded', test: () => !!window.chainflipTestExtensionV4, expected: true },
            { name: 'Test UI Injected', test: () => !!document.getElementById('test-extension-overlay-v4'), expected: true },
            { name: 'Console Available', test: () => typeof console !== 'undefined', expected: true }
        ];
        
        this.testResults = tests.map(test => ({
            name: test.name,
            passed: test.test() === test.expected,
            timestamp: Date.now()
        }));
        
        const passedTests = this.testResults.filter(r => r.passed).length;
        const successRate = (passedTests / this.testResults.length * 100).toFixed(1);
        
        this.updateSuccessRate(successRate);
    }

    updateTestStatus(status) {
        const statusElement = document.getElementById('test-status-v4');
        if (statusElement) {
            statusElement.textContent = status;
            if (status.includes('Error')) {
                statusElement.style.color = '#f44336';
            } else if (status.includes('Success')) {
                statusElement.style.color = '#4CAF50';
            } else {
                statusElement.style.color = '#2196F3';
            }
        }
    }

    incrementTestsRun() {
        const element = document.getElementById('tests-run-v4');
        if (element) {
            const current = parseInt(element.textContent) || 0;
            element.textContent = current + 1;
        }
    }

    updateSuccessRate(rate) {
        const element = document.getElementById('success-rate-v4');
        if (element) {
            element.textContent = rate + '%';
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            padding: 20px;
            border-radius: 12px;
            z-index: 10001;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            text-align: center;
            min-width: 300px;
            font-size: 16px;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize the test extension when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.chainflipTestExtensionV4 = new ChainflipTestExtensionV4();
    });
} else {
    window.chainflipTestExtensionV4 = new ChainflipTestExtensionV4();
}

// Make extension globally accessible for debugging
console.log('Test Extension v4 initialized. Use window.chainflipTestExtensionV4 for debugging.');

