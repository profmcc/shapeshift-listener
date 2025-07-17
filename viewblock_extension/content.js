// Content script for ViewBlock Data Capture extension

let capturedData = [];
let floatingUI = null;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };

// Global state for auto-paging
let autoPagingState = {
    isActive: false,
    currentPage: 1,
    maxPages: 10,
    delay: 2000,
    capturedTransactions: [],
    nextPageButton: null,
    stopRequested: false
};

// Function to save state to Chrome storage
function saveAutoPagingState() {
    if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.set({
            autoPagingState: {
                isActive: autoPagingState.isActive,
                currentPage: autoPagingState.currentPage,
                maxPages: autoPagingState.maxPages,
                delay: autoPagingState.delay,
                capturedTransactions: autoPagingState.capturedTransactions,
                stopRequested: autoPagingState.stopRequested
            }
        });
    }
}

// Function to load state from Chrome storage
function loadAutoPagingState() {
    if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.get(['autoPagingState'], function(result) {
            if (result.autoPagingState) {
                const saved = result.autoPagingState;
                autoPagingState.isActive = saved.isActive || false;
                autoPagingState.currentPage = saved.currentPage || getCurrentPageFromUrl();
                autoPagingState.maxPages = saved.maxPages || 10;
                autoPagingState.delay = saved.delay || 2000;
                autoPagingState.capturedTransactions = saved.capturedTransactions || [];
                autoPagingState.stopRequested = saved.stopRequested || false;
                
                console.log('Loaded auto-paging state:', autoPagingState);
                
                // If auto-paging was active and not stopped, continue
                if (autoPagingState.isActive && !autoPagingState.stopRequested) {
                    console.log('Resuming auto-paging from page', autoPagingState.currentPage);
                    // Wait a moment for page to fully load, then capture and continue
                    setTimeout(() => {
                        continueAutoPaging();
                    }, 1000);
                }
            }
        });
    }
}

// Function to continue auto-paging (used both for initial start and resume)
async function continueAutoPaging() {
    while (autoPagingState.isActive && !autoPagingState.stopRequested && autoPagingState.currentPage <= autoPagingState.maxPages) {
        console.log(`Processing page ${autoPagingState.currentPage}/${autoPagingState.maxPages}`);
        
        // Wait a moment for page to fully load
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Capture current page data
        const pageData = captureCurrentPageData();
        if (pageData.length > 0) {
            autoPagingState.capturedTransactions.push(...pageData);
            console.log(`Captured ${pageData.length} transactions from page ${autoPagingState.currentPage}`);
            console.log(`Total captured so far: ${autoPagingState.capturedTransactions.length}`);
        }
        
        // Save state after each page
        saveAutoPagingState();
        updateFloatingUI();
        
        // Wait additional time to ensure data is fully captured
        await new Promise(resolve => setTimeout(resolve, Math.max(autoPagingState.delay, 3000)));
        
        // Check if we should continue to next page
        if (autoPagingState.currentPage >= autoPagingState.maxPages) {
            console.log('Reached maximum pages');
            break;
        }
        
        // Navigate to next page
        console.log(`Navigating to page ${autoPagingState.currentPage + 1}...`);
        autoPagingState.currentPage++;
        saveAutoPagingState();
        
        const success = await navigateToNextPage();
        if (!success) {
            console.log('Failed to navigate to next page');
            break;
        }
        
        // The page will reload and this function will be called again from loadAutoPagingState
        return;
    }
    
    // Auto-paging completed
    autoPagingState.isActive = false;
    saveAutoPagingState();
    updateFloatingUI();
    console.log(`Auto-paging completed! Total transactions captured: ${autoPagingState.capturedTransactions.length}`);
    
    // Show completion message
    if (autoPagingState.capturedTransactions.length > 0) {
        alert(`Auto-capture completed! Captured ${autoPagingState.capturedTransactions.length} transactions. Click "Download Data" to save.`);
    }
}

// Function to navigate to next page
async function navigateToNextPage() {
    // First try to click next button
    if (findAndClickNextPage()) {
        return true;
    }
    
    // Fallback to URL manipulation
    const currentUrl = window.location.href;
    let nextPageUrl;
    
    if (currentUrl.includes('page=')) {
        nextPageUrl = currentUrl.replace(/page=\d+/, `page=${autoPagingState.currentPage}`);
    } else {
        const separator = currentUrl.includes('?') ? '&' : '?';
        nextPageUrl = `${currentUrl}${separator}page=${autoPagingState.currentPage}`;
    }
    
    console.log(`Navigating to: ${nextPageUrl}`);
    window.location.href = nextPageUrl;
    return true;
}

// Function to capture current page data
function captureCurrentPageData() {
    console.log('Capturing current page data...');
    try {
        const data = extractTableData();
        console.log(`Captured ${data.length} transactions from current page`);
        return data;
    } catch (error) {
        console.error('Error capturing page data:', error);
        return [];
    }
}

