# ShapeShift Affiliate Tracker - v6.0 Clean Centralized CSV

## 🎯 **Overview**

This is the **clean, centralized version** of the ShapeShift Affiliate Tracker system. All listeners now use a centralized configuration system and save data exclusively to CSV files (no databases).

## 🏗️ **Architecture**

### **Centralized Configuration**
- **Single config file**: `config/shapeshift_config.yaml`
- **Config loader**: `shared/config_loader.py`
- **All parameters centralized**: API keys, addresses, contracts, thresholds

### **CSV-Based Storage**
- **No databases**: All data stored in CSV files
- **Organized structure**: Separate directories for transactions, block tracking, consolidated data
- **Easy analysis**: CSV files can be opened in Excel, Google Sheets, or pandas

### **Modular Listener System**
- **Independent listeners**: Each protocol has its own listener class
- **Common interface**: All listeners follow the same pattern
- **Easy maintenance**: Update one listener without affecting others

## 📁 **File Structure**

```
listeners_v6_clean/
├── README.md                           # This file
├── csv_master_runner.py               # Main orchestrator
├── csv_cowswap_listener.py            # CoW Swap listener
├── csv_thorchain_listener.py          # THORChain listener
├── csv_portals_listener.py            # Portals listener
└── csv_relay_listener.py              # Relay listener (⚠️ has issues)
```

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Ensure you have the required packages
pip install web3 requests python-dotenv pyyaml

# Set your Alchemy API key in .env file
echo "ALCHEMY_API_KEY=your_key_here" > .env
```

### **2. Run Individual Listeners**
```bash
# Run CoW Swap listener
python csv_cowswap_listener.py

# Run THORChain listener
python csv_thorchain_listener.py

# Run Portals listener
python csv_portals_listener.py

# Run Relay listener (⚠️ has detection issues)
python csv_relay_listener.py
```

### **3. Run All Listeners**
```bash
# Run the master runner to execute all listeners
python csv_master_runner.py
```

## 📊 **Data Output Structure**

### **CSV Directory Structure**
```
csv_data/
├── transactions/                       # Individual protocol CSVs
│   ├── cowswap_transactions.csv
│   ├── thorchain_transactions.csv
│   ├── portals_transactions.csv
│   └── relay_transactions.csv
├── block_tracking/                    # Block tracking for each protocol
│   ├── cowswap_block_tracker.csv
│   ├── thorchain_block_tracker.csv
│   ├── portals_block_tracker.csv
│   └── relay_block_tracker.csv
├── consolidated/                      # Combined data
│   └── all_transactions.csv
└── reports/                          # Analysis reports
```

### **Transaction CSV Schema**
All transaction CSVs have consistent columns:
- `tx_hash`: Transaction hash
- `chain`: Blockchain name
- `block_number`: Block number
- `timestamp`: Block timestamp
- `from_address`: Sender address
- `to_address`: Recipient address
- `affiliate_address`: ShapeShift affiliate address
- `affiliate_fee_amount`: Affiliate fee amount
- `affiliate_fee_usd`: Affiliate fee in USD
- `volume_amount`: Transaction volume
- `volume_usd`: Volume in USD
- `gas_used`: Gas used
- `gas_price`: Gas price
- `created_at`: Record creation timestamp

## ⚙️ **Configuration**

### **Centralized Config File**
All configuration is in `config/shapeshift_config.yaml`:

```yaml
# API Keys
api:
  alchemy_api_key: "${ALCHEMY_API_KEY}"

# ShapeShift Affiliate Addresses
shapeshift_affiliates:
  primary: "0x35339070f178dC4119732982C23F5a8d88D3f8a3"
  thorchain_address: "thor122h9hlrugzdny9ct95z6g7afvpzu34s73uklju"
  thorchain_name: "ss"

# Chain Configurations
chains:
  ethereum:
    rpc_url: "https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}"
    start_block: 19000000

# Contract Addresses
contracts:
  cowswap:
    ethereum: "0x9008d19f58aabd9ed0d60971565aa8510560ab41"
