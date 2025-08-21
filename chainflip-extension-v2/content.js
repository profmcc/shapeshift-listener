// Chainflip Affiliate Tracker v2 - Content Script
// Tracks ShapeShift affiliate transactions on Chainflip protocol

console.log('Chainflip Affiliate Tracker v2 loaded');

class ChainflipAffiliateTracker {
    constructor() {
        this.version = '2.0.0';
        this.affiliateAddress = '0x0000000000000000000000000000000000000000'; // Replace with actual ShapeShift address
        this.transactions = [];
        this.isTracking = false;
        this.init();
    }

    init() {
        console.log(`Initializing Chainflip Affiliate Tracker v${this.version}`);
        this.setupMutationObserver();
        this.injectTrackingUI();
        this.startTracking();
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
        // Create tracking overlay
        const overlay = document.createElement('div');
        overlay.id = 'affiliate-tracker-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            z-index: 10000;
            font-family: monospace;
            font-size: 12px;
            min-width: 200px;
        `;

        overlay.innerHTML = `
            <div><strong>Chainflip Tracker v${this.version}</strong></div>
            <div>Status: <span id="tracker-status">Active</span></div>
            <div>Transactions: <span id="tx-count">0</span></div>
            <div>Volume: <span id="total-volume">$0</span></div>
            <button id="export-data" style="margin-top: 5px; padding: 2px 5px;">Export Data</button>
        `;

        document.body.appendChild(overlay);

        // Add export functionality
        document.getElementById('export-data').addEventListener('click', () => {
            this.exportTransactionData();
        });
    }

    startTracking() {
        this.isTracking = true;
        this.updateStatus('Active');
        
        // Start monitoring for transaction data
        setInterval(() => {
            this.scanForTransactions();
        }, 5000); // Check every 5 seconds

        console.log('Transaction tracking started');
    }

    checkForNewTransactions() {
        // Look for transaction elements or data
        const txElements = document.querySelectorAll('[data-transaction], [data-hash], .transaction, .tx');
        
        txElements.forEach(element => {
            const txHash = this.extractTransactionHash(element);
            if (txHash && !this.transactions.find(tx => tx.hash === txHash)) {
                this.processNewTransaction(txHash, element);
            }
        });
    }

    scanForTransactions() {
        // Scan the page for any transaction-related data
        this.scanTransactionTables();
        this.scanTransactionLists();
        this.scanNetworkRequests();
    }

    scanTransactionTables() {
        // Look for transaction tables
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length > 0) {
                    this.extractTransactionFromRow(cells);
                }
            });
        });
    }

    scanTransactionLists() {
        // Look for transaction list elements
        const lists = document.querySelectorAll('.transaction-list, .tx-list, [class*="transaction"], [class*="tx"]');
        lists.forEach(list => {
            const items = list.querySelectorAll('li, .item, .entry');
            items.forEach(item => {
                this.extractTransactionFromItem(item);
            });
        });
    }

    scanNetworkRequests() {
        // Monitor network requests for transaction data
        // This would require additional permissions and setup
    }

    extractTransactionFromRow(cells) {
        // Extract transaction data from table row
        let txData = {};
        
        cells.forEach((cell, index) => {
            const text = cell.textContent.trim();
            
            // Look for transaction hash
            if (text.match(/^0x[a-fA-F0-9]{64}$/)) {
                txData.hash = text;
            }
            
            // Look for amounts
            if (text.match(/^\d+\.?\d*\s*[A-Z]{3,4}$/)) {
                txData.amount = text;
            }
            
            // Look for addresses
            if (text.match(/^0x[a-fA-F0-9]{40}$/)) {
                if (!txData.from) txData.from = text;
                else if (!txData.to) txData.to = text;
            }
        });

        if (txData.hash && !this.transactions.find(tx => tx.hash === txData.hash)) {
            this.processNewTransaction(txData.hash, null, txData);
        }
    }

    extractTransactionFromItem(item) {
        // Extract transaction data from list item
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
        // Try multiple ways to extract transaction hash
        const hashSelectors = [
            '[data-hash]',
            '[data-transaction]',
            '[data-tx]',
            '.hash',
            '.tx-hash'
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
            ...additionalData
        };

        // Extract additional data from element if available
        if (element) {
            this.extractTransactionDetails(transaction, element);
        }

        this.transactions.push(transaction);
        this.updateUI();
        this.saveToStorage();
        
        // Check if this is an affiliate transaction
        this.checkAffiliateInvolvement(transaction);
    }

    extractTransactionDetails(transaction, element) {
        // Extract amount, tokens, addresses from the element
        const text = element.textContent;
        
        // Look for amount patterns
        const amountMatch = text.match(/(\d+\.?\d*)\s*([A-Z]{3,4})/);
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
        
        // Look for status
        if (text.includes('Success') || text.includes('Confirmed')) {
            transaction.status = 'Confirmed';
        } else if (text.includes('Pending')) {
            transaction.status = 'Pending';
        } else if (text.includes('Failed')) {
            transaction.status = 'Failed';
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
            background: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 10px;
            z-index: 10001;
            font-family: Arial, sans-serif;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        `;
        
        notification.innerHTML = `
            <h3>🎉 Affiliate Transaction Detected!</h3>
            <p>Hash: ${transaction.hash}</p>
            <p>Amount: ${transaction.amount || 'N/A'} ${transaction.token || ''}</p>
            <button onclick="this.parentElement.remove()" style="padding: 5px 10px; margin-top: 10px;">Close</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }

    updateUI() {
        const txCount = document.getElementById('tx-count');
        const totalVolume = document.getElementById('total-volume');
        
        if (txCount) txCount.textContent = this.transactions.length;
        
        // Calculate total volume
        let total = 0;
        this.transactions.forEach(tx => {
            if (tx.amount && !isNaN(parseFloat(tx.amount))) {
                total += parseFloat(tx.amount);
            }
        });
        
        if (totalVolume) totalVolume.textContent = `$${total.toFixed(2)}`;
    }

    updateStatus(status) {
        const statusElement = document.getElementById('tracker-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.style.color = status === 'Active' ? '#4CAF50' : '#f44336';
        }
    }

    saveToStorage() {
        chrome.storage.local.set({
            'chainflip_transactions': this.transactions,
            'last_updated': Date.now()
        });
    }

    exportTransactionData() {
        const dataStr = JSON.stringify(this.transactions, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `chainflip_transactions_v${this.version}_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }
}

// Initialize the tracker when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ChainflipAffiliateTracker();
    });
} else {
    new ChainflipAffiliateTracker();
}


