// DeFi Data Snatcher v3 - Crypto Transaction Table Capture Extension

// Prevent multiple injections - ULTRA aggressive approach
if (window.defiDataSnatcherV3Loaded) {
  console.log('🚫 DeFi Data Snatcher v3 already loaded, skipping...');
  return; // Exit early instead of throwing error
}

// Set flag immediately
window.defiDataSnatcherV3Loaded = true;

// Also check if our UI already exists
if (document.getElementById('defi-snatcher-v3-ui')) {
  console.log('🚫 UI already exists, skipping...');
  return;
}

// Check if any of our functions already exist
if (window.defiDataSnatcherV3Functions) {
  console.log('🚫 Functions already exist, skipping...');
  return;
}

// Mark functions as loaded
window.defiDataSnatcherV3Functions = true;

console.log('🚀 DeFi Data Snatcher v3 loaded!');

// Global variables - check if they already exist
if (typeof window.defiDataSnatcherV3Data === 'undefined') {
  window.defiDataSnatcherV3Data = {
    capturedData: [],
    isCapturing: false,
    currentTable: null,
    previewData: null,
    selectedTable: null
  };
}

// Use the global data object
const data = window.defiDataSnatcherV3Data;

// Create the main UI
function createUI() {
  console.log('🎯 Creating DeFi Data Snatcher v3 UI...');
  
  // Remove existing UI if it exists
  const existingUI = document.getElementById('defi-snatcher-v3-ui');
  if (existingUI) {
    console.log('🗑️ Removing existing UI');
    existingUI.remove();
  }
  
  // Create new UI with unique timestamp
  const ui = document.createElement('div');
  ui.id = 'defi-snatcher-v3-ui';
  ui.setAttribute('data-timestamp', Date.now());
  ui.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      width: 350px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 15px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.4);
      z-index: 10000;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      backdrop-filter: blur(10px);
    ">
      <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="
          width: 40px;
          height: 40px;
          background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 15px;
          font-size: 20px;
        ">💎</div>
        <h3 style="margin: 0; font-size: 18px;">DeFi Data Snatcher v3</h3>
      </div>
      
      <div style="margin-bottom: 20px;">
        <button id="captureBtn" style="
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 8px;
          background: linear-gradient(45deg, #4CAF50, #45a049);
          color: white;
          cursor: pointer;
          font-weight: bold;
          font-size: 14px;
          transition: all 0.3s ease;
        ">🎯 Start Table Selection</button>
      </div>
      
      <div style="margin-bottom: 20px;">
        <button id="exportBtn" style="
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 8px;
          background: linear-gradient(45deg, #2196F3, #1976D2);
          color: white;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.3s ease;
        ">📊 Export Data</button>
      </div>
      
      <div style="margin-bottom: 20px;">
        <button id="clearBtn" style="
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 8px;
          background: linear-gradient(45deg, #FF9800, #F57C00);
          color: white;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.3s ease;
        ">🗑️ Clear Data</button>
      </div>
      
      <div style="margin-bottom: 20px;">
        <button id="closeBtn" style="
          width: 100%;
          padding: 12px;
          border: none;
          border-radius: 8px;
          background: linear-gradient(45deg, #9E9E9E, #757575);
          color: white;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.3s ease;
        ">❌ Close</button>
      </div>
      
      <div id="status" style="
        padding: 12px;
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        font-size: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
      ">
        Ready to start table selection
      </div>
      
      <div id="stats" style="
        margin-top: 15px;
        padding: 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        font-size: 11px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
      ">
        Captured: 0 transactions
      </div>
    </div>
  `;
  
  // Add event listeners
  ui.querySelector('#captureBtn').addEventListener('click', startTableSelection);
  ui.querySelector('#exportBtn').addEventListener('click', exportData);
  ui.querySelector('#clearBtn').addEventListener('click', clearData);
  ui.querySelector('#closeBtn').addEventListener('click', () => ui.remove());
  
  // Add hover effects
  const buttons = ui.querySelectorAll('button');
  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      btn.style.transform = 'translateY(-2px)';
      btn.style.boxShadow = '0 5px 15px rgba(0,0,0,0.3)';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translateY(0)';
      btn.style.boxShadow = 'none';
    });
  });
  
  // Make draggable
  makeDraggable(ui);
  
  // Add to page
  document.body.appendChild(ui);
  
  console.log('✅ DeFi Data Snatcher v3 UI created and added to page');
  return ui;
}

// Make UI draggable
function makeDraggable(ui) {
  const header = ui.querySelector('h3');
  let isDragging = false;
  let currentX;
  let currentY;
  let initialX;
  let initialY;
  let xOffset = 0;
  let yOffset = 0;
  
  header.addEventListener('mousedown', (e) => {
    initialX = e.clientX - xOffset;
    initialY = e.clientY - yOffset;
    isDragging = true;
    e.preventDefault();
  });
  
  document.addEventListener('mousemove', (e) => {
    if (isDragging) {
      e.preventDefault();
      currentX = e.clientX - initialX;
      currentY = e.clientY - initialY;
      xOffset = currentX;
      yOffset = currentY;
      ui.style.transform = `translate(${currentX}px, ${currentY}px)`;
    }
  });
  
  document.addEventListener('mouseup', () => {
    isDragging = false;
  });
}

// Start table selection mode
function startTableSelection() {
  if (data.isCapturing) return;
  
  console.log('🚀 Starting table selection mode...');
  
  data.isCapturing = true;
  data.selectedTable = null;
  
  const captureBtn = document.getElementById('captureBtn');
  captureBtn.textContent = '⏸️ Stop Selection';
  captureBtn.style.background = 'linear-gradient(45deg, #f44336, #d32f2f)';
  captureBtn.onclick = stopTableSelection;
  
  document.getElementById('status').textContent = '🎯 Highlight part of a table to select it...';
  
  // Add selection change listener
  document.addEventListener('selectionchange', handleSelectionChange);
  console.log('✅ Added selectionchange listener');
  
  // Also add click listener as fallback
  document.addEventListener('click', handleTableClick);
  console.log('✅ Added click listener');
  
  // Add visual indicators to tables
  highlightTables();
  
  console.log('🎯 Table selection mode activated - waiting for table selection');
}

// Handle selection changes
function handleSelectionChange() {
  if (!data.isCapturing) return;
  
  console.log('🎯 Selection changed, checking for table...');
  
  const selection = window.getSelection();
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0);
    console.log('📝 Range found:', range);
    
    // Try to find table from the selection
    let table = findParentTable(range.commonAncestorContainer);
    
    // If no table found, try from the start container
    if (!table) {
      table = findParentTable(range.startContainer);
    }
    
    // If still no table, try from the end container
    if (!table) {
      table = findParentTable(range.endContainer);
    }
    
    console.log('🔍 Table found:', table);
    
    if (table && table !== data.selectedTable) {
      console.log('✅ New table selected, updating UI...');
      data.selectedTable = table;
      
      // Highlight the selected table
      highlightSelectedTable(table);
      
      // Update status to show preview button
      document.getElementById('status').textContent = 
        `✅ Table selected! Click "Preview Capture" to see what will be captured.`;
      
      // Change button to preview mode
      const captureBtn = document.getElementById('captureBtn');
      captureBtn.textContent = '👁️ Preview Capture';
      captureBtn.style.background = 'linear-gradient(45deg, #FF9800, #F57C00)';
      captureBtn.onclick = () => {
        if (data.selectedTable) {
          previewTableCapture(data.selectedTable);
          stopTableSelection();
        }
      };
    }
  }
}

// Handle table clicks as fallback
function handleTableClick(event) {
  if (!data.isCapturing) return;
  
  console.log('🖱️ Table clicked, checking for table...');
  
  const table = findParentTable(event.target);
  if (table && table !== data.selectedTable) {
    console.log('✅ Table found via click, updating UI...');
    data.selectedTable = table;
    
    // Highlight the selected table
    highlightSelectedTable(table);
    
    // Update status to show preview button
    document.getElementById('status').textContent = 
      `✅ Table selected! Click "Preview Capture" to see what will be captured.`;
    
    // Change button to preview mode
    const captureBtn = document.getElementById('captureBtn');
    captureBtn.textContent = '👁️ Preview Capture';
    captureBtn.style.background = 'linear-gradient(45deg, #FF9800, #F57C00)';
    captureBtn.onclick = () => {
      if (data.selectedTable) {
        previewTableCapture(data.selectedTable);
        stopTableSelection();
      }
    };
  }
}

// Highlight the selected table
function highlightSelectedTable(table) {
  // Remove previous highlights
  removeTableHighlights();
  
  // Add special highlight for selected table
  table.style.outline = '4px solid #FF9800';
  table.style.outlineOffset = '3px';
  table.style.transform = 'scale(1.02)';
  table.style.transition = 'all 0.3s ease';
  
  // Add selection indicator
  const indicator = document.createElement('div');
  indicator.style.cssText = `
    position: absolute;
    top: -40px;
    left: 50%;
    transform: translateX(-50%);
    background: #FF9800;
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: bold;
    z-index: 10001;
    pointer-events: none;
    animation: pulse 2s infinite;
  `;
  indicator.textContent = 'Table Selected! Click Preview to capture';
  
  table.parentElement.style.position = 'relative';
  table.parentElement.appendChild(indicator);
}

// Stop table selection
function stopTableSelection() {
  data.isCapturing = false;
  data.selectedTable = null;
  
  const captureBtn = document.getElementById('captureBtn');
  captureBtn.textContent = '🎯 Start Table Selection';
  captureBtn.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
  captureBtn.onclick = startTableSelection;
  
  document.getElementById('status').textContent = '✅ Selection stopped. Ready to start again.';
  
  // Remove selection listener
  document.removeEventListener('selectionchange', handleSelectionChange);
  
  // Remove click listener
  document.removeEventListener('click', handleTableClick);
  
  // Remove highlights
  removeTableHighlights();
}

// Find parent table element
function findParentTable(element) {
  if (!element) return null;
  
  let current = element;
  let depth = 0;
  const maxDepth = 10; // Prevent infinite loops
  
  while (current && current !== document.body && depth < maxDepth) {
    console.log('🔍 Checking element:', current.tagName, current.className, current.id);
    
    // Check if this element is a table
    if (current.tagName === 'TABLE') {
      console.log('✅ Found TABLE element');
      return current;
    }
    
    // Check if this element contains a table
    if (current.querySelector('table')) {
      console.log('✅ Found element containing table');
      return current;
    }
    
    // Check for common table classes
    if (current.classList.contains('table') || 
        current.classList.contains('MuiTable-root') ||
        current.classList.contains('ant-table') ||
        current.classList.contains('table-container') ||
        current.classList.contains('data-table')) {
      console.log('✅ Found table-like element with class:', current.className);
      return current;
    }
    
    // Check for table role
    if (current.getAttribute('role') === 'table') {
      console.log('✅ Found element with table role');
      return current;
    }
    
    // Check for table-like content (rows and cells)
    if (current.querySelector('tr, .MuiTableRow-root, .ant-table-row')) {
      console.log('✅ Found element with table rows');
      return current;
    }
    
    current = current.parentElement;
    depth++;
  }
  
  console.log('❌ No table found after checking', depth, 'levels');
  return null;
}

// Highlight potential tables
function highlightTables() {
  const tables = document.querySelectorAll('table, .table, [role="table"], .MuiTable-root, .ant-table');
  
  tables.forEach((table, index) => {
    if (!table.dataset.snatcherHighlighted) {
      table.dataset.snatcherHighlighted = 'true';
      
      // Add highlight border
      table.style.outline = '3px solid #4CAF50';
      table.style.outlineOffset = '2px';
      table.style.transition = 'all 0.3s ease';
      
      // Add click indicator
      const indicator = document.createElement('div');
      indicator.style.cssText = `
        position: absolute;
        top: -30px;
        left: 50%;
        transform: translateX(-50%);
        background: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        z-index: 10001;
        pointer-events: none;
        animation: pulse 2s infinite;
      `;
      indicator.textContent = 'Highlight this table to select it';
      
      // Add pulse animation
      const style = document.createElement('style');
      style.textContent = `
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.7; }
          100% { opacity: 1; }
        }
      `;
      document.head.appendChild(style);
      
      table.parentElement.style.position = 'relative';
      table.parentElement.appendChild(indicator);
      
      // Add hover effect
      table.addEventListener('mouseenter', () => {
        if (!data.selectedTable || table !== data.selectedTable) {
          table.style.outline = '3px solid #FF9800';
          table.style.transform = 'scale(1.01)';
        }
      });
      
      table.addEventListener('mouseleave', () => {
        if (!data.selectedTable || table !== data.selectedTable) {
          table.style.outline = '3px solid #4CAF50';
          table.style.transform = 'scale(1)';
        }
      });
    }
  });
}

// Remove table highlights
function removeTableHighlights() {
  const tables = document.querySelectorAll('[data-snatcher-highlighted]');
  
  tables.forEach(table => {
    table.style.outline = '';
    table.style.transform = '';
    delete table.dataset.snatcherHighlighted;
    
    // Remove indicator
    const indicator = table.parentElement.querySelector('div');
    if (indicator && (indicator.textContent === 'Highlight this table to select it' || 
                     indicator.textContent === 'Table Selected! Click Preview to capture')) {
      indicator.remove();
    }
  });
}

// Preview table capture
function previewTableCapture(table) {
  console.log('📊 Previewing table capture...');
  
  try {
    const tableData = parseTable(table);
    
    if (tableData.length > 0) {
      data.previewData = tableData;
      showPreviewModal(tableData);
      
      document.getElementById('status').textContent = 
        `✅ Preview ready: ${tableData.length} transactions detected`;
      
      console.log(`✅ Preview ready: ${tableData.length} transactions`);
    } else {
      document.getElementById('status').textContent = '⚠️ No transaction data found in table';
      console.log('⚠️ No transaction data found in table');
    }
    
  } catch (error) {
    console.error('❌ Error previewing table:', error);
    document.getElementById('status').textContent = `❌ Error: ${error.message}`;
  }
}

// Parse table data with enhanced token parsing
function parseTable(table) {
  const rows = table.querySelectorAll('tr, .MuiTableRow-root, .ant-table-row');
  const transactions = [];
  
  // Find header row to identify columns
  let headers = [];
  let dataRows = [];
  
  rows.forEach((row, index) => {
    const cells = row.querySelectorAll('td, th, .MuiTableCell-root, .ant-table-cell');
    
    if (index === 0 || cells[0].tagName === 'TH') {
      // Header row
      headers = Array.from(cells).map(cell => 
        cell.textContent.trim().toLowerCase().replace(/\s+/g, '_')
      );
    } else {
      // Data row
      dataRows.push(Array.from(cells).map(cell => cell.textContent.trim()));
    }
  });
  
  // If no clear headers, try to infer from first data row
  if (headers.length === 0 && dataRows.length > 0) {
    headers = ['project', 'from', 'to', 'status', 'time'];
  }
  
  // Parse each data row
  dataRows.forEach((rowData, rowIndex) => {
    if (rowData.length >= 3) { // Minimum columns for a transaction
      const transaction = {
        id: Date.now() + rowIndex,
        timestamp: new Date().toISOString(),
        platform: 'unknown',
        from_chain: '',
        from_address: '',
        from_token: '',
        from_amount: '',
        to_chain: '',
        to_address: '',
        to_token: '',
        to_amount: '',
        status: '',
        time_ago: '',
        raw_data: rowData.join(' | ')
      };
      
      // Map data to fields based on headers
      headers.forEach((header, colIndex) => {
        if (colIndex < rowData.length) {
          const value = rowData[colIndex];
          
          switch (header) {
            case 'project':
            case 'platform':
              transaction.platform = value;
              break;
            case 'from':
              const fromData = parseChainTokenDataEnhanced(value);
              transaction.from_chain = fromData.chain;
              transaction.from_address = fromData.address;
              transaction.from_token = fromData.token;
              transaction.from_amount = fromData.amount;
              break;
            case 'to':
              const toData = parseChainTokenDataEnhanced(value);
              transaction.to_chain = toData.chain;
              transaction.to_token = toData.token;
              transaction.to_amount = toData.amount;
              break;
            case 'status':
              transaction.status = value;
              break;
            case 'time':
            case 'time_ago':
              transaction.time_ago = value;
              break;
          }
        }
      });
      
      transactions.push(transaction);
    }
  });
  
  return transactions;
}

// Enhanced parsing for chain/token data
function parseChainTokenDataEnhanced(text) {
  const result = {
    chain: '',
    address: '',
    token: '',
    amount: ''
  };
  
  // Extract chain info (could be "chain" prefix or just the address)
  const chainMatch = text.match(/chain\s+([^\s]+)/i);
  if (chainMatch) {
    result.chain = chainMatch[1];
  }
  
  // Extract address - look for various formats
  const addressPatterns = [
    /(0x[a-fA-F0-9]{40})/, // Full address
    /(0x[a-fA-F0-9]{6,}?\.{3}[a-fA-F0-9]{6,})/, // Abbreviated address
    /([A-Za-z0-9]{20,})/, // Non-hex long addresses
    /(0x[a-fA-F0-9]{6,})/ // Short hex addresses
  ];
  
  for (const pattern of addressPatterns) {
    const match = text.match(pattern);
    if (match) {
      result.address = match[1];
      break;
    }
  }
  
  // Extract token amount and symbol with better pattern matching
  const tokenPatterns = [
    /(\d+(?:\.\d+)?)\s+([A-Z]{2,})/, // Standard: 0.1305 WETH
    /(\d+(?:\.\d+)?)\s*([A-Z]{2,})/, // No space: 0.1305WETH
    /([A-Z]{2,})\s+(\d+(?:\.\d+)?)/, // Reversed: WETH 0.1305
    /(\d+(?:\.\d+)?)\s*([A-Z]{3,})/, // Longer symbols: 0.1305 USDC
  ];
  
  for (const pattern of tokenPatterns) {
    const match = text.match(pattern);
    if (match) {
      result.amount = match[1];
      result.token = match[2];
      break;
    }
  }
  
  return result;
}

// Show preview modal with enhanced functionality
function showPreviewModal(data) {
  const preview = document.createElement('div');
  preview.id = 'data-preview-v3';
  preview.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 1000px;
    max-height: 80vh;
    background: white;
    border-radius: 15px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    z-index: 10002;
    overflow: hidden;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  `;
  
  preview.innerHTML = `
    <div style="
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    ">
      <h3 style="margin: 0;">📊 Table Capture Preview v3</h3>
      <div style="display: flex; gap: 10px;">
        <button id="copy-csv" style="
          background: rgba(255,255,255,0.2);
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 12px;
        ">📋 Copy CSV</button>
        <button id="close-preview" style="
          background: none;
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          padding: 5px;
        ">×</button>
      </div>
    </div>
    
    <div style="padding: 20px; max-height: 60vh; overflow-y: auto;">
      <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;">
        <h4 style="margin: 0 0 10px 0; color: #28a745;">✅ Preview Summary</h4>
        <p style="margin: 0; font-size: 14px;">
          <strong>${data.length}</strong> transactions detected and parsed. 
          Review the data below and click "Confirm Capture" when ready.
        </p>
      </div>
      
      <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 20px;">
        <thead>
          <tr style="background: #f5f5f5;">
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Platform</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">From</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">To</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Status</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Time</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(tx => `
            <tr>
              <td style="padding: 10px; border: 1px solid #ddd; font-weight: 600;">${tx.platform}</td>
              <td style="padding: 10px; border: 1px solid #ddd;">
                <div style="margin-bottom: 5px;">
                  <strong>${tx.from_amount} ${tx.from_token}</strong>
                </div>
                <div style="font-size: 11px; color: #666; font-family: monospace;">
                  ${tx.from_address || 'N/A'}
                </div>
              </td>
              <td style="padding: 10px; border: 1px solid #ddd;">
                <div style="margin-bottom: 5px;">
                  <strong>${tx.to_amount} ${tx.to_token}</strong>
                </div>
                <div style="font-size: 11px; color: #666; font-family: monospace;">
                  ${tx.to_address || 'N/A'}
                </div>
              </td>
              <td style="padding: 10px; border: 1px solid #ddd;">
                <span style="
                  padding: 4px 8px;
                  border-radius: 12px;
                  font-size: 11px;
                  font-weight: 600;
                  ${tx.status === 'Completed' ? 'background: #d4edda; color: #155724;' : 
                    tx.status === 'Processing' ? 'background: #fff3cd; color: #856404;' : 
                    'background: #f8d7da; color: #721c24;'}
                ">${tx.status}</span>
              </td>
              <td style="padding: 10px; border: 1px solid #ddd;">${tx.time_ago}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      
      <div style="text-align: center; margin-top: 20px;">
        <button id="confirm-capture" style="
          background: linear-gradient(45deg, #4CAF50, #45a049);
          color: white;
          border: none;
          padding: 15px 30px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          margin-right: 15px;
        ">✅ Confirm Capture</button>
        
        <button id="cancel-capture" style="
          background: linear-gradient(45deg, #9E9E9E, #757575);
          color: white;
          border: none;
          padding: 15px 30px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
        ">❌ Cancel</button>
      </div>
    </div>
  `;
  
  // Add event listeners
  preview.querySelector('#copy-csv').addEventListener('click', () => {
    const csvContent = convertToCSV(data);
    navigator.clipboard.writeText(csvContent).then(() => {
      const btn = preview.querySelector('#copy-csv');
      const originalText = btn.textContent;
      btn.textContent = '✅ Copied!';
      btn.style.background = '#28a745';
      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = 'rgba(255,255,255,0.2)';
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy:', err);
      alert('Failed to copy to clipboard. Please manually copy the data.');
    });
  });
  
  preview.querySelector('#confirm-capture').addEventListener('click', () => {
    // Capture the data
    data.capturedData.push(...data);
    updateStats();
    
    // Close preview
    preview.remove();
    
    // Update UI
    document.getElementById('status').textContent = `✅ Captured ${data.length} transactions! Ready for export.`;
    
    // Show success message
    showMessage(`Successfully captured ${data.length} transactions!`, 'success');
  });
  
  preview.querySelector('#cancel-capture').addEventListener('click', () => {
    preview.remove();
    document.getElementById('status').textContent = '❌ Capture cancelled. Ready for new selection.';
  });
  
  preview.querySelector('#close-preview').addEventListener('click', () => {
    preview.remove();
    document.getElementById('status').textContent = '❌ Preview closed. Ready for new selection.';
  });
  
  // Close on outside click
  preview.addEventListener('click', (e) => {
    if (e.target === preview) {
      preview.remove();
      document.getElementById('status').textContent = '❌ Preview closed. Ready for new selection.';
    }
  });
  
  document.body.appendChild(preview);
}

// Show message to user
function showMessage(message, type = 'info') {
  const messageDiv = document.createElement('div');
  messageDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 8px;
    color: white;
    font-size: 14px;
    font-weight: bold;
    z-index: 10003;
    max-width: 300px;
    word-wrap: break-word;
    animation: slideIn 0.3s ease;
  `;
  
  // Set background color based on type
  switch (type) {
    case 'error':
      messageDiv.style.background = 'linear-gradient(45deg, #f44336, #d32f2f)';
      break;
    case 'success':
      messageDiv.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
      break;
    default:
      messageDiv.style.background = 'linear-gradient(45deg, #2196F3, #1976D2)';
  }
  
  messageDiv.textContent = message;
  document.body.appendChild(messageDiv);
  
  // Remove after 5 seconds
  setTimeout(() => {
    if (messageDiv.parentNode) {
      messageDiv.remove();
    }
  }, 5000);
}

// Update stats
function updateStats() {
  const total = data.capturedData.length;
  document.getElementById('stats').textContent = `Captured: ${total} transactions`;
}

// Export data
function exportData() {
  if (data.capturedData.length === 0) {
    showMessage('No data to export!', 'error');
    return;
  }
  
  try {
    const csvContent = convertToCSV(data.capturedData);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `defi_transactions_v3_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
    
    document.getElementById('status').textContent = `📊 Exported ${data.capturedData.length} transactions`;
    showMessage(`Successfully exported ${data.capturedData.length} transactions!`, 'success');
    
    console.log(`📊 Exported ${data.capturedData.length} transactions`);
    
  } catch (error) {
    console.error('❌ Export failed:', error);
    showMessage('Export failed: ' + error.message, 'error');
  }
}

// Clear data
function clearData() {
  data.capturedData = [];
  data.previewData = null;
  updateStats();
  document.getElementById('status').textContent = '🗑️ Data cleared! Ready for new selection.';
  showMessage('Data cleared successfully!', 'success');
  console.log('🗑️ Data cleared');
}

// Convert to CSV
function convertToCSV(data) {
  if (data.length === 0) return '';
  
  const headers = [
    'Platform', 'From Chain', 'From Address', 'From Token', 'From Amount',
    'To Chain', 'To Address', 'To Token', 'To Amount', 'Status', 'Time Ago', 'Timestamp'
  ];
  
  const csvRows = [headers.join(',')];
  
  for (const row of data) {
    const values = [
      row.platform,
      row.from_chain,
      row.from_address,
      row.from_token,
      row.from_amount,
      row.to_chain,
      row.to_address,
      row.to_token,
      row.to_amount,
      row.status,
      row.time_ago,
      row.timestamp
    ];
    
    const csvRow = values.map(value => {
      if (value === null || value === undefined) return '';
      
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    });
    
    csvRows.push(csvRow.join(','));
  }
  
  return csvRows.join('\n');
}

// Listen for extension icon click
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 Received message:', message);
  if (message.action === 'showUI') {
    console.log('🎯 Received showUI message');
    createUI();
    sendResponse({ success: true });
  }
});

// Send confirmation that content script is loaded
chrome.runtime.sendMessage({ 
  action: 'contentScriptLoaded', 
  tabId: sender.tab?.id || 'unknown',
  timestamp: Date.now()
}).catch(() => {
  // Ignore errors if background script isn't ready yet
});

// Also create UI when page loads (for testing)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, ready for DeFi Data Snatcher v3');
    
    // Test selection change event
    document.addEventListener('selectionchange', () => {
      console.log('🧪 Selection change event fired');
    });
  });
} else {
  console.log('📄 DOM already loaded, ready for DeFi Data Snatcher v3');
  
  // Test selection change event
  document.addEventListener('selectionchange', () => {
    console.log('🧪 Selection change event fired');
  });
}

// Additional safety check - remove any existing event listeners
window.addEventListener('beforeunload', () => {
  console.log('🧹 Cleaning up before unload');
  window.defiDataSnatcherV3Loaded = false;
});

console.log('✅ DeFi Data Snatcher v3 content script ready!');