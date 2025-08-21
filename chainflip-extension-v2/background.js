// Chainflip Affiliate Tracker v2 - Background Service Worker
// Handles background tasks and data management

console.log('Chainflip Affiliate Tracker v2 Background Service Worker loaded');

// Extension installation
chrome.runtime.onInstalled.addListener((details) => {
    console.log('Extension installed:', details.reason);
    
    if (details.reason === 'install') {
        // Initialize storage with default values
        chrome.storage.local.set({
            'chainflip_transactions': [],
            'last_updated': Date.now(),
            'version': '2.0.0',
            'settings': {
                'auto_track': true,
                'notifications': true,
                'export_format': 'json'
            }
        });
    }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background received message:', request);
    
    switch (request.action) {
        case 'get_transactions':
            chrome.storage.local.get(['chainflip_transactions'], (result) => {
                sendResponse({ transactions: result.chainflip_transactions || [] });
            });
            return true; // Keep message channel open for async response
            
        case 'save_transaction':
            chrome.storage.local.get(['chainflip_transactions'], (result) => {
                const transactions = result.chainflip_transactions || [];
                transactions.push(request.transaction);
                
                chrome.storage.local.set({
                    'chainflip_transactions': transactions,
                    'last_updated': Date.now()
                });
                
                sendResponse({ success: true, count: transactions.length });
            });
            return true;
            
        case 'export_data':
            exportTransactionData(request.format || 'json');
            sendResponse({ success: true });
            break;
            
        case 'clear_data':
            chrome.storage.local.set({
                'chainflip_transactions': [],
                'last_updated': Date.now()
            });
            sendResponse({ success: true });
            break;
            
        default:
            sendResponse({ error: 'Unknown action' });
    }
});

// Handle tab updates to inject content script if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('app.chainflip.io')) {
        console.log('Chainflip tab updated, ensuring content script is active');
        
        // Check if content script is already injected
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: () => {
                return window.chainflipAffiliateTracker !== undefined;
            }
        }).then((results) => {
            if (results && results[0] && !results[0].result) {
                console.log('Injecting content script into Chainflip tab');
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content.js']
                });
            }
        });
    }
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    if (tab.url && tab.url.includes('app.chainflip.io')) {
        // Open popup or perform action
        console.log('Extension icon clicked on Chainflip tab');
        
        // You could open a popup here or perform other actions
        chrome.tabs.sendMessage(tab.id, { action: 'show_popup' });
    } else {
        // Open Chainflip in new tab
        chrome.tabs.create({ url: 'https://app.chainflip.io' });
    }
});

// Export transaction data
function exportTransactionData(format = 'json') {
    chrome.storage.local.get(['chainflip_transactions'], (result) => {
        const transactions = result.chainflip_transactions || [];
        
        if (format === 'csv') {
            exportAsCSV(transactions);
        } else {
            exportAsJSON(transactions);
        }
    });
}

function exportAsJSON(transactions) {
    const dataStr = JSON.stringify(transactions, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const url = URL.createObjectURL(dataBlob);
    chrome.downloads.download({
        url: url,
        filename: `chainflip_transactions_v2_${new Date().toISOString().split('T')[0]}.json`,
        saveAs: true
    });
}

function exportAsCSV(transactions) {
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
        filename: `chainflip_transactions_v2_${new Date().toISOString().split('T')[0]}.csv`,
        saveAs: true
    });
}

// Periodic data cleanup (remove old transactions)
setInterval(() => {
    chrome.storage.local.get(['chainflip_transactions'], (result) => {
        const transactions = result.chainflip_transactions || [];
        const now = Date.now();
        const oneWeekAgo = now - (7 * 24 * 60 * 60 * 1000); // 7 days
        
        const filteredTransactions = transactions.filter(tx => {
            return tx.timestamp && tx.timestamp > oneWeekAgo;
        });
        
        if (filteredTransactions.length !== transactions.length) {
            chrome.storage.local.set({
                'chainflip_transactions': filteredTransactions,
                'last_updated': now
            });
            console.log(`Cleaned up ${transactions.length - filteredTransactions.length} old transactions`);
        }
    });
}, 24 * 60 * 60 * 1000); // Run once per day


