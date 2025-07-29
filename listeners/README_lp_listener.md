# LP Listener - WETH/FOX Liquidity Pool Tracker

A dedicated listener for tracking WETH/FOX liquidity pool events across multiple chains.

## 🎯 Features

- **Multi-chain Support**: Tracks pools on Ethereum Mainnet and Arbitrum
- **Real-time Monitoring**: Fetches mint, burn, and swap events
- **Liquidity Analysis**: Calculates impact of liquidity removals
- **DAO Tracking**: Monitors ShapeShift DAO's LP token ownership
- **Price Integration**: Real-time token pricing via CoinGecko API
- **Comprehensive Reporting**: Detailed analysis and visualizations

## 📊 Tracked Pools

| Chain | Pool Address | DAO LP Tokens |
|-------|--------------|---------------|
| Ethereum | `0x470e8de2eBaef52014A47Cb5E6aF86884947F08c` | 74,219.8483 |
| Arbitrum | `0x5f6ce0ca13b87bd738519545d3e018e70e339c24` | 4,414.3394 |

## 🚀 Usage

### Basic Usage
```bash
# Run listener with default settings (1000 blocks)
python listeners/lp_listener.py

# Fetch specific number of blocks
python listeners/lp_listener.py --blocks 2000

# Analyze specific pool only
python listeners/lp_listener.py --pool ethereum

# Run analysis only (no event fetching)
python listeners/lp_listener.py --analysis-only
```

### Advanced Usage
```bash
# Fetch last 5000 blocks and analyze
python listeners/lp_listener.py --blocks 5000 --limit 200

# Analyze only Arbitrum pool
python listeners/lp_listener.py --pool arbitrum --analysis-only
```

## 📈 Output

The listener provides comprehensive analysis including:

### Pool Reserves
- Current WETH and FOX amounts
- USD values with real-time pricing
- Total pool liquidity

### DAO Ownership
- DAO's LP token percentage
- USD value of DAO's position
- Total LP supply tracking

### Liquidity Analysis
- Total liquidity removed via burns
- Original vs current pool size
- Reduction percentage
- Burn event history

## 🗄️ Database Structure

Each pool gets its own database with tables:

### `mint` table
- `block_number`, `tx_hash`, `log_index`
- `sender`, `amount0`, `amount1`, `timestamp`

### `burn` table  
- `block_number`, `tx_hash`, `log_index`
- `sender`, `amount0`, `amount1`, `to_addr`, `timestamp`

### `swap` table
- `block_number`, `tx_hash`, `log_index`
- `sender`, `amount0In`, `amount1In`, `amount0Out`, `amount1Out`, `to_addr`, `timestamp`

## 📊 Example Output

```
============================================================
ANALYZING ETHEREUM WETH/FOX
============================================================

Current Pool Reserves:
  WETH: 123.4567 ($432,098.45)
  FOX: 2,847,392.12 ($427,108.82)
  Total: $859,207.27

DAO Ownership:
  DAO LP tokens: 74,219.85
  Total LP supply: 1,234,567.89
  DAO percentage: 6.01%
  DAO USD value: $51,638.36

Liquidity Analysis:
  Total removed: $45,678.90
  Original total: $904,886.17
  Current total: $859,207.27
  Reduction: 5.0%
  Burn events: 12
```

## 🔧 Configuration

The listener uses these default settings:

- **RPC URLs**: Infura endpoints for Ethereum and Arbitrum
- **Token Addresses**: WETH and FOX contract addresses per chain
- **DAO LP Tokens**: Hardcoded amounts for each pool
- **Database Paths**: `databases/{chain}_weth_fox_events.db`

## 📝 Logging

All activity is logged to:
- Console output
- `lp_listener.log` file

## 🎨 Visualizations

The original debug scripts include matplotlib visualizations for:
- Liquidity removals over time
- Cumulative liquidity removed
- Pool liquidity distribution
- DAO ownership charts

## 🔗 Dependencies

- `web3`: Ethereum interaction
- `pandas`: Data analysis
- `requests`: API calls
- `eth_abi`: Event decoding
- `matplotlib`: Visualizations (optional)

## 🚨 Error Handling

- Graceful fallback to hardcoded prices if CoinGecko API fails
- Comprehensive error logging
- Continues processing if one pool fails
- Automatic database table creation

## 📋 Monitoring

The listener is designed for:
- **Real-time monitoring** of liquidity changes
- **Historical analysis** of pool activity
- **DAO position tracking** across multiple chains
- **Liquidity impact assessment** for governance decisions 