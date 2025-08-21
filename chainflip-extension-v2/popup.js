// Chainflip Affiliate Tracker v2 - Popup Script
// Handles popup UI interactions and data display

console.log('Chainflip Affiliate Tracker v2 Popup loaded');

class PopupManager {
    constructor() {
        this.transactions = [];
        this.init();
    }

    init() {
        this.loadData();
        this.setupEventListeners();
        this.updateUI();
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
                'chainflip_transactions',
                'last_updated',
                'version'
            ]);

            this.transactions = result.chainflip_transactions || [];
            this.lastUpdated = result.last_updated || Date.now();
            this.version = result.version || '2.0.0';

            console.log(`Loaded ${this.transactions.length} transactions`);
            this.updateUI();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load transaction data');
        }
    }

    updateUI() {
        this.updateStats();
        this.updateTransactionsList();
        this.updateStatus();
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
            container.innerHTML = '<div class="loading">No transactions found</div>';
            return;
        }

        // Show recent transactions (last 5)
        const recentTxs = this.transactions
            .sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0))
            .slice(0, 5);

        const html = recentTxs.map(tx => this.createTransactionHTML(tx)).join('');
        container.innerHTML = html;
    }

    createTransactionHTML(tx) {
        const date = new Date(tx.timestamp || Date.now());
        const timeAgo = this.getTimeAgo(date);
        
        const affiliateBadge = tx.isAffiliate ? '<span class="affiliate-badge">AFFILIATE</span>' : '';
        
        return `
            <div class="transaction-item">
                <div class="tx-hash">${tx.hash || 'Unknown'}</div>
                <div class="tx-details">
                    <span>${timeAgo}</span>
                    <span>${affiliateBadge}</span>
                </div>
                ${tx.amount ? `<div style="font-size: 11px; opacity: 0.7;">${tx.amount} ${tx.token || ''}</div>` : ''}
            </div>
        `;
    }

    updateStatus() {
        const statusElement = document.getElementById('status');
        if (!statusElement) return;

        if (this.transactions.length > 0) {
            statusElement.className = 'status active';
            statusElement.textContent = `Status: Active (${this.transactions.length} transactions tracked)`;
        } else {
            statusElement.className = 'status inactive';
            statusElement.textContent = 'Status: No transactions found';
        }
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
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export data');
        }
    }

    async refreshData() {
        try {
            // Try to get fresh data from active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab && tab.url && tab.url.includes('app.chainflip.io')) {
                // Request fresh data from content script
                await chrome.tabs.sendMessage(tab.id, { action: 'refresh_data' });
                console.log('Requested data refresh from content script');
            }

            // Reload local data
            await this.loadData();
            
            // Show success message
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
            this.showError('Failed to clear data');
        }
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
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            background: ${type === 'error' ? 'rgba(244, 67, 54, 0.9)' : 'rgba(76, 175, 80, 0.9)'};
            color: white;
        `;

        document.body.appendChild(messageDiv);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.remove();
            }
        }, 3000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PopupManager();
});

// Listen for messages from content script or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Popup received message:', request);
    
    if (request.action === 'update_data') {
        // Refresh data when notified
        window.popupManager?.loadData();
    }
    
    sendResponse({ received: true });
});


