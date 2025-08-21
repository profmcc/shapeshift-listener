// Chainflip Affiliate Tracker v3 - Background Service Worker
// Handles background tasks and data management with improved connection handling

console.log('Chainflip Affiliate Tracker v3 Background Service Worker loaded');

class BackgroundServiceWorker {
    constructor() {
        this.version = '3.0.0';
        this.connections = new Map();
        this.transactions = [];
        this.settings = {
            auto_track: true,
            notifications: true,
            export_format: 'json',
            connection_timeout: 5000,
            max_retries: 5
        };
        this.init();
    }

    init() {
        console.log(`Initializing Background Service Worker v${this.version}`);
        
        // Load existing data
        this.loadData();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up periodic cleanup
        this.setupPeriodicCleanup();
        
        console.log('Background Service Worker initialized successfully');
    }

    setupEventListeners() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            console.log('Extension installed:', details.reason);
            
            if (details.reason === 'install') {
                this.initializeStorage();
            } else if (details.reason === 'update') {
                this.handleUpdate();
            }
        });

        // Handle connection requests from content scripts
        chrome.runtime.onConnect.addListener((port) => {
            console.log('New connection request from:', port.sender.tab?.url);
            
            if (port.name === 'chainflip-tracker-v3') {
                this.handleContentScriptConnection(port);
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
            if (changeInfo.status === 'complete' && tab.url && this.isChainflipUrl(tab.url)) {
                console.log('Chainflip tab updated, ensuring content script is active');
                this.ensureContentScriptActive(tabId);
            }
        });

        // Handle extension icon click
        chrome.action.onClicked.addListener((tab) => {
            if (tab.url && this.isChainflipUrl(tab.url)) {
                console.log('Extension icon clicked on Chainflip tab');
                this.toggleContentScript(tab.id);
            } else {
                // Open Chainflip in new tab
                chrome.tabs.create({ url: 'https://app.chainflip.io' });
            }
        });
    }

    handleContentScriptConnection(port) {
        const connectionId = this.generateConnectionId();
        
        // Store connection
        this.connections.set(connectionId, {
            port: port,
            tabId: port.sender.tab?.id,
            url: port.sender.tab?.url,
            connected: Date.now()
        });

        console.log(`Content script connected: ${connectionId}`);

        // Handle messages from this connection
        port.onMessage.addListener((message) => {
            console.log(`Message from ${connectionId}:`, message);
            this.handlePortMessage(connectionId, message);
        });

        // Handle disconnection
        port.onDisconnect.addListener(() => {
            console.log(`Content script disconnected: ${connectionId}`);
            this.connections.delete(connectionId);
        });

        // Send connection confirmation
        port.postMessage({
            action: 'connection_test_response',
            connectionId: connectionId,
            success: true,
            version: this.version
        });
    }

    handlePortMessage(connectionId, message) {
        const connection = this.connections.get(connectionId);
        if (!connection) return;

        switch (message.action) {
            case 'connection_test':
                this.handleConnectionTest(connectionId, message);
                break;
            case 'new_transaction':
                this.handleNewTransaction(connectionId, message);
                break;
            case 'save_transactions':
                this.handleSaveTransactions(connectionId, message);
                break;
            case 'get_transactions':
                this.handleGetTransactions(connectionId, message);
                break;
            default:
                console.log(`Unknown message action: ${message.action}`);
        }
    }

    handleConnectionTest(connectionId, message) {
        const connection = this.connections.get(connectionId);
        if (connection) {
            connection.port.postMessage({
                action: 'connection_test_response',
                success: true,
                connectionId: connectionId,
                version: this.version
            });
        }
    }

    handleNewTransaction(connectionId, message) {
        if (message.transaction) {
            // Add transaction if not already present
            const existingIndex = this.transactions.findIndex(tx => tx.hash === message.transaction.hash);
            if (existingIndex === -1) {
                this.transactions.push(message.transaction);
                this.saveData();
                console.log(`New transaction added: ${message.transaction.hash}`);
            }
        }
    }

    handleSaveTransactions(connectionId, message) {
        if (message.transactions && Array.isArray(message.transactions)) {
            this.transactions = message.transactions;
            this.saveData();
            
            const connection = this.connections.get(connectionId);
            if (connection) {
                connection.port.postMessage({
                    action: 'save_transactions_response',
                    success: true,
                    count: this.transactions.length
                });
            }
        }
    }

    handleGetTransactions(connectionId, message) {
        const connection = this.connections.get(connectionId);
        if (connection) {
            connection.port.postMessage({
                action: 'get_transactions_response',
                success: true,
                transactions: this.transactions,
                count: this.transactions.length
            });
        }
    }

    handleMessage(request, sender, sendResponse) {
        switch (request.action) {
            case 'get_transactions':
                this.getTransactions(sendResponse);
                break;
            case 'save_transaction':
                this.saveTransaction(request.transaction, sendResponse);
                break;
            case 'export_data':
                this.exportTransactionData(request.format || 'json', sendResponse);
                break;
            case 'clear_data':
                this.clearData(sendResponse);
                break;
            case 'get_settings':
                this.getSettings(sendResponse);
                break;
            case 'update_settings':
                this.updateSettings(request.settings, sendResponse);
                break;
            default:
                sendResponse({ error: 'Unknown action' });
        }
    }

    async getTransactions(sendResponse) {
        try {
            const result = await chrome.storage.local.get(['chainflip_transactions_v3']);
            const transactions = result.chainflip_transactions_v3 || [];
            sendResponse({ 
                success: true, 
                transactions: transactions,
                count: transactions.length 
            });
        } catch (error) {
            console.error('Error getting transactions:', error);
            sendResponse({ error: 'Failed to get transactions' });
        }
    }

    async saveTransaction(transaction, sendResponse) {
        try {
            const result = await chrome.storage.local.get(['chainflip_transactions_v3']);
            const transactions = result.chainflip_transactions_v3 || [];
            
            // Check if transaction already exists
            const existingIndex = transactions.findIndex(tx => tx.hash === transaction.hash);
            if (existingIndex === -1) {
                transactions.push(transaction);
            } else {
                // Update existing transaction
                transactions[existingIndex] = { ...transactions[existingIndex], ...transaction };
            }
            
            await chrome.storage.local.set({
                'chainflip_transactions_v3': transactions,
                'last_updated_v3': Date.now()
            });
            
            this.transactions = transactions;
            sendResponse({ success: true, count: transactions.length });
        } catch (error) {
            console.error('Error saving transaction:', error);
            sendResponse({ error: 'Failed to save transaction' });
        }
    }

    async exportTransactionData(format, sendResponse) {
        try {
            const result = await chrome.storage.local.get(['chainflip_transactions_v3']);
            const transactions = result.chainflip_transactions_v3 || [];
            
            if (transactions.length === 0) {
                sendResponse({ error: 'No transactions to export' });
                return;
            }

            if (format === 'csv') {
                this.exportAsCSV(transactions);
            } else {
                this.exportAsJSON(transactions);
            }
            
            sendResponse({ success: true });
        } catch (error) {
            console.error('Export error:', error);
            sendResponse({ error: 'Failed to export data' });
        }
    }

    async clearData(sendResponse) {
        try {
            await chrome.storage.local.remove(['chainflip_transactions_v3', 'last_updated_v3']);
            this.transactions = [];
            sendResponse({ success: true });
        } catch (error) {
            console.error('Clear data error:', error);
            sendResponse({ error: 'Failed to clear data' });
        }
    }

    async getSettings(sendResponse) {
        try {
            const result = await chrome.storage.local.get(['settings_v3']);
            const settings = result.settings_v3 || this.settings;
            sendResponse({ success: true, settings: settings });
        } catch (error) {
            console.error('Error getting settings:', error);
            sendResponse({ error: 'Failed to get settings' });
        }
    }

    async updateSettings(newSettings, sendResponse) {
        try {
            this.settings = { ...this.settings, ...newSettings };
            await chrome.storage.local.set({ 'settings_v3': this.settings });
            sendResponse({ success: true, settings: this.settings });
        } catch (error) {
            console.error('Error updating settings:', error);
            sendResponse({ error: 'Failed to update settings' });
        }
    }

    async initializeStorage() {
        try {
            await chrome.storage.local.set({
                'chainflip_transactions_v3': [],
                'last_updated_v3': Date.now(),
                'version_v3': this.version,
                'settings_v3': this.settings
            });
            console.log('Storage initialized successfully');
        } catch (error) {
            console.error('Failed to initialize storage:', error);
        }
    }

    async loadData() {
        try {
            const result = await chrome.storage.local.get([
                'chainflip_transactions_v3',
                'settings_v3'
            ]);
            
            this.transactions = result.chainflip_transactions_v3 || [];
            this.settings = result.settings_v3 || this.settings;
            
            console.log(`Loaded ${this.transactions.length} transactions from storage`);
        } catch (error) {
            console.error('Failed to load data:', error);
        }
    }

    async saveData() {
        try {
            await chrome.storage.local.set({
                'chainflip_transactions_v3': this.transactions,
                'last_updated_v3': Date.now()
            });
        } catch (error) {
            console.error('Failed to save data:', error);
        }
    }

    handleUpdate() {
        console.log('Extension updated, checking for data migration...');
        // Handle any necessary data migrations here
    }

    isChainflipUrl(url) {
        return url.includes('app.chainflip.io') || 
               url.includes('chainflip.io') ||
               url.includes('broker.chainflip.io');
    }

    async ensureContentScriptActive(tabId) {
        try {
            // Check if content script is already injected
            const results = await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: () => {
                    return window.chainflipAffiliateTrackerV3 !== undefined;
                }
            });
            
            if (results && results[0] && !results[0].result) {
                console.log('Injecting content script into Chainflip tab');
                await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content.js']
                });
            }
        } catch (error) {
            console.error('Failed to ensure content script is active:', error);
        }
    }

    async toggleContentScript(tabId) {
        try {
            // Send message to toggle content script interface
            await chrome.tabs.sendMessage(tabId, { action: 'toggle_interface' });
        } catch (error) {
            console.error('Failed to toggle content script interface:', error);
        }
    }

    generateConnectionId() {
        return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    exportAsJSON(transactions) {
        const dataStr = JSON.stringify(transactions, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const url = URL.createObjectURL(dataBlob);
        chrome.downloads.download({
            url: url,
            filename: `chainflip_transactions_v${this.version}_${new Date().toISOString().split('T')[0]}.json`,
            saveAs: true
        });
    }

    exportAsCSV(transactions) {
        if (transactions.length === 0) return;
        
        // Get all unique keys from transactions
        const keys = new Set();
        transactions.forEach(tx => {
            Object.keys(tx).forEach(key => keys.add(key));
        });
        
        const csvHeaders = Array.from(keys).join(',');
        const csvRows = transactions.map(tx => {
            return Array.from(keys).map(key => {
                const value = tx[key] || '';
                // Escape commas and quotes
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            }).join(',');
        });
        
        const csvContent = [csvHeaders, ...csvRows].join('\n');
        const dataBlob = new Blob([csvContent], { type: 'text/csv' });
        
        const url = URL.createObjectURL(dataBlob);
        chrome.downloads.download({
            url: url,
            filename: `chainflip_transactions_v${this.version}_${new Date().toISOString().split('T')[0]}.csv`,
            saveAs: true
        });
    }

    setupPeriodicCleanup() {
        // Clean up old transactions every day
        setInterval(async () => {
            try {
                const result = await chrome.storage.local.get(['chainflip_transactions_v3']);
                const transactions = result.chainflip_transactions_v3 || [];
                const now = Date.now();
                const oneWeekAgo = now - (7 * 24 * 60 * 60 * 1000); // 7 days
                
                const filteredTransactions = transactions.filter(tx => {
                    return tx.timestamp && tx.timestamp > oneWeekAgo;
                });
                
                if (filteredTransactions.length !== transactions.length) {
                    await chrome.storage.local.set({
                        'chainflip_transactions_v3': filteredTransactions,
                        'last_updated_v3': now
                    });
                    this.transactions = filteredTransactions;
                    console.log(`Cleaned up ${transactions.length - filteredTransactions.length} old transactions`);
                }
            } catch (error) {
                console.error('Periodic cleanup failed:', error);
            }
        }, 24 * 60 * 60 * 1000); // Run once per day
    }
}

// Initialize the background service worker
const backgroundWorker = new BackgroundServiceWorker();

// Handle service worker lifecycle
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(self.clients.claim());
});


