# ButterSwap Affiliate Fee Listener

A comprehensive listener for tracking ShapeShift affiliate fees from ButterSwap trades across multiple EVM chains.

## 🎯 Features

- **Multi-chain Support**: Tracks ButterSwap activity on Ethereum, Polygon, Optimism, Arbitrum, Base, Avalanche, and BSC
- **Real-time Monitoring**: Fetches swap, mint, and burn events from ButterSwap routers and factories
- **Affiliate Detection**: Identifies ShapeShift affiliate fee transfers across all supported chains
- **Comprehensive Database**: Stores detailed transaction data with USD value calculations
- **Block Tracking**: Prevents duplicate processing with intelligent block tracking
- **Error Handling**: Robust error handling and logging for production use

## 📊 Supported Chains

| Chain | Router Address | Factory Address | RPC Provider |
|-------|----------------|-----------------|--------------|
| Ethereum | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | Alchemy/Infura |
| Polygon | `0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff` | `0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32` | Alchemy/Infura |
| Optimism | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | Alchemy/Infura |
| Arbitrum | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | Alchemy/Infura |
| Base | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | Alchemy/Infura |
| Avalanche | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | Alchemy/Infura |
| BSC | `0x10ED43C718714eb63d5aA57B78B54704E256024E` | `0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73` | Binance RPC |

## 🚀 Usage

### Basic Usage
```bash
# Run listener with default settings (2000 blocks)
python listeners/butterswap_listener.py

# Fetch specific number of blocks
python listeners/butterswap_listener.py --blocks 5000
```

### Integration with Master Runner
```bash
# Run all listeners including ButterSwap
python listeners/master_runner.py

# Run only ButterSwap listener
python listeners/master_runner.py --blocks 2000
```

## 📈 Database Structure

The listener creates a comprehensive database at `databases/butterswap_transactions.db` with the following schema:

### `butterswap_transactions` table
- `id`: Primary key
- `chain`: Chain name (Ethereum, Polygon, etc.)
- `tx_hash`: Transaction hash
- `block_number`: Block number
- `block_timestamp`: Block timestamp
- `event_type`: Event type (swap, mint, burn)
- `owner`: Transaction owner
- `sell_token`: Token being sold
- `buy_token`: Token being bought
- `sell_amount`: Amount sold
- `buy_amount`: Amount bought
- `fee_amount`: Fee amount
- `order_uid`: Order unique identifier
- `app_data`: Application data
- `affiliate_fee_usd`: Affiliate fee in USD
- `volume_usd`: Trade volume in USD
- `sell_token_name`: Human-readable sell token name
- `buy_token_name`: Human-readable buy token name
- `created_at`: Record creation timestamp

## 🔧 Configuration

### Environment Variables
```bash
# Required for Alchemy RPC (preferred)
ALCHEMY_API_KEY=your_alchemy_api_key

# Fallback for Infura RPC
INFURA_API_KEY=your_infura_api_key
```

### ShapeShift Affiliate Addresses
The listener tracks affiliate fees sent to these ShapeShift addresses:

- **Ethereum**: `0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be`
- **Polygon**: `0xB5F944600785724e31Edb90F9DFa16dBF01Af000`
- **Optimism**: `0x6268d07327f4fb7380732dc6d63d95F88c0E083b`
- **Arbitrum**: `0x38276553F8fbf2A027D901F8be45f00373d8Dd48`
- **Base**: `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502`
- **Avalanche**: `0x74d63F31C2335b5b3BA7ad2812357672b2624cEd`
- **BSC**: `0x8b92b1698b57bEDF2142297e9397875ADBb2297E`

## 📊 Event Detection

### Supported Events
- **Swap Events**: Tracks token swaps with affiliate fee detection
- **Mint Events**: Tracks liquidity additions
- **Burn Events**: Tracks liquidity removals
- **ERC-20 Transfers**: Detects affiliate fee transfers

### Event Signatures
```python
event_signatures = {
    'swap': '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822',
    'mint': '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f',
    'burn': '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496',
    'erc20_transfer': '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
}
```

