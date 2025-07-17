// Background service worker for ViewBlock Data Capture extension

chrome.runtime.onInstalled.addListener(function() {
  console.log('ViewBlock Data Capture extension installed');
  
  // Initialize storage
  chrome.storage.local.set({
    capturedData: [],
    stats: {
      transactions: 0,
      pages: 0
    }
  });
});

// Handle download completion
chrome.downloads.onChanged.addListener(function(downloadDelta) {
  if (downloadDelta.state && downloadDelta.state.current === 'complete') {
    console.log('Download completed:', downloadDelta.id);
  }
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'clearData') {
    chrome.storage.local.clear(function() {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (request.action === 'getStats') {
    chrome.storage.local.get(['stats'], function(result) {
      sendResponse({ stats: result.stats || { transactions: 0, pages: 0 } });
    });
    return true;
  }
}); 