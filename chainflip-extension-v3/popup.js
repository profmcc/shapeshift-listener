// Chainflip Affiliate Tracker v3 - Popup Script
// Handles popup UI interactions and data display with improved connection handling

console.log('Chainflip Affiliate Tracker v3 Popup loaded');

class PopupManagerV3 {
    constructor() {
        this.transactions = [];
        this.lastUpdated = null;
        this.version = '3.0.0';
        this.connectionStatus = 'unknown';
        this.init();
    }

    init() {
        this.loadData();
        this.setupEventListeners();
        this.updateUI();
        this.checkConnectionStatus();
        
        // Set up periodic refresh
        setInterval(() => {
            this.refreshData();
        }, 10000); // Refresh every 10 seconds
    }

    setupEventListeners() {
        // Export buttons
        document.getElementById('export-json').addEventListener('click', () => {
            this.exportData('json');
        });

        document.getElementById('export-csv').addEventListener('click', () => {
            this.exportData('csv');
        });

        // Refresh button
        document.getElementById('refresh-data').addEventListener('click', () => {
            this.refreshData();
        });

        // Clear data button
        document.getElementById('clear-data').addEventListener('click', () => {
            this.clearData();
        });
    }

    async loadData() {
        try {
            // Get data from storage
            const result = await chrome.storage.local.get([
                'chainflip_transactions_v3',
                'last_updated_v3',
                'version_v3'
            ]);

            this.transactions = result.chainflip_transactions_v3 || [];
            this.lastUpdated = result.last_updated_v3 || Date.now();
            this.version = result.version_v3 || this.version;

            console.log(`Loaded ${this.transactions.length} transactions`);
            this.updateUI();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load transaction data');
        }
    }

    async checkConnectionStatus() {
        try {
            // Try to send a test message to background script
            const response = await chrome.runtime.sendMessage({
                action: 'connection_test'
            });
            
            if (response && response.success) {
                this.connectionStatus = 'connected';
                this.updateConnectionStatus();
            } else {
                this.connectionStatus = 'disconnected';
                this.updateConnectionStatus();
            }
        } catch (error) {
            console.warn('Background script not responding:', error);
            this.connectionStatus = 'disconnected';
            this.updateConnectionStatus();
        }
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;

        // Remove existing classes
        statusElement.className = 'connection-status';
        
        switch (this.connectionStatus) {
            case 'connected':
                statusElement.textContent = 'Connection: Connected';
                statusElement.classList.add('connected');
                break;
            case 'disconnected':
                statusElement.textContent = 'Connection: Disconnected';
                statusElement.classList.add('disconnected');
                break;
            case 'local':
                statusElement.textContent = 'Connection: Local Mode';
                statusElement.classList.add('local');
                break;
            default:
                statusElement.textContent = 'Connection: Unknown';
                statusElement.classList.add('disconnected');
        }
    }

    updateUI() {
        this.updateStats();
        this.updateTransactionsList();
    }

