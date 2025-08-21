# Centralized Configuration System

## 🎯 Overview

The ShapeShift Affiliate Tracker now uses a **centralized configuration system** that makes it easy to manage all addresses, contracts, and settings in one place. This eliminates the need to modify individual listener files when adding new contracts or addresses.

## 📁 File Structure

```
config/
├── shapeshift_config.yaml          # Main configuration file
shared/
├── config_loader.py                # Configuration loader utility
listeners/
├── csv_relay_listener.py           # Updated to use centralized config
├── csv_portals_listener.py         # Updated to use centralized config
├── csv_thorchain_listener.py       # Updated to use centralized config
└── csv_cowswap_listener.py         # Updated to use centralized config
```

## 🔧 Configuration File (`config/shapeshift_config.yaml`)

### API Keys and RPC Endpoints
```yaml
api:
  alchemy_api_key: "${ALCHEMY_API_KEY}"
  infura_api_key: "${INFURA_API_KEY}"
  coinmarketcap_api_key: "${COINMARKETCAP_API_KEY}"
```

### ShapeShift Affiliate Addresses
```yaml
shapeshift_affiliates:
  primary: "0x35339070f178dC4119732982C23F5a8d88D3f8a3"  # Main address
  relay: "0x35339070f178dC4119732982C23F5a8d88D3f8a3"    # Relay affiliate
  portals: "0x35339070f178dC4119732982C23F5a8d88D3f8a3"   # Portals affiliate
  thorchain: "0x35339070f178dC4119732982C23F5a8d88D3f8a3" # ThorChain affiliate
  cowswap: "0x35339070f178dC4119732982C23F5a8d88D3f8a3"   # CoW Swap affiliate
  
  # Alternative/legacy addresses found in data
  legacy_relay: "0x2905d7e4d048d29954f81b02171dd313f457a4a4"
  legacy_portals: "0x0840bba848e991cdcfbf2b71b8e1cb94fb72d6343ad4bb182f7ee1c48612221d"
  
  # Common variations (including text variations)
  variations:
    - "0x35339070f178dC4119732982C23F5a8d88D3f8a3"
    - "0x2905d7e4d048d29954f81b02171dd313f457a4a4"
    - "0x0840bba848e991cdcfbf2b71b8e1cb94fb72d6343ad4bb182f7ee1c48612221d"
    - "shapeshift"
    - "ss"
    - "ShapeShift"
    - "SHAPESHIFT"
```

### Chain Configurations
```yaml
chains:
  ethereum:
    name: "Ethereum Mainnet"
    chain_id: 1
    rpc_url: "https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}"
    start_block: 19000000
    chunk_size: 100
    delay: 0.5
    
  base:
    name: "Base"
    chain_id: 8453
    rpc_url: "https://base-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}"
    start_block: 32900000
    chunk_size: 100
    delay: 0.5
```

### Protocol-Specific Contract Addresses
```yaml
contracts:
  relay:
    ethereum: "0x542f021da7834c7f81531b48961d3f467f54b0f08"
    base: "0xF5042e6ffaC5a625D4E7848e0b01373D8eB9e222"
    base_alternative: "0xeeeeee9eC4769A09a76A83C7bC42b185872860eE"
    
    # Event signatures
    affiliate_fee_event: "0x4a25d94a55df505cf9da1f1649d0381e2613c3c83c6a0a3df055ae0e82f6e4d7"
    transfer_event: "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
```

### Data Storage Configuration
```yaml
storage:
  csv_directory: "csv_data"
  database_directory: "databases"
  backup_directory: "backups"
  
  file_patterns:
    portals: "portals_transactions.csv"
    relay: "relay_transactions.csv"
    thorchain: "thorchain_transactions.csv"
    cowswap: "cowswap_transactions.csv"
    block_tracker: "{protocol}_block_tracker.csv"
    consolidated: "consolidated_transactions.csv"
```

### Listener Configuration
```yaml
listeners:
  common:
    max_blocks_per_scan: 1000
    retry_attempts: 3
    retry_delay: 1.0
    rate_limit_delay: 0.5
    
  relay:
    chunk_size: 100
    delay: 0.5
    max_blocks: 1000
```

### Volume Thresholds
```yaml
thresholds:
  minimum_volume_usd: 0.0
  minimum_affiliate_fee_usd: 0.01
```

## 🚀 Using the Configuration in Listeners

