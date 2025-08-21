// Chainflip Affiliate Tracker v3 - Content Script
// Tracks ShapeShift affiliate transactions on Chainflip protocol
// Improved connection handling and error recovery

console.log('Chainflip Affiliate Tracker v3 loaded');

class ChainflipAffiliateTrackerV3 {
    constructor() {
        this.version = '3.0.0';
        this.affiliateAddress = '0x0000000000000000000000000000000000000000'; // Replace with actual ShapeShift address
        this.transactions = [];
        this.isTracking = false;
        this.connectionRetries = 0;
        this.maxRetries = 5;
        this.retryDelay = 2000;
        this.backgroundPort = null;
        this.init();
    }

    async init() {
        console.log(`Initializing Chainflip Affiliate Tracker v${this.version}`);
        
        try {
            await this.establishConnection();
            this.setupMutationObserver();
            this.injectTrackingUI();
            this.startTracking();
            this.setupPeriodicConnectionCheck();
        } catch (error) {
            console.error('Initialization failed:', error);
            this.handleConnectionError();
        }
    }

    async establishConnection() {
        try {
            // Try to connect to background script
            this.backgroundPort = chrome.runtime.connect({ name: 'chainflip-tracker-v3' });
            
            this.backgroundPort.onMessage.addListener((message) => {
                console.log('Content script received message:', message);
                this.handleBackgroundMessage(message);
            });

            this.backgroundPort.onDisconnect.addListener(() => {
                console.log('Background port disconnected');
                this.backgroundPort = null;
                this.handleConnectionError();
            });

            // Send connection test message
            await this.sendMessage({ action: 'connection_test', version: this.version });
            console.log('Background connection established successfully');
            
        } catch (error) {
            console.error('Failed to establish background connection:', error);
            throw error;
        }
    }

    async sendMessage(message) {
        if (!this.backgroundPort) {
            throw new Error('No background connection');
        }

        return new Promise((resolve, reject) => {
            try {
                this.backgroundPort.postMessage(message);
                
                // Set up response handler
                const responseHandler = (response) => {
                    if (response && response.success !== undefined) {
                        this.backgroundPort.onMessage.removeListener(responseHandler);
                        resolve(response);
                    }
                };
                
                this.backgroundPort.onMessage.addListener(responseHandler);
                
                // Timeout after 5 seconds
                setTimeout(() => {
                    this.backgroundPort.onMessage.removeListener(responseHandler);
                    reject(new Error('Message timeout'));
                }, 5000);
                
            } catch (error) {
                reject(error);
            }
        });
    }

    handleBackgroundMessage(message) {
        switch (message.action) {
            case 'connection_test_response':
                console.log('Connection test successful');
                break;
            case 'refresh_requested':
                this.refreshData();
                break;
            case 'settings_updated':
                this.updateSettings(message.settings);
                break;
            default:
                console.log('Unknown message received:', message);
        }
    }

    handleConnectionError() {
        console.warn('Connection error detected, attempting recovery...');
        
        if (this.connectionRetries < this.maxRetries) {
            this.connectionRetries++;
            console.log(`Retry attempt ${this.connectionRetries}/${this.maxRetries}`);
            
            setTimeout(() => {
                this.attemptReconnection();
            }, this.retryDelay * this.connectionRetries);
        } else {
            console.error('Max retry attempts reached, falling back to local mode');
            this.fallbackToLocalMode();
        }
    }

    async attemptReconnection() {
        try {
            await this.establishConnection();
            this.connectionRetries = 0;
            console.log('Reconnection successful');
        } catch (error) {
            console.error('Reconnection failed:', error);
            this.handleConnectionError();
        }
    }

    fallbackToLocalMode() {
        console.log('Switching to local mode - data will be stored locally only');
        this.updateStatus('Local Mode (No Background)');
        
        // Store data in localStorage as fallback
        this.saveToLocalStorage();
    }

    setupPeriodicConnectionCheck() {
        // Check connection every 30 seconds
        setInterval(() => {
            if (this.backgroundPort && this.backgroundPort.disconnected) {
                console.log('Periodic check: connection lost, attempting recovery');
                this.handleConnectionError();
            }
        }, 30000);
    }

