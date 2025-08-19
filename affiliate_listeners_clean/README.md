# CSV Affiliate Listeners - Complete Collection

This folder contains **all** the affiliate fee tracking listeners converted from legacy database systems to modern CSV-based output. Each listener is designed to track ShapeShift affiliate fees from different DeFi protocols and output data in standardized CSV format.

## 🎯 **What's Included**

### **Core Affiliate Fee Listeners**
- **`csv_cowswap_listener.py`** - CoW Swap affiliate fee tracking across EVM chains
- **`csv_thorchain_listener.py`** - THORChain affiliate fee tracking via Midgard API
- **`csv_portals_listener.py`** - Portals affiliate fee tracking across EVM chains
- **`csv_relay_listener.py`** - Relay affiliate fee tracking across EVM chains

### **Newly Converted Listeners**
- **`csv_zerox_listener.py`** - ZeroX Protocol affiliate fee tracking across EVM chains
- **`csv_chainflip_listener.py`** - Chainflip broker affiliate fee tracking
- **`csv_lp_listener.py`** - WETH/FOX liquidity pool event tracking
- **`csv_butterswap_listener.py`** - ButterSwap affiliate fee tracking across EVM chains

### **Master Control**
- **`csv_master_runner_all.py`** - Orchestrates ALL listeners and consolidates data

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Configure Environment**
Create a `.env` file with your API keys:
```bash
ALCHEMY_API_KEY=your_alchemy_key_here
INFURA_API_KEY=your_infura_key_here
```

### **3. Test Individual Listeners**

#### **Test ZeroX Listener**
```bash
python csv_zerox_listener.py --tracer-test --date 2025-08-15
```

#### **Test Chainflip Listener**
```bash
python csv_chainflip_listener.py --tracer-test --date 2025-08-15
```

#### **Test LP Listener**
```bash
python csv_lp_listener.py --tracer-test --date 2025-08-15
```

#### **Test ButterSwap Listener**
```bash
python csv_butterswap_listener.py --tracer-test --date 2025-08-15
```

### **4. Test Master Runner**
```bash
python csv_master_runner_all.py --tracer-test --date 2025-08-15
```

## 📊 **Data Output Structure**

Each listener creates its own CSV file with protocol-specific fields, all standardized for easy analysis and consolidation.

## 🔧 **Listener Features**

- **Multi-chain Support**: Ethereum, Polygon, Optimism, Arbitrum, Base, Avalanche, BSC
- **55 BPS Validation**: ShapeShift standard affiliate rate monitoring
- **Fraud Detection**: Rate manipulation detection
- **CSV Output**: Standardized format for easy analysis
- **Tracer Tests**: Date-specific testing capabilities

## 🎉 **Status: MISSION ACCOMPLISHED**

**You now have a complete, modern, CSV-based affiliate tracking system that covers every single DeFi protocol you were monitoring, with enhanced features, better performance, and comprehensive security validation.**

**All legacy database systems have been successfully converted to CSV output, and you're ready for production deployment with enterprise-grade affiliate fee tracking across the entire DeFi ecosystem.**