### Basic Usage
```python
from shared.config_loader import get_config, get_shapeshift_address, get_contract_address

# Get global config instance
config = get_config()

# Get ShapeShift affiliate address
affiliate_address = get_shapeshift_address('relay')

# Get contract address for specific protocol and chain
relay_base = get_contract_address('relay', 'base')

# Get chain configuration
base_config = config.get_chain_config('base')
```

### Advanced Usage
```python
from shared.config_loader import (
    get_config, get_shapeshift_address, get_contract_address, 
    get_chain_config, get_storage_path, get_listener_config,
    get_event_signature, get_threshold
)

class CSVRelayListener:
    def __init__(self):
        self.config = get_config()
        
        # Get API key
        self.alchemy_api_key = self.config.get_alchemy_api_key()
        
        # Get all ShapeShift addresses
        self.shapeshift_affiliates = self.config.get_all_shapeshift_addresses()
        
        # Get storage paths
        self.csv_dir = self.config.get_storage_path('csv_directory')
        self.relay_csv = self.config.get_storage_path('file_pattern', 'relay')
        
        # Get listener configuration
        self.listener_config = self.config.get_listener_config('relay')
        self.chunk_size = self.listener_config.get('chunk_size', 100)
        
        # Get event signatures
        self.affiliate_fee_event = self.config.get_event_signature('relay', 'affiliate_fee')
        
        # Get thresholds
        self.min_volume_usd = self.config.get_threshold('minimum_volume_usd')
```

## ➕ Adding New Configuration

### Adding a New Chain
1. **Edit `config/shapeshift_config.yaml`**
```yaml
chains:
  # ... existing chains ...
  new_chain:
    name: "New Chain"
    chain_id: 12345
    rpc_url: "https://new-chain.g.alchemy.com/v2/${ALCHEMY_API_KEY}"
    start_block: 1000000
    chunk_size: 100
    delay: 0.5
```

2. **Add contract addresses**
```yaml
contracts:
  relay:
    # ... existing chains ...
    new_chain: "0x1234567890abcdef..."
```

### Adding a New Protocol
1. **Add protocol configuration**
```yaml
contracts:
  new_protocol:
    ethereum: "0x1234567890abcdef..."
    base: "0xabcdef1234567890..."
    
    # Event signatures
    swap_event: "0x1234567890abcdef..."
    fee_event: "0xabcdef1234567890..."
```

2. **Add listener settings**
```yaml
listeners:
  new_protocol:
    chunk_size: 100
    delay: 0.5
    max_blocks: 1000
```

3. **Add storage patterns**
```yaml
storage:
  file_patterns:
    new_protocol: "new_protocol_transactions.csv"
```

### Adding New ShapeShift Addresses
```yaml
shapeshift_affiliates:
  # ... existing addresses ...
  new_protocol: "0xnewaddress1234567890abcdef..."
  
  variations:
    # ... existing variations ...
    - "0xnewaddress1234567890abcdef..."
    - "newshapeshift"
    - "nss"
```

## 🔍 Configuration Testing

### Run Configuration Tests
```bash
python test_centralized_config.py
```

### Test Individual Components
```bash
python shared/config_loader.py
```

## 📝 Benefits of Centralized Configuration

1. **Single Source of Truth**: All addresses and settings in one file
2. **Easy Updates**: Add new contracts/addresses without touching listener code
3. **Consistency**: All listeners use the same configuration
4. **Environment Variables**: Support for `.env` file integration
5. **Validation**: Built-in configuration validation and error handling
6. **Flexibility**: Easy to add new chains, protocols, and addresses

## 🚨 Important Notes

1. **Environment Variables**: The config file uses `${VARIABLE_NAME}` syntax for environment variables
2. **File Paths**: Always use relative paths from the project root
3. **Validation**: The config loader validates configuration on startup
4. **Reloading**: Use `config.reload_config()` to reload configuration without restarting
5. **Backup**: Keep backups of your configuration file

## 🔧 Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Ensure `config/shapeshift_config.yaml` exists
   - Check file permissions

2. **"Invalid YAML"**
   - Validate YAML syntax using online YAML validator
   - Check for proper indentation

3. **"Environment variable not found"**
   - Ensure `.env` file exists and contains required variables
   - Check variable names match exactly

4. **"Import error"**
   - Ensure `shared/` directory is in Python path
   - Check for circular imports

### Debug Configuration
```python
from shared.config_loader import get_config

config = get_config()
summary = config.get_config_summary()
print(summary)
```

## 📚 Example Listener Implementation

See `csv_relay_listener.py` for a complete example of how to use the centralized configuration system in a listener.

---

**🎉 The centralized configuration system makes it easy to manage all your ShapeShift affiliate tracking settings in one place!**