    updateStats() {
        // Transaction count
        const txCount = document.getElementById('tx-count');
        if (txCount) {
            txCount.textContent = this.transactions.length;
        }

        // Total volume
        const totalVolume = document.getElementById('total-volume');
        if (totalVolume) {
            let total = 0;
            this.transactions.forEach(tx => {
                if (tx.amount && !isNaN(parseFloat(tx.amount))) {
                    total += parseFloat(tx.amount);
                }
            });
            totalVolume.textContent = `$${total.toFixed(2)}`;
        }

        // Affiliate transaction count
        const affiliateCount = document.getElementById('affiliate-count');
        if (affiliateCount) {
            const affiliateTxs = this.transactions.filter(tx => tx.isAffiliate);
            affiliateCount.textContent = affiliateTxs.length;
        }

        // Last updated
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated) {
            if (this.lastUpdated) {
                const date = new Date(this.lastUpdated);
                const timeAgo = this.getTimeAgo(date);
                lastUpdated.textContent = timeAgo;
            } else {
                lastUpdated.textContent = 'Never';
            }
        }
    }

    updateTransactionsList() {
        const container = document.getElementById('transactions-list');
        if (!container) return;

        if (this.transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📊</div>
                    <div class="text">No transactions found</div>
                    <div class="subtext">Navigate to Chainflip to start tracking</div>
                </div>
            `;
            return;
        }

        // Show recent transactions (last 6)
        const recentTxs = this.transactions
            .sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0))
            .slice(0, 6);

        const html = recentTxs.map(tx => this.createTransactionHTML(tx)).join('');
        container.innerHTML = html;
    }

    createTransactionHTML(tx) {
        const date = new Date(tx.timestamp || Date.now());
        const timeAgo = this.getTimeAgo(date);
        
        const affiliateBadge = tx.isAffiliate ? '<span class="affiliate-badge">AFFILIATE</span>' : '';
        
        const amountDisplay = tx.amount ? 
            `<div style="font-size: 11px; opacity: 0.7; margin-top: 3px;">${tx.amount} ${tx.token || ''}</div>` : '';
        
        const statusDisplay = tx.status ? 
            `<div style="font-size: 10px; opacity: 0.6; margin-top: 2px;">${tx.status}</div>` : '';
        
        return `
            <div class="transaction-item">
                <div class="tx-hash">${tx.hash || 'Unknown'}</div>
                <div class="tx-details">
                    <span>${timeAgo}</span>
                    <span>${affiliateBadge}</span>
                </div>
                ${amountDisplay}
                ${statusDisplay}
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

    async exportData(format) {
        try {
            if (this.transactions.length === 0) {
                this.showError('No transactions to export');
                return;
            }

            // Send message to background script to handle export
            await chrome.runtime.sendMessage({
                action: 'export_data',
                format: format
            });

            console.log(`Exporting data as ${format.toUpperCase()}`);
            this.showSuccess(`Data exported as ${format.toUpperCase()}`);
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export data. Check if background script is running.');
        }
    }

    async refreshData() {
        try {
            // Try to get fresh data from background script
            await this.loadData();
            
            // Check connection status
            await this.checkConnectionStatus();
            
            // Try to get fresh data from active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab && tab.url && this.isChainflipUrl(tab.url)) {
                // Request fresh data from content script
                try {
                    await chrome.tabs.sendMessage(tab.id, { action: 'refresh_data' });
                    console.log('Requested data refresh from content script');
                } catch (error) {
                    console.warn('Content script not responding:', error);
                }
            }
            
            this.showSuccess('Data refreshed successfully');
        } catch (error) {
            console.error('Refresh error:', error);
            this.showError('Failed to refresh data');
        }
    }

    async clearData() {
        try {
            // Confirm action
            if (!confirm('Are you sure you want to clear all transaction data? This action cannot be undone.')) {
                return;
            }

            // Send message to background script
            await chrome.runtime.sendMessage({ action: 'clear_data' });
            
            // Clear local data
            this.transactions = [];
            this.lastUpdated = null;
            
            // Update UI
            this.updateUI();
            
            this.showSuccess('All data cleared successfully');
        } catch (error) {
            console.error('Clear data error:', error);
            this.showError('Failed to clear data. Check if background script is running.');
        }
    }

    isChainflipUrl(url) {
        return url.includes('app.chainflip.io') || 
               url.includes('chainflip.io') ||
               url.includes('broker.chainflip.io');
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showMessage(message, type) {
        // Remove existing message
        const existing = document.querySelector('.message');
        if (existing) existing.remove();

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Insert after header
        const header = document.querySelector('.header');
        if (header && header.nextSibling) {
            header.parentNode.insertBefore(messageDiv, header.nextSibling);
        } else {
            document.body.insertBefore(messageDiv, document.body.firstChild);
        }

        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.remove();
            }
        }, 4000);
    }

    // Debug method to show connection info
    showDebugInfo() {
        console.log('=== Debug Info ===');
        console.log('Transactions:', this.transactions.length);
        console.log('Connection Status:', this.connectionStatus);
        console.log('Last Updated:', this.lastUpdated);
        console.log('Version:', this.version);
        console.log('==================');
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.popupManagerV3 = new PopupManagerV3();
    
    // Add debug info to console
    console.log('Popup initialized. Use window.popupManagerV3.showDebugInfo() for debug info.');
});

// Listen for messages from content script or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Popup received message:', request);
    
    if (request.action === 'update_data') {
        // Refresh data when notified
        window.popupManagerV3?.loadData();
    }
    
    sendResponse({ received: true });
});

// Handle runtime errors
chrome.runtime.onError.addListener((error) => {
    console.error('Runtime error:', error);
    if (window.popupManagerV3) {
        window.popupManagerV3.showError(`Runtime error: ${error.message}`);
    }
});

// Handle extension updates
chrome.runtime.onUpdateAvailable.addListener(() => {
    console.log('Extension update available');
    if (window.popupManagerV3) {
        window.popupManagerV3.showSuccess('Extension update available. Please refresh the page.');
    }
});

// Handle extension restart
chrome.runtime.onRestartRequired.addListener(() => {
    console.log('Extension restart required');
    if (window.popupManagerV3) {
        window.popupManagerV3.showError('Extension restart required. Please reload the extension.');
    }
});