// Enhanced auto-paging function
async function startAutoPaging() {
    if (!isViewBlockThorchainPage()) {
        alert('Please navigate to ViewBlock THORChain transactions page with affiliate=ss parameter');
        return;
    }
    
    if (autoPagingState.isActive) {
        console.log('Auto-paging already active');
        return;
    }
    
    autoPagingState.isActive = true;
    autoPagingState.stopRequested = false;
    autoPagingState.currentPage = getCurrentPageFromUrl();
    autoPagingState.capturedTransactions = [];
    
    console.log(`Starting auto-paging: max ${autoPagingState.maxPages} pages, ${autoPagingState.delay}ms delay`);
    console.log(`Starting from page ${autoPagingState.currentPage}`);
    
    saveAutoPagingState();
    
    await continueAutoPaging();
}

// Function to stop auto-paging
function stopAutoPaging() {
    autoPagingState.stopRequested = true;
    autoPagingState.isActive = false;
    console.log('Auto-paging stopped');
    
    // Clear saved state
    chrome.storage.local.remove(['autoPagingState']);
    
    updateFloatingUI();
}

// Function to find and click the next page button
function findAndClickNextPage() {
    console.log('Looking for next page button...');
    
    // Try multiple selectors for pagination buttons
    const nextPageSelectors = [
        'button[aria-label="Next page"]',
        'button[aria-label="Next"]',
        'a[aria-label="Next page"]',
        'a[aria-label="Next"]',
        '.pagination button:last-child',
        '.pagination a:last-child',
        '[data-testid="next-page"]',
        '.MuiPaginationItem-next',
        'button[data-testid="next"]',
        'a[data-testid="next"]',
        'button[title="Next"]',
        'a[title="Next"]'
    ];
    
    let nextButton = null;
    
    // First try the specific selectors
    for (const selector of nextPageSelectors) {
        try {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                if (element.textContent.toLowerCase().includes('next') || 
                    element.getAttribute('aria-label')?.toLowerCase().includes('next') ||
                    element.getAttribute('title')?.toLowerCase().includes('next')) {
                    nextButton = element;
                    break;
                }
            }
            if (nextButton) break;
        } catch (e) {
            console.log(`Selector ${selector} failed:`, e);
        }
    }
    
    // If no specific next button found, look for numbered pagination
    if (!nextButton) {
        const allButtons = document.querySelectorAll('button, a');
        for (const button of allButtons) {
            const text = button.textContent.trim();
            const ariaLabel = button.getAttribute('aria-label') || '';
            const title = button.getAttribute('title') || '';
            
            // Look for next indicators
            if (text.toLowerCase().includes('next') || 
                ariaLabel.toLowerCase().includes('next') ||
                title.toLowerCase().includes('next')) {
                nextButton = button;
                break;
            }
            
            // Look for numbered buttons (current page + 1)
            if (text === String(autoPagingState.currentPage + 1)) {
                nextButton = button;
                break;
            }
        }
    }
    
    // Also check for URL-based pagination
    if (!nextButton) {
        const currentUrl = window.location.href;
        const urlMatch = currentUrl.match(/[?&]page=(\d+)/);
        if (urlMatch) {
            const currentPage = parseInt(urlMatch[1]);
            const nextPageUrl = currentUrl.replace(/[?&]page=\d+/, `&page=${currentPage + 1}`);
            console.log(`Trying URL-based navigation to: ${nextPageUrl}`);
            window.location.href = nextPageUrl;
            return true;
        }
    }
    
    if (nextButton) {
        console.log('Found next page button:', nextButton);
        nextButton.click();
        return true;
    } else {
        console.log('No next page button found');
        return false;
    }
}

// Function to wait for page load and new data
function waitForPageLoad() {
    return new Promise((resolve) => {
        let attempts = 0;
        const maxAttempts = 30; // 30 seconds max wait
        
        const checkForNewData = () => {
            attempts++;
            console.log(`Waiting for page load... attempt ${attempts}`);
            
            // Check if table has loaded
            const table = document.querySelector('table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                if (rows.length > 0) {
                    console.log(`Page loaded with ${rows.length} rows`);
                    resolve(true);
                    return;
                }
            }
            
            if (attempts >= maxAttempts) {
                console.log('Page load timeout');
                resolve(false);
                return;
            }
            
            setTimeout(checkForNewData, 1000);
        };
        
        checkForNewData();
    });
}

// Function to get current page from URL
function getCurrentPageFromUrl() {
    const currentUrl = window.location.href;
    const urlMatch = currentUrl.match(/[?&]page=(\d+)/);
    return urlMatch ? parseInt(urlMatch[1]) : 1;
}

// Function to check if we're on the right page
function isViewBlockThorchainPage() {
    const currentUrl = window.location.href;
    return currentUrl.includes('viewblock.io/thorchain') && 
           (currentUrl.includes('affiliate=ss') || currentUrl.includes('txs'));
}

