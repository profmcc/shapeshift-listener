// DeFi Data Snatcher v4 - Popup Script
console.log('🚀 DeFi Data Snatcher v4 popup script loaded!');

// Get current active tab
async function getCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

// Send message to content script
async function sendMessageToContentScript(action) {
  try {
    const tab = await getCurrentTab();
    
    // Just send message directly - no content script injection
    const response = await chrome.tabs.sendMessage(tab.id, { action });
    console.log('✅ Message sent:', action, response);
    
  } catch (error) {
    console.error('❌ Error sending message:', error);
    
    // Show error to user
    showMessage('Error: Could not communicate with page. Make sure you are on a valid website.', 'error');
  }
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
    z-index: 10000;
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

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 Popup DOM loaded for v4');
  
  // Start table selection button
  document.getElementById('captureBtn').addEventListener('click', async () => {
    console.log('🎯 Start table selection clicked (v4)');
    
    // Close popup
    window.close();
    
    // Send message to content script
    await sendMessageToContentScript('showUI');
  });
  
  // Export data button
  document.getElementById('exportBtn').addEventListener('click', async () => {
    console.log('📊 Export data clicked (v4)');
    
    // Close popup
    window.close();
    
    // Send message to content script
    await sendMessageToContentScript('exportData');
  });
  
  // Clear data button
  document.getElementById('clearBtn').addEventListener('click', async () => {
    console.log('🗑️ Clear data clicked (v4)');
    
    // Close popup
    window.close();
    
    // Send message to content script
    await sendMessageToContentScript('clearData');
  });
});

console.log('✅ DeFi Data Snatcher v4 popup script ready!');