    setupMutationObserver() {
        // Watch for DOM changes to detect new transactions
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    this.checkForNewTransactions();
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    injectTrackingUI() {
        // Remove existing overlay if present
        const existing = document.getElementById('affiliate-tracker-overlay-v3');
        if (existing) existing.remove();

        // Create tracking overlay
        const overlay = document.createElement('div');
        overlay.id = 'affiliate-tracker-overlay-v3';
        overlay.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
            min-width: 250px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;

        overlay.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong style="color: #4CAF50;">🔄 Chainflip Tracker v${this.version}</strong>
            </div>
            <div style="margin-bottom: 8px;">Status: <span id="tracker-status-v3" style="color: #4CAF50;">Active</span></div>
            <div style="margin-bottom: 8px;">Transactions: <span id="tx-count-v3">0</span></div>
            <div style="margin-bottom: 8px;">Volume: <span id="total-volume-v3">$0</span></div>
            <div style="margin-bottom: 8px;">Connection: <span id="connection-status-v3" style="color: #4CAF50;">Connected</span></div>
            <div style="display: flex; gap: 5px; margin-top: 10px;">
                <button id="export-data-v3" style="flex: 1; padding: 5px 8px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Export</button>
                <button id="refresh-data-v3" style="flex: 1; padding: 5px 8px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">Refresh</button>
                <button id="clear-data-v3" style="flex: 1; padding: 5px 8px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear</button>
            </div>
        `;

        document.body.appendChild(overlay);

        // Add event listeners
        document.getElementById('export-data-v3').addEventListener('click', () => {
            this.exportTransactionData();
        });

        document.getElementById('refresh-data-v3').addEventListener('click', () => {
            this.refreshData();
        });

        document.getElementById('clear-data-v3').addEventListener('click', () => {
            this.clearData();
        });
    }

    startTracking() {
        this.isTracking = true;
        this.updateStatus('Active');
        
        // Start monitoring for transaction data
        setInterval(() => {
            this.scanForTransactions();
        }, 3000); // Check every 3 seconds

        console.log('Transaction tracking started');
    }

    checkForNewTransactions() {
        // Look for transaction elements or data
        const txElements = document.querySelectorAll('[data-transaction], [data-hash], .transaction, .tx, [class*="transaction"], [class*="tx"]');
        
        txElements.forEach(element => {
            const txHash = this.extractTransactionHash(element);
            if (txHash && !this.transactions.find(tx => tx.hash === txHash)) {
                this.processNewTransaction(txHash, element);
            }
        });
    }

    scanForTransactions() {
        // Enhanced scanning methods
        this.scanTransactionTables();
        this.scanTransactionLists();
        this.scanNetworkRequests();
        this.scanCustomElements();
    }

    scanTransactionTables() {
        // Look for transaction tables with improved selectors
        const tables = document.querySelectorAll('table, [role="table"], .table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tr, [role="row"], .row');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td, [role="cell"], .cell');
                if (cells.length > 0) {
                    this.extractTransactionFromRow(cells);
                }
            });
        });
    }

    scanTransactionLists() {
        // Look for transaction list elements with broader selectors
        const lists = document.querySelectorAll('.transaction-list, .tx-list, [class*="transaction"], [class*="tx"], [data-testid*="transaction"], [data-testid*="tx"]');
        lists.forEach(list => {
            const items = list.querySelectorAll('li, .item, .entry, [role="listitem"]');
            items.forEach(item => {
                this.extractTransactionFromItem(item);
            });
        });
    }

    scanCustomElements() {
        // Look for custom transaction elements
        const customElements = document.querySelectorAll('[data-hash], [data-transaction-id], [data-tx-hash]');
        customElements.forEach(element => {
            const hash = element.getAttribute('data-hash') || 
                        element.getAttribute('data-transaction-id') || 
                        element.getAttribute('data-tx-hash');
            
            if (hash && hash.match(/^0x[a-fA-F0-9]{64}$/)) {
                if (!this.transactions.find(tx => tx.hash === hash)) {
                    this.processNewTransaction(hash, element);
                }
            }
        });
    }

    scanNetworkRequests() {
        // Monitor network requests for transaction data
        // This would require additional permissions and setup
    }

    extractTransactionFromRow(cells) {
        // Extract transaction data from table row with improved parsing
        let txData = {};
        
        cells.forEach((cell, index) => {
            const text = cell.textContent.trim();
            
            // Look for transaction hash
            if (text.match(/^0x[a-fA-F0-9]{64}$/)) {
                txData.hash = text;
            }
            
            // Look for amounts with various formats
            if (text.match(/^\d+\.?\d*\s*[A-Z]{2,6}$/)) {
                txData.amount = text;
            }
            
            // Look for addresses
            if (text.match(/^0x[a-fA-F0-9]{40}$/)) {
                if (!txData.from) txData.from = text;
                else if (!txData.to) txData.to = text;
            }
            
            // Look for status indicators
            if (text.match(/^(Success|Confirmed|Pending|Failed|Processing)$/i)) {
                txData.status = text;
            }
        });

        if (txData.hash && !this.transactions.find(tx => tx.hash === txData.hash)) {
            this.processNewTransaction(txData.hash, null, txData);
        }
    }

    extractTransactionFromItem(item) {
        // Extract transaction data from list item with improved parsing
        const text = item.textContent;
        const hashMatch = text.match(/0x[a-fA-F0-9]{64}/);
        
        if (hashMatch) {
            const hash = hashMatch[0];
            if (!this.transactions.find(tx => tx.hash === hash)) {
                this.processNewTransaction(hash, item);
            }
        }
    }

    extractTransactionHash(element) {
        // Try multiple ways to extract transaction hash with improved selectors
        const hashSelectors = [
            '[data-hash]',
            '[data-transaction]',
            '[data-tx]',
            '[data-transaction-id]',
            '[data-tx-hash]',
            '.hash',
            '.tx-hash',
            '.transaction-hash'
        ];

        for (const selector of hashSelectors) {
            const hashElement = element.querySelector(selector);
            if (hashElement) {
                const hash = hashElement.textContent.trim();
                if (hash.match(/^0x[a-fA-F0-9]{64}$/)) {
                    return hash;
                }
            }
        }

        // Try to extract from text content
        const text = element.textContent;
        const hashMatch = text.match(/0x[a-fA-F0-9]{64}/);
        return hashMatch ? hashMatch[0] : null;
    }

    processNewTransaction(hash, element, additionalData = {}) {
        console.log(`New transaction detected: ${hash}`);
        
        const transaction = {
            hash: hash,
            timestamp: Date.now(),
            url: window.location.href,
            protocol: 'Chainflip',
            pageTitle: document.title,
            ...additionalData
        };

        // Extract additional data from element if available
        if (element) {
            this.extractTransactionDetails(transaction, element);
        }

        this.transactions.push(transaction);
        this.updateUI();
        this.saveData();
        
        // Check if this is an affiliate transaction
        this.checkAffiliateInvolvement(transaction);
        
        // Notify background script if connected
        if (this.backgroundPort) {
            this.sendMessage({
                action: 'new_transaction',
                transaction: transaction
            }).catch(error => {
                console.warn('Failed to notify background script:', error);
            });
        }
    }

    extractTransactionDetails(transaction, element) {
        // Extract amount, tokens, addresses from the element with improved parsing
        const text = element.textContent;
        
        // Look for amount patterns with various formats
        const amountMatch = text.match(/(\d+\.?\d*)\s*([A-Z]{2,6})/);
        if (amountMatch) {
            transaction.amount = amountMatch[1];
            transaction.token = amountMatch[2];
        }
        
        // Look for address patterns
        const addressMatches = text.match(/0x[a-fA-F0-9]{40}/g);
        if (addressMatches) {
            if (addressMatches.length >= 2) {
                transaction.from = addressMatches[0];
                transaction.to = addressMatches[1];
            }
        }
        
        // Look for status with improved matching
        if (text.match(/Success|Confirmed/i)) {
            transaction.status = 'Confirmed';
        } else if (text.match(/Pending|Processing/i)) {
            transaction.status = 'Pending';
        } else if (text.match(/Failed|Error/i)) {
            transaction.status = 'Failed';
        }
        
        // Look for additional metadata
        const metadataMatch = text.match(/Block\s*#?\s*(\d+)/i);
        if (metadataMatch) {
            transaction.blockNumber = metadataMatch[1];
        }
    }

    checkAffiliateInvolvement(transaction) {
        // Check if ShapeShift affiliate address is involved
        if (transaction.from === this.affiliateAddress || 
            transaction.to === this.affiliateAddress) {
            transaction.isAffiliate = true;
            console.log(`Affiliate transaction detected: ${transaction.hash}`);
            this.notifyAffiliateTransaction(transaction);
        }
    }

    notifyAffiliateTransaction(transaction) {
        // Create notification for affiliate transaction
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 25px;
            border-radius: 15px;
            z-index: 10001;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            text-align: center;
            min-width: 300px;
        `;
        
        notification.innerHTML = `
            <h3 style="margin: 0 0 15px 0; font-size: 20px;">🎉 Affiliate Transaction Detected!</h3>
            <p style="margin: 8px 0; font-size: 14px;"><strong>Hash:</strong> ${transaction.hash}</p>
            <p style="margin: 8px 0; font-size: 14px;"><strong>Amount:</strong> ${transaction.amount || 'N/A'} ${transaction.token || ''}</p>
            <p style="margin: 8px 0; font-size: 14px;"><strong>Status:</strong> ${transaction.status || 'Unknown'}</p>
            <button onclick="this.parentElement.remove()" style="padding: 10px 20px; margin-top: 15px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; cursor: pointer; font-size: 14px;">Close</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 15 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 15000);
    }

    updateUI() {
        const txCount = document.getElementById('tx-count-v3');
        const totalVolume = document.getElementById('total-volume-v3');
        const connectionStatus = document.getElementById('connection-status-v3');
        
        if (txCount) txCount.textContent = this.transactions.length;
        
        // Calculate total volume
        let total = 0;
        this.transactions.forEach(tx => {
            if (tx.amount && !isNaN(parseFloat(tx.amount))) {
                total += parseFloat(tx.amount);
            }
        });
        
        if (totalVolume) totalVolume.textContent = `$${total.toFixed(2)}`;
        
        // Update connection status
        if (connectionStatus) {
            if (this.backgroundPort && !this.backgroundPort.disconnected) {
                connectionStatus.textContent = 'Connected';
                connectionStatus.style.color = '#4CAF50';
            } else {
                connectionStatus.textContent = 'Disconnected';
                connectionStatus.style.color = '#f44336';
            }
        }
    }

    updateStatus(status) {
        const statusElement = document.getElementById('tracker-status-v3');
        if (statusElement) {
            statusElement.textContent = status;
            if (status === 'Active') {
                statusElement.style.color = '#4CAF50';
            } else if (status.includes('Local')) {
                statusElement.style.color = '#ff9800';
            } else {
                statusElement.style.color = '#f44336';
            }
        }
    }

    async saveData() {
        try {
            // Try to save to background script first
            if (this.backgroundPort && !this.backgroundPort.disconnected) {
                await this.sendMessage({
                    action: 'save_transactions',
                    transactions: this.transactions
                });
            }
        } catch (error) {
            console.warn('Failed to save to background script, using local storage:', error);
            this.saveToLocalStorage();
        }
    }

    saveToLocalStorage() {
        try {
            localStorage.setItem('chainflip_transactions_v3', JSON.stringify(this.transactions));
            localStorage.setItem('chainflip_last_updated_v3', Date.now().toString());
            console.log('Data saved to local storage');
        } catch (error) {
            console.error('Failed to save to local storage:', error);
        }
    }

    loadFromLocalStorage() {
        try {
            const stored = localStorage.getItem('chainflip_transactions_v3');
            if (stored) {
                this.transactions = JSON.parse(stored);
                console.log(`Loaded ${this.transactions.length} transactions from local storage`);
                this.updateUI();
            }
        } catch (error) {
            console.error('Failed to load from local storage:', error);
        }
    }

    exportTransactionData() {
        const dataStr = JSON.stringify(this.transactions, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `chainflip_transactions_v${this.version}_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    refreshData() {
        console.log('Refreshing transaction data...');
        this.scanForTransactions();
        this.loadFromLocalStorage();
        this.updateUI();
    }

    clearData() {
        if (confirm('Are you sure you want to clear all transaction data? This action cannot be undone.')) {
            this.transactions = [];
            this.updateUI();
            this.saveData();
            localStorage.removeItem('chainflip_transactions_v3');
            localStorage.removeItem('chainflip_last_updated_v3');
            console.log('All transaction data cleared');
        }
    }
}

// Initialize the tracker when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ChainflipAffiliateTrackerV3();
    });
} else {
    new ChainflipAffiliateTrackerV3();
}

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('Page became visible, refreshing data...');
        // Refresh data when page becomes visible
        if (window.chainflipAffiliateTrackerV3) {
            window.chainflipAffiliateTrackerV3.refreshData();
        }
    }
});

// Make tracker globally accessible for debugging
window.chainflipAffiliateTrackerV3 = null;
document.addEventListener('DOMContentLoaded', () => {
    window.chainflipAffiliateTrackerV3 = new ChainflipAffiliateTrackerV3();
});