// Enhanced floating UI with better controls
function createFloatingUI() {
    // Remove existing UI if present
    const existingUI = document.getElementById('viewblock-floating-ui');
    if (existingUI) {
        existingUI.remove();
    }
    
    const floatingUI = document.createElement('div');
    floatingUI.id = 'viewblock-floating-ui';
    floatingUI.innerHTML = `
        <div id="ui-header">
            <span id="ui-title">ViewBlock Scraper</span>
            <div id="ui-controls">
                <button id="ui-minimize" title="Minimize">−</button>
                <button id="ui-close" title="Close">×</button>
            </div>
        </div>
        <div id="ui-content">
            <div id="ui-status">
                <div id="status-text">Ready</div>
                <div id="progress-info">Page: ${autoPagingState.currentPage} | Captured: ${autoPagingState.capturedTransactions.length}</div>
            </div>
            
            <div id="ui-settings">
                <div class="setting-group">
                    <label for="max-pages">Max Pages:</label>
                    <input type="number" id="max-pages" value="${autoPagingState.maxPages}" min="1" max="50">
                </div>
                <div class="setting-group">
                    <label for="page-delay">Delay (ms):</label>
                    <input type="number" id="page-delay" value="${autoPagingState.delay}" min="500" max="10000" step="100">
                </div>
            </div>
            
            <div id="ui-buttons">
                <button id="capture-current" class="action-btn primary">Capture Current Page</button>
                <button id="start-auto-paging" class="action-btn ${autoPagingState.isActive ? 'danger' : 'success'}">${autoPagingState.isActive ? 'Stop Auto-Capture' : 'Start Auto-Capture'}</button>
                <button id="download-data" class="action-btn secondary">Download Data</button>
                <button id="debug-info" class="action-btn secondary">Debug Info</button>
            </div>
        </div>
    `;
    
    // Add comprehensive styles
    const style = document.createElement('style');
    style.textContent = `
        #viewblock-floating-ui {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 320px;
            background: #ffffff;
            border: 2px solid #2196F3;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            color: #333333;
            z-index: 10000;
            user-select: none;
        }
        
        #ui-header {
            background: #2196F3;
            color: white;
            padding: 10px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
            border-radius: 6px 6px 0 0;
        }
        
        #ui-title {
            font-weight: bold;
            font-size: 16px;
        }
        
        #ui-controls button {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 0 5px;
            margin-left: 5px;
        }
        
        #ui-controls button:hover {
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
        }
        
        #ui-content {
            padding: 15px;
            background: #ffffff;
        }
        
        #ui-status {
            margin-bottom: 15px;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 4px;
            border-left: 4px solid #2196F3;
        }
        
        #status-text {
            font-weight: bold;
            color: #333333;
            margin-bottom: 5px;
        }
        
        #progress-info {
            font-size: 12px;
            color: #666666;
        }
        
        #ui-settings {
            margin-bottom: 15px;
        }
        
        .setting-group {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .setting-group label {
            flex: 1;
            color: #333333;
            font-weight: 500;
        }
        
        .setting-group input {
            flex: 1;
            padding: 5px 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            color: #333333;
            background: #ffffff;
        }
        
        .setting-group input:focus {
            outline: none;
            border-color: #2196F3;
            box-shadow: 0 0 0 2px rgba(33,150,243,0.2);
        }
        
        #ui-buttons {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .action-btn {
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .action-btn.primary {
            background: #2196F3;
            color: white;
        }
        
        .action-btn.primary:hover {
            background: #1976D2;
        }
        
        .action-btn.success {
            background: #4CAF50;
            color: white;
        }
        
        .action-btn.success:hover {
            background: #45a049;
        }
        
        .action-btn.danger {
            background: #f44336;
            color: white;
        }
        
        .action-btn.danger:hover {
            background: #da190b;
        }
        
        .action-btn.secondary {
            background: #757575;
            color: white;
        }
        
        .action-btn.secondary:hover {
            background: #616161;
        }
        
        .ui-minimized #ui-content {
            display: none;
        }
        
        .ui-minimized {
            width: 200px;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(floatingUI);
    
    // Add event listeners
    setupFloatingUIEvents();
    
    return floatingUI;
}

// Function to update the floating UI with current status
function updateFloatingUI() {
    const ui = document.getElementById('viewblock-floating-ui');
    if (!ui) return;
    
    const statusText = ui.querySelector('#status-text');
    const progressInfo = ui.querySelector('#progress-info');
    const startAutoPagingBtn = ui.querySelector('#start-auto-paging');
    const captureCurrentBtn = ui.querySelector('#capture-current');
    const downloadDataBtn = ui.querySelector('#download-data');
    const debugInfoBtn = ui.querySelector('#debug-info');
    
    if (autoPagingState.isActive) {
        statusText.textContent = `Auto-capturing page ${autoPagingState.currentPage}/${autoPagingState.maxPages}`;
        progressInfo.textContent = `Page: ${autoPagingState.currentPage} | Captured: ${autoPagingState.capturedTransactions.length}`;
        startAutoPagingBtn.textContent = 'Stop Auto-Capture';
        startAutoPagingBtn.classList.remove('success');
        startAutoPagingBtn.classList.add('danger');
        captureCurrentBtn.style.display = 'none';
        downloadDataBtn.style.display = 'block';
        debugInfoBtn.style.display = 'block';
    } else {
        statusText.textContent = `Ready - ${autoPagingState.capturedTransactions.length} transactions captured`;
        progressInfo.textContent = autoPagingState.capturedTransactions.length > 0 ? 
            `Last capture: ${new Date().toLocaleTimeString()}` : '';
        startAutoPagingBtn.textContent = 'Start Auto-Capture';
        startAutoPagingBtn.classList.remove('danger');
        startAutoPagingBtn.classList.add('success');
        captureCurrentBtn.style.display = 'block';
        downloadDataBtn.style.display = 'block';
        debugInfoBtn.style.display = 'block';
    }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openFloatingUI') {
        if (isViewBlockThorchainPage()) {
            createFloatingUI();
            updateFloatingUI();
            sendResponse({success: true});
        } else {
            sendResponse({success: false, error: 'Not on ViewBlock THORChain page'});
        }
    }
});

async function captureCurrentPage() {
  try {
    const transactions = await extractTableData();
    const newData = await processTransactions(transactions);
    
    // Store the captured data
    chrome.storage.local.get(['capturedData'], function(result) {
      const existingData = result.capturedData || [];
      const updatedData = [...existingData, ...newData];
      chrome.storage.local.set({ capturedData: updatedData });
    });

    return {
      success: true,
      transactions: newData
    };
  } catch (error) {
    console.error('Error capturing current page:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

async function capturePageWithNavigation(pageNumber, maxPages) {
  try {
    // Navigate to the specific page if not on page 1
    if (pageNumber > 1) {
      await navigateToPage(pageNumber);
      await waitForTableLoad();
    }

    const transactions = await extractTableData();
    const newData = await processTransactions(transactions);
    
    // Store the captured data
    chrome.storage.local.get(['capturedData'], function(result) {
      const existingData = result.capturedData || [];
      const updatedData = [...existingData, ...newData];
      chrome.storage.local.set({ capturedData: updatedData });
    });

    // Check if there are more pages
    const hasMorePages = await checkForMorePages();

    return {
      success: true,
      transactions: newData,
      hasMorePages: hasMorePages && pageNumber < maxPages,
      pageNumber: pageNumber
    };
  } catch (error) {
    console.error('Error capturing page with navigation:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

async function captureAllPages() {
  try {
    let allTransactions = [];
    let pagesProcessed = 0;
    let currentPage = 1;
    const maxPages = 50; // Limit to prevent infinite loops

    while (currentPage <= maxPages) {
      // Navigate to page if not on first page
      if (currentPage > 1) {
        await navigateToPage(currentPage);
        await waitForTableLoad();
      }

      const transactions = await extractTableData();
      if (transactions.length === 0) {
        break; // No more data
      }

      const processedTransactions = await processTransactions(transactions);
      allTransactions = [...allTransactions, ...processedTransactions];
      pagesProcessed++;

      // Update progress
      const progress = Math.round((currentPage / maxPages) * 100);
      chrome.runtime.sendMessage({
        action: 'updateProgress',
        progress: progress
      });

      currentPage++;
      
      // Small delay between pages
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Store all captured data
    chrome.storage.local.set({ capturedData: allTransactions });

    return {
      success: true,
      totalTransactions: allTransactions.length,
      pagesProcessed: pagesProcessed
    };
  } catch (error) {
    console.error('Error capturing all pages:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

async function checkForMorePages() {
  try {
    // Look for pagination controls
    const pagination = document.querySelector('[class*="pagination"], [class*="Pagination"]');
    if (pagination) {
      // Check for next button
      const nextButton = pagination.querySelector('button[aria-label*="next"], button[aria-label*="Next"], a[aria-label*="next"], a[aria-label*="Next"]');
      if (nextButton && !nextButton.disabled && nextButton.style.display !== 'none') {
        return true;
      }
    }
    
    // Check for "Load More" buttons using text content
    const allButtons = document.querySelectorAll('button');
    for (const button of allButtons) {
      const buttonText = button.textContent.trim().toLowerCase();
      if ((buttonText.includes('load more') || buttonText.includes('show more')) && 
          button.offsetParent !== null && !button.disabled) {
        return true;
      }
    }
    
    // Check for data-testid load more
    const loadMoreByTestId = document.querySelector('[data-testid="load-more"]');
    if (loadMoreByTestId && loadMoreByTestId.offsetParent !== null && !loadMoreByTestId.disabled) {
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error checking for more pages:', error);
    return false;
  }
}

async function extractTableData() {
  console.log('Starting table data extraction...');
  
  // Try multiple table selectors
  const tableSelectors = [
    'table',
    '[role="table"]',
    '.table',
    '[class*="table"]',
    '[class*="Table"]',
    'div[class*="table"]',
    'div[class*="Table"]'
  ];
  
  let table = null;
  for (const selector of tableSelectors) {
    table = document.querySelector(selector);
    if (table) {
      console.log(`Found table with selector: ${selector}`);
      break;
    }
  }
  
  if (!table) {
    console.log('No table found, checking for alternative structures...');
    
    // Look for div-based table structures
    const divTable = document.querySelector('[class*="table"], [class*="Table"], [role="grid"]');
    if (divTable) {
      console.log('Found div-based table structure');
      return await extractDivTableData(divTable);
    }
    
    // Log all elements that might be tables
    const allElements = document.querySelectorAll('*');
    console.log('Available elements that might be tables:');
    for (const el of allElements) {
      if (el.className && (el.className.includes('table') || el.className.includes('Table') || el.className.includes('row'))) {
        console.log(`Potential table element: ${el.tagName} with classes: ${el.className}`);
      }
    }
    
    throw new Error('No table found on page');
  }

  const rows = table.querySelectorAll('tr');
  console.log(`Found ${rows.length} rows in table`);
  
  const transactions = [];

  // Skip header row
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    const cells = row.querySelectorAll('td');
    
    console.log(`Row ${i}: ${cells.length} cells`);
    
    if (cells.length >= 5) {
      // Extract data from the 5 columns: Info, Type, Action, Status, Time
      const infoText = await extractFullText(cells[0]);
      const typeText = await extractFullText(cells[1]);
      const actionText = await extractFullText(cells[2]);
      const statusText = await extractFullText(cells[3]);
      const timeText = await extractFullText(cells[4]);
      
      console.log(`Row ${i} cell data:`);
      console.log(`  Info: "${infoText}"`);
      console.log(`  Type: "${typeText}"`);
      console.log(`  Action: "${actionText}"`);
      console.log(`  Status: "${statusText}"`);
      console.log(`  Time: "${timeText}"`);
      
      // Debug regex matches
      const rawText = row.textContent.trim();
      const rawHashMatch = rawText.match(/[a-fA-F0-9]{64}/);
      const rawAmountMatch = rawText.match(/([\d,]+\.?\d*)([A-Z]+)([\d,]+\.?\d*)?([A-Z]+)?/);
      
      // Parse the Info column which contains hash and block info
      // The Info column contains: "Info4C76…81F921,855,951thor…ehsw0xA3…2479"
      // We need to extract the hash part: "4C76…81F9"
      const hashMatch = infoText.match(/Info([A-F0-9]{4})…([A-F0-9]{4})/);
      
      // Extract block height - look for the block number after the hash
      // Pattern: "4C76…81F921,855,951" -> extract "21,855,951"
      const blockMatch = infoText.match(/[A-F0-9]{4}…[A-F0-9]{4}(\d{1,3}(?:,\d{3})*)/);
      
      // Also try to extract from raw text for better accuracy
      // Look for the pattern: InfoXXXX…XXXX21,855,349...
      const rawBlockMatch = rawText.match(/Info[A-F0-9]{4}…[A-F0-9]{4}(\d{1,3}(?:,\d{3})*)/);
      
      // Parse the Action column which contains the swap details
      // Look for patterns like "0.00917145BTC11.20742389LTC" or "500USDT7,678.72THOR"
      // We need to be more specific to avoid matching hash parts
      const cleanActionText = actionText.replace('Action', '').trim();
      
      // Parse the action text to extract from/to amounts and assets
      // Pattern: "2,500TCY566.69307USDT" -> from: 2500 TCY, to: 566.69307 USDT
      const actionAmountMatch = cleanActionText.match(/^([\d,]+\.?\d*)([A-Z]+)([\d,]+\.?\d*)?([A-Z]+)?$/);
      
      // For cases where there's no second asset like "5,000USDC0"
      const singleAssetMatch = cleanActionText.match(/^([\d,]+\.?\d*)([A-Z]+)0$/);
      
      console.log(`  Raw text: "${rawText}"`);
      console.log(`  Clean action text: "${cleanActionText}"`);
      console.log(`  Hash match:`, hashMatch);
      console.log(`  Block match:`, blockMatch);
      console.log(`  Action amount match:`, actionAmountMatch);
      
      // Improved regex to handle various formats:
      // "0.00917145BTC11.20742389LTC" -> from: 0.00917145 BTC, to: 11.20742389 LTC
      // "500USDT7,678.72THOR" -> from: 500 USDT, to: 7,678.72 THOR
      // "3,906.71FOX0.00083342BTC" -> from: 3,906.71 FOX, to: 0.00083342 BTC
      // But avoid matching hash parts by being more specific about where we look
      
      const transaction = {
        tx_hash: hashMatch ? `${hashMatch[1]}…${hashMatch[2]}` : '',
        block_height: rawBlockMatch ? rawBlockMatch[1] : (blockMatch ? blockMatch[1] : ''),
        timestamp: timeText.replace('Time', '').trim(),
        type: typeText.replace('Type', '').trim(),
        action: cleanActionText,
        status: statusText.replace('Status', '').trim(),
        from_asset: actionAmountMatch ? actionAmountMatch[2] : (singleAssetMatch ? singleAssetMatch[2] : ''),
        to_asset: actionAmountMatch && actionAmountMatch[4] ? actionAmountMatch[4] : '',
        from_amount: actionAmountMatch ? parseFloat(actionAmountMatch[1].replace(/,/g, '')) : (singleAssetMatch ? parseFloat(singleAssetMatch[1].replace(/,/g, '')) : null),
        to_amount: actionAmountMatch && actionAmountMatch[3] ? parseFloat(actionAmountMatch[3].replace(/,/g, '')) : (singleAssetMatch ? 0 : null),
        raw_row_text: rawText
      };
      
      console.log('Extracted transaction:', transaction);
      transactions.push(transaction);
    }
  }

  return transactions;
}

async function extractDivTableData(container) {
  console.log('Extracting data from div-based table structure...');
  
  // Look for row-like elements
  const rowSelectors = [
    '[class*="row"]',
    '[class*="Row"]',
    '[role="row"]',
    'div[class*="row"]',
    'div[class*="Row"]'
  ];
  
  let rows = [];
  for (const selector of rowSelectors) {
    rows = container.querySelectorAll(selector);
    if (rows.length > 0) {
      console.log(`Found ${rows.length} rows with selector: ${selector}`);
      break;
    }
  }
  
  if (rows.length === 0) {
    // Fallback: look for any divs that might be rows
    rows = container.querySelectorAll('div');
    console.log(`Fallback: found ${rows.length} divs`);
  }
  
  const transactions = [];
  
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const cells = row.querySelectorAll('div, span, td');
    
    console.log(`Div row ${i}: ${cells.length} cells, text: ${row.textContent.substring(0, 100)}...`);
    
    if (cells.length >= 3) {
      // Try to extract data from the row text
      const rowText = row.textContent.trim();
      
      // Look for patterns in the text
      const transaction = {
        tx_hash: extractHashFromText(rowText),
        block_height: extractBlockFromText(rowText),
        timestamp: extractTimestampFromText(rowText),
        from_address: extractAddressFromText(rowText, 'from'),
        to_address: extractAddressFromText(rowText, 'to'),
        amount: extractAmountFromText(rowText),
        raw_row_text: rowText
      };
      
      if (transaction.tx_hash || transaction.amount) {
        console.log('Extracted transaction from div:', transaction);
        transactions.push(transaction);
      }
    }
  }
  
  return transactions;
}

function extractHashFromText(text) {
  // Look for hash patterns
  const hashMatch = text.match(/[a-fA-F0-9]{64}/);
  return hashMatch ? hashMatch[0] : '';
}

function extractBlockFromText(text) {
  // Look for block number patterns
  const blockMatch = text.match(/(\d{1,3}(?:,\d{3})*)/);
  return blockMatch ? blockMatch[1] : '';
}

function extractTimestampFromText(text) {
  // Look for timestamp patterns
  const timestampMatch = text.match(/(\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2})/);
  return timestampMatch ? timestampMatch[1] : '';
}

function extractAddressFromText(text, type) {
  // Look for address patterns (thor1...)
  const addressMatch = text.match(/thor1[a-zA-Z0-9]{38,}/);
  return addressMatch ? addressMatch[0] : '';
}

function extractAmountFromText(text) {
  // Look for amount patterns (e.g., "1.234 BTC → 0.567 ETH")
  const amountMatch = text.match(/([\d,]+\.?\d*)\s*([A-Z]+)\s*→\s*([\d,]+\.?\d*)\s*([A-Z]+)/);
  if (amountMatch) {
    return `${amountMatch[1]} ${amountMatch[2]} → ${amountMatch[3]} ${amountMatch[4]}`;
  }
  return '';
}

async function extractFullText(element) {
  // First try to get the title attribute (common for tooltips)
  let fullText = element.getAttribute('title') || element.textContent.trim();
  
  // If the element has a data attribute with full text, use that
  const dataFull = element.getAttribute('data-full') || element.getAttribute('data-tooltip');
  if (dataFull) {
    fullText = dataFull;
  }
  
  // Try to trigger hover and capture tooltip
  try {
    // Create a mouseover event
    const mouseoverEvent = new MouseEvent('mouseover', {
      bubbles: true,
      cancelable: true,
      view: window
    });
    
    element.dispatchEvent(mouseoverEvent);
    
    // Wait a bit for tooltip to appear
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Look for tooltip elements
    const tooltips = document.querySelectorAll('[class*="tooltip"], [class*="Tooltip"], [class*="popover"], [class*="Popover"]');
    
    for (const tooltip of tooltips) {
      if (tooltip.style.display !== 'none' && tooltip.offsetParent !== null) {
        const tooltipText = tooltip.textContent.trim();
        if (tooltipText && tooltipText !== fullText) {
          fullText = tooltipText;
          break;
        }
      }
    }
    
    // Trigger mouseout to hide tooltip
    const mouseoutEvent = new MouseEvent('mouseout', {
      bubbles: true,
      cancelable: true,
      view: window
    });
    element.dispatchEvent(mouseoutEvent);
    
  } catch (error) {
    console.warn('Error extracting tooltip:', error);
  }
  
  return fullText;
}

async function processTransactions(transactions) {
  return transactions.map(tx => {
    return {
      ...tx,
      affiliate_address: 'ss', // Since we're on the affiliate=ss page
      captured_at: new Date().toISOString()
    };
  });
}

function parseAmountField(amountText) {
  const result = {
    fromAsset: null,
    toAsset: null,
    fromAmount: null,
    toAmount: null
  };
  
  if (!amountText) return result;
  
  // Look for patterns like "1.234 BTC → 0.567 ETH"
  const arrowMatch = amountText.match(/(.+?)\s*→\s*(.+)/);
  if (arrowMatch) {
    const fromPart = arrowMatch[1].trim();
    const toPart = arrowMatch[2].trim();
    
    // Parse from part
    const fromMatch = fromPart.match(/([\d,]+\.?\d*)\s*([A-Z]+)/);
    if (fromMatch) {
      result.fromAmount = parseFloat(fromMatch[1].replace(/,/g, ''));
      result.fromAsset = fromMatch[2];
    }
    
    // Parse to part
    const toMatch = toPart.match(/([\d,]+\.?\d*)\s*([A-Z]+)/);
    if (toMatch) {
      result.toAmount = parseFloat(toMatch[1].replace(/,/g, ''));
      result.toAsset = toMatch[2];
    }
  }
  
  return result;
}

async function navigateToPage(pageNumber) {
  try {
    console.log(`Attempting to navigate to page ${pageNumber}`);
    
    // Look for pagination controls
    const pagination = document.querySelector('[class*="pagination"], [class*="Pagination"]');
    if (pagination) {
      console.log('Found pagination controls');
      
      // Try to find the specific page button
      const pageButtons = pagination.querySelectorAll('button, a');
      for (const button of pageButtons) {
        const buttonText = button.textContent.trim();
        console.log(`Checking button: "${buttonText}"`);
        if (buttonText === pageNumber.toString()) {
          console.log(`Found page ${pageNumber} button, clicking...`);
          button.click();
          return;
        }
      }
      
      // If specific page button not found, try next button
      if (pageNumber > 1) {
        const nextButton = pagination.querySelector('button[aria-label*="next"], button[aria-label*="Next"], a[aria-label*="next"], a[aria-label*="Next"]');
        if (nextButton && !nextButton.disabled) {
          console.log('Found next button, clicking...');
          nextButton.click();
          return;
        }
      }
    }
    
    // Fallback: try to modify URL
    console.log('Using URL-based navigation');
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('page', pageNumber);
    window.location.href = currentUrl.toString();
  } catch (error) {
    console.error('Error navigating to page:', error);
  }
}

async function waitForTableLoad() {
  try {
    // Wait for table to be present and loaded
    let attempts = 0;
    const maxAttempts = 10;
    
    while (attempts < maxAttempts) {
      const table = document.querySelector('table, [role="table"], [class*="table"], [class*="Table"]');
      if (table) {
        const rows = table.querySelectorAll('tr, [role="row"]');
        if (rows.length > 1) { // At least header + 1 data row
          return true;
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 500));
      attempts++;
    }
    
    return false;
  } catch (error) {
    console.error('Error waiting for table load:', error);
    return false;
  }
}

async function waitForTableLoad() {
  await waitForElement('table');
  // Additional wait for data to load
  await new Promise(resolve => setTimeout(resolve, 2000));
}

async function waitForElement(selector) {
  return new Promise((resolve) => {
    if (document.querySelector(selector)) {
      resolve();
      return;
    }
    
    const observer = new MutationObserver(() => {
      if (document.querySelector(selector)) {
        observer.disconnect();
        resolve();
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      observer.disconnect();
      resolve();
    }, 10000);
  });
}

// Auto-capture when page loads (optional)
if (window.location.href.includes('viewblock.io/thorchain/txs')) {
  console.log('ViewBlock THORChain page detected. Extension ready.');
}

async function debugPageStructure() {
  console.log('=== DEBUGGING PAGE STRUCTURE ===');
  
  // Log the current URL
  console.log('Current URL:', window.location.href);
  
  // Check if we're on the right page
  if (!window.location.href.includes('viewblock.io/thorchain/txs')) {
    console.log('❌ Not on ViewBlock THORChain page');
    return { success: false, error: 'Not on correct page' };
  }
  
  console.log('✅ On ViewBlock THORChain page');
  
  // Look for various table structures
  const tableSelectors = [
    'table',
    '[role="table"]',
    '.table',
    '[class*="table"]',
    '[class*="Table"]',
    'div[class*="table"]',
    'div[class*="Table"]',
    '[role="grid"]'
  ];
  
  console.log('Searching for table structures...');
  for (const selector of tableSelectors) {
    const elements = document.querySelectorAll(selector);
    console.log(`${selector}: ${elements.length} elements found`);
    if (elements.length > 0) {
      for (let i = 0; i < Math.min(3, elements.length); i++) {
        console.log(`  Element ${i}:`, elements[i]);
        console.log(`  Classes:`, elements[i].className);
        console.log(`  Text preview:`, elements[i].textContent.substring(0, 200));
      }
    }
  }
  
  // Look for row structures
  const rowSelectors = [
    'tr',
    '[role="row"]',
    '[class*="row"]',
    '[class*="Row"]'
  ];
  
  console.log('Searching for row structures...');
  for (const selector of rowSelectors) {
    const elements = document.querySelectorAll(selector);
    console.log(`${selector}: ${elements.length} elements found`);
    if (elements.length > 0) {
      for (let i = 0; i < Math.min(3, elements.length); i++) {
        console.log(`  Row ${i}:`, elements[i].textContent.substring(0, 200));
      }
    }
  }
  
  // Look for any elements with transaction-like text
  console.log('Searching for transaction-like content...');
  const allElements = document.querySelectorAll('*');
  let txLikeElements = 0;
  for (const el of allElements) {
    const text = el.textContent;
    if (text && (text.includes('thor1') || text.includes('BTC') || text.includes('ETH') || text.includes('→'))) {
      console.log(`Transaction-like element:`, el.tagName, el.className, text.substring(0, 100));
      txLikeElements++;
      if (txLikeElements > 10) break;
    }
  }
  
  console.log('=== DEBUG COMPLETE ===');
  return { success: true };
} 

// Function to download captured data
function downloadCapturedData() {
    const data = autoPagingState.capturedTransactions.length > 0 ? 
        autoPagingState.capturedTransactions : capturedData;
    
    if (data.length === 0) {
        alert('No data to download. Please capture some transactions first.');
        return;
    }
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `viewblock_thorchain_data_${timestamp}.json`;
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log(`Downloaded ${data.length} transactions to ${filename}`);
}

// Function to show debug information
function showDebugInfo() {
    const table = document.querySelector('table');
    const paginationElements = document.querySelectorAll('button, a');
    
    let debugInfo = `=== ViewBlock THORChain Debug Info ===\n\n`;
    debugInfo += `Current URL: ${window.location.href}\n`;
    debugInfo += `Page Title: ${document.title}\n\n`;
    
    if (table) {
        const rows = table.querySelectorAll('tbody tr');
        debugInfo += `Table found with ${rows.length} rows\n`;
        
        if (rows.length > 0) {
            const firstRow = rows[0];
            const cells = firstRow.querySelectorAll('td');
            debugInfo += `First row has ${cells.length} cells\n`;
            
            for (let i = 0; i < Math.min(cells.length, 5); i++) {
                const cell = cells[i];
                debugInfo += `Cell ${i + 1}: "${cell.textContent.trim()}"\n`;
            }
        }
    } else {
        debugInfo += `No table found on page\n`;
    }
    
    debugInfo += `\nPagination elements found: ${paginationElements.length}\n`;
    paginationElements.forEach((element, index) => {
        const text = element.textContent.trim();
        const ariaLabel = element.getAttribute('aria-label');
        if (text || ariaLabel) {
            debugInfo += `Element ${index + 1}: text="${text}", aria-label="${ariaLabel}"\n`;
        }
    });
    
    debugInfo += `\nCaptured transactions: ${autoPagingState.capturedTransactions.length}\n`;
    debugInfo += `Auto-paging state: ${JSON.stringify(autoPagingState, null, 2)}\n`;
    
    console.log(debugInfo);
    alert(debugInfo);
}

// Function to setup floating UI event listeners
function setupFloatingUIEvents() {
    const ui = document.getElementById('viewblock-floating-ui');
    if (!ui) return;
    
    // Make draggable
    let isDragging = false;
    let dragOffset = { x: 0, y: 0 };
    
    const header = ui.querySelector('#ui-header');
    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        dragOffset = {
            x: e.clientX - ui.offsetLeft,
            y: e.clientY - ui.offsetTop
        };
    });
    
    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            ui.style.left = (e.clientX - dragOffset.x) + 'px';
            ui.style.top = (e.clientY - dragOffset.y) + 'px';
            ui.style.right = 'auto';
        }
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    // Settings change handlers
    ui.querySelector('#max-pages').addEventListener('change', (e) => {
        autoPagingState.maxPages = parseInt(e.target.value);
        saveAutoPagingState();
    });
    
    ui.querySelector('#page-delay').addEventListener('change', (e) => {
        autoPagingState.delay = parseInt(e.target.value);
        saveAutoPagingState();
    });
    
    // Button event listeners
    ui.querySelector('#capture-current').addEventListener('click', () => {
        console.log('Capturing current page...');
        const data = captureCurrentPageData();
        if (data.length > 0) {
            autoPagingState.capturedTransactions.push(...data);
            saveAutoPagingState();
            updateFloatingUI();
            console.log(`Captured ${data.length} transactions from current page`);
            alert(`Captured ${data.length} transactions from current page!`);
        } else {
            alert('No transactions found on current page');
        }
    });
    
    ui.querySelector('#start-auto-paging').addEventListener('click', () => {
        if (autoPagingState.isActive) {
            stopAutoPaging();
        } else {
            // Update settings from UI
            autoPagingState.maxPages = parseInt(ui.querySelector('#max-pages').value);
            autoPagingState.delay = parseInt(ui.querySelector('#page-delay').value);
            startAutoPaging();
        }
    });
    
    ui.querySelector('#download-data').addEventListener('click', () => {
        downloadCapturedData();
    });
    
    ui.querySelector('#debug-info').addEventListener('click', () => {
        showDebugInfo();
    });
    
    ui.querySelector('#ui-minimize').addEventListener('click', () => {
        ui.classList.toggle('ui-minimized');
    });
    
    ui.querySelector('#ui-close').addEventListener('click', () => {
        ui.remove();
    });
}

// Initialize when page loads
function initializeExtension() {
    if (isViewBlockThorchainPage()) {
        console.log('ViewBlock THORChain page detected. Extension ready.');
        
        // Create floating UI
        setTimeout(() => {
            createFloatingUI();
            updateFloatingUI();
        }, 1000);
        
        // Load state and potentially resume auto-paging
        loadAutoPagingState();
    } else {
        console.log('Not on ViewBlock THORChain page, extension inactive');
    }
}

// Initialize immediately and on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeExtension);
} else {
    initializeExtension();
} 