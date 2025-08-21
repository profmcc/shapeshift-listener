# 🎯 ButterSwap Listener

## 📋 **Current Status**
**Status**: PARTIALLY WORKING  
**Last Tested**: August 20, 2025  
**Classification**: Technically functional but no ShapeShift affiliate transactions detected

## 📁 **Contents**
- `butterswap_listener.py` - Blockchain-based listener for ButterSwap
- `butterswap_web_scraper.py` - Web scraper for ButterSwap explorer
- `butterswap_transactions.db` - Database for blockchain listener
- `butterswap_web_transactions.db` - Database for web scraper
- `BUTTERSWAP_HANDOFF_PARTIALLY_WORKING.md` - Comprehensive testing documentation

## 🔍 **What Works**
- ✅ Multi-chain connectivity (6/7 chains) - blockchain listener
- ✅ Web explorer connection and navigation
- ✅ Transaction element detection (32 found)
- ✅ Address copy-paste mechanism
- ✅ Database initialization and management
- ✅ Affiliate detection logic implementation

## 🚨 **What Doesn't Work**
- ❌ No ButterSwap events detected in recent blockchain blocks
- ❌ No ShapeShift affiliate transactions found (web scraper)
- ❌ Both databases remain empty
- ❌ Avalanche chain connection fails
- ❌ BSC hits rate limits

## 🎯 **Key Features**

### **Blockchain Listener**
- **Supported Chains**: Ethereum, Polygon, Optimism, Arbitrum, Base, BSC
- **Event Types**: Swap events, affiliate fee events
- **Block Scanning**: Real-time block monitoring
- **Database**: SQLite with proper indexing

### **Web Scraper**
- **Explorer**: https://explorer.butterswap.io/en
- **Multi-Chain Support**: 7 blockchain networks
- **Address Extraction**: Copy-paste for full Ethereum addresses
- **Affiliate Filtering**: Only saves ShapeShift affiliate transactions
- **Transaction Parsing**: Extracts details from explorer interface

## 🚫 **Redundancy Prevention**
This folder contains comprehensive documentation of what was tested and what didn't work. **DO NOT** retest:
- Basic connectivity (except Avalanche)
- Small/medium block ranges
- Web scraper connection and navigation
- Address extraction mechanisms
- Database operations
- Current affiliate detection logic

## 🚀 **Next Steps**
See `BUTTERSWAP_HANDOFF_PARTIALLY_WORKING.md` for detailed:
- What TO test in future
- Root cause analysis
- Technical implementation details
- Testing commands used
- Alternative detection methods

## 🔗 **Additional Resources**
- **ButterSwap Explorer**: https://explorer.butterswap.io/en
- **Original Summary**: `BUTTERSWAP_WEB_SCRAPER_SUMMARY.md` (in original project)
- **Dependencies**: `scripts/requirements_butterswap_scraper.txt`

---
**Status**: Ready for future investigation, no immediate action needed