## 🔍 Affiliate Fee Detection

The listener uses a sophisticated approach to detect ShapeShift affiliate fees:

1. **Event Monitoring**: Scans all ButterSwap router and factory events
2. **Transfer Detection**: Identifies ERC-20 transfers to ShapeShift affiliate addresses
3. **Transaction Analysis**: Analyzes transaction receipts for affiliate involvement
4. **Fee Calculation**: Calculates USD values for affiliate fees and trade volumes

## 📈 Example Output

```
🚀 Starting ButterSwap affiliate fee listener

🔍 Processing ethereum...
🔍 Scanning Ethereum ButterSwap blocks 19500000 to 19502000
   📊 Processed 10000 blocks...
   ✅ Found ShapeShift ButterSwap swap: 0x1234567890abcdef...
💾 Saved 15 ButterSwap events to database

🔍 Processing polygon...
🔍 Scanning Polygon ButterSwap blocks 45000000 to 45002000
   ✅ Found ShapeShift ButterSwap swap: 0xabcdef1234567890...
💾 Saved 8 ButterSwap events to database

✅ ButterSwap listener completed! Found 23 total events

📊 ButterSwap Database Statistics:
   Total transactions: 23
   Swap events: 20
   Unique chains: 2
   Total affiliate fees: $45.67
   Total volume: $12,345.67
```

## 🔗 Integration

### Master Runner Integration
The ButterSwap listener is fully integrated with the master runner system:

```python
# In master_runner.py
self.listeners = {
    'relay': RelayListener(),
    'portals': PortalsListener(),
    'thorchain': THORChainListener(),
    'chainflip': ChainflipBrokerListener(),
    'cowswap': CowSwapDuneListener(),
    'zerox': ZeroXListener(),
    'butterswap': ButterSwapListener(),  # ✅ Integrated
}
```

### Database Consolidation
ButterSwap transactions are automatically consolidated into the comprehensive database:

```python
consolidation_map = {
    # ... other protocols
    'butterswap': {
        'source_db': 'databases/butterswap_transactions.db',
        'source_table': 'butterswap_transactions',
        'protocol': 'ButterSwap'
    }
}
```

## 🛠️ Error Handling

The listener includes comprehensive error handling:

- **RPC Connection Failures**: Graceful fallback and retry logic
- **Event Parsing Errors**: Detailed logging for debugging
- **Database Errors**: Transaction rollback and recovery
- **Rate Limiting**: Configurable delays between requests

## 📝 Logging

All activity is logged with detailed information:

- **INFO**: Normal operation and successful events
- **WARNING**: Non-critical issues and fallbacks
- **ERROR**: Critical errors and failures
- **DEBUG**: Detailed debugging information

## 🔧 Performance Optimization

- **Chunked Processing**: Configurable block chunk sizes per chain
- **Rate Limiting**: Adjustable delays to prevent RPC rate limiting
- **Block Tracking**: Prevents duplicate processing of scanned blocks
- **Database Indexing**: Optimized queries with proper indexing

## 🚨 Monitoring

The listener is designed for production monitoring:

- **Real-time Processing**: Continuous block scanning
- **Comprehensive Logging**: Detailed operation logs
- **Database Statistics**: Regular performance reporting
- **Error Recovery**: Automatic retry and recovery mechanisms

## 📋 Dependencies

- `web3`: Ethereum interaction
- `eth_abi`: Event decoding
- `sqlite3`: Database operations
- `requests`: API calls (if needed)
- `shared.block_tracker`: Block tracking functionality

## 🎯 Use Cases

- **Affiliate Fee Tracking**: Monitor ShapeShift affiliate revenue from ButterSwap
- **Volume Analysis**: Track trading volumes across multiple chains
- **Performance Monitoring**: Monitor ButterSwap protocol performance
- **Cross-chain Analytics**: Analyze ButterSwap activity across all supported chains

## 🔗 Related Documentation

- [Master Runner Documentation](README_master_runner.md)
- [Database Schema Documentation](README_database_schema.md)
- [Affiliate Fee Tracking Overview](README_affiliate_fees.md)