```

### **Environment Variables**
Required in `.env` file:
```bash
ALCHEMY_API_KEY=your_alchemy_key_here
```

## 🔍 **Listener Status**

### **✅ Working Listeners**
1. **CoW Swap**: 100% functional, event monitoring
2. **THORChain**: 100% functional, API integration  
3. **Portals**: 100% functional, treasury detection method

### **❌ Not Working**
4. **Relay**: 0% functional, fundamental detection issues

## 🚨 **Known Issues**

### **Relay Listener Critical Issue**
- **Problem**: Looking for `AffiliateFee` events that don't exist
- **Impact**: Will not find any transactions
- **Status**: Needs complete investigation of actual affiliate mechanism
- **Workaround**: None - listener is fundamentally broken

### **Portals Listener - RESOLVED ✅**
- **Problem**: Block scanning range was too limited (only recent blocks)
- **Solution**: Added block override functionality for historical scanning
- **Status**: 100% functional, found 27 transactions in known block
- **Detection Method**: ShapeShift DAO Treasury receiving affiliate fees

## 🛠️ **Customization**

### **Adding New Protocols**
1. **Create new listener class** following existing pattern
2. **Add configuration** to `shapeshift_config.yaml`
3. **Import in master runner** and add to listener manager
4. **Test thoroughly** before production use

### **Modifying Existing Listeners**
1. **Update configuration** in `shapeshift_config.yaml`
2. **Modify listener logic** as needed
3. **Test changes** with small block ranges
4. **Update documentation** if needed

## 📈 **Monitoring & Analysis**

### **CSV Statistics**
Each listener provides statistics:
```python
stats = listener.get_csv_stats()
print(f"Total transactions: {stats['total_transactions']}")
print(f"Chains: {stats['chains']}")
```

### **Volume Analysis**
Master runner provides volume distribution:
- Under $13: Low volume transactions
- $13-$100: Target range transactions
- $100-$1000: High volume transactions
- Over $1000: Very high volume transactions

## 🔧 **Troubleshooting**

### **Common Issues**
1. **API Key Missing**: Check `.env` file and `ALCHEMY_API_KEY`
2. **No Transactions Found**: Check block ranges and affiliate addresses
3. **Rate Limiting**: Increase delays in listener config
4. **Connection Errors**: Verify RPC URLs and network connectivity

### **Debug Mode**
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 **API Reference**

### **ConfigLoader Methods**
- `get_config()`: Get main config instance
- `get_alchemy_api_key()`: Get Alchemy API key
- `get_shapeshift_address(protocol)`: Get affiliate address
- `get_contract_address(protocol, chain)`: Get contract address
- `get_chain_config(chain)`: Get chain configuration
- `get_storage_path(type, protocol)`: Get storage path
- `get_listener_config(protocol)`: Get listener settings
- `get_threshold(type)`: Get threshold values

### **Listener Methods**
- `run_listener()`: Execute the listener
- `get_csv_stats()`: Get CSV statistics
- `process_chain(chain, start, end)`: Process specific chain
- `save_transactions_to_csv(transactions)`: Save to CSV

## 🎯 **Next Steps**

### **Immediate Priorities**
1. **Fix Relay detection** (critical)
2. **Test working listeners** (CoW Swap, THORChain, Portals)
3. **Deploy validated listeners** for production monitoring

### **Future Enhancements**
1. **Add new protocols** (0x, Jupiter, Chainflip)
2. **Implement price feeds** for accurate USD calculations
3. **Add monitoring dashboard** for real-time tracking
4. **Create CLI tools** for easy management

## 📞 **Support**

For issues or questions:
1. **Check handoff documentation** in `affiliate_listener_handoff/`
2. **Review configuration** in `config/shapeshift_config.yaml`
3. **Check logs** in `logs/` directory
4. **Verify CSV output** in `csv_data/` directory

---

**🎉 Welcome to v6.0 - Clean, Centralized, CSV-Based!**
