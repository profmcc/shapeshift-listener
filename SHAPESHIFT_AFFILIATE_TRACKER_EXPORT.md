# ShapeShift Affiliate Fee Tracker - Complete System Export

## 🎯 Project Overview
Multi-chain affiliate fee tracking system for ShapeShift across DeFi protocols including Relay, Portals, THORChain, CowSwap, Chainflip, and 0x Protocol.

## 🔗 Supported Chains & RPC URLs

### Primary Chains
- **Ethereum**: `https://mainnet.infura.io/v3/{INFURA_API_KEY}`
- **Polygon**: `https://polygon-mainnet.infura.io/v3/{INFURA_API_KEY}`
- **Optimism**: `https://optimism-mainnet.infura.io/v3/{INFURA_API_KEY}`
- **Arbitrum**: `https://arbitrum-mainnet.infura.io/v3/{INFURA_API_KEY}`
- **Base**: `https://base-mainnet.infura.io/v3/{INFURA_API_KEY}`
- **Avalanche**: `https://avalanche-mainnet.infura.io/v3/{INFURA_API_KEY}`
- **BSC**: `https://bsc-dataseed.binance.org/`

### Alternative RPC URLs (Alchemy)
- **Ethereum**: `https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}`
- **Polygon**: `https://polygon-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}`
- **Optimism**: `https://opt-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}`
- **Arbitrum**: `https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}`
- **Base**: `https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}`

## 🏢 ShapeShift Affiliate Addresses

### Primary Affiliate Address
```
0x2905d7e4d048d29954f81b02171dd313f457a4a4
```

### Protocol-Specific Addresses
- **Relay**: `0x2905d7e4d048d29954f81b02171dd313f457a4a4`
- **Portals**: `0x2905d7e4d048d29954f81b02171dd313f457a4a4`
- **CowSwap**: 
  - Ethereum: `0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be`
  - Polygon: `0xB5F944600785724e31Edb90F9DFa16dBF01Af000`
  - Optimism: `0x6268d07327f4fb7380732dc6d63d95F88c0E083b`
  - Arbitrum: `0x38276553F8fbf2A027D901F8be45f00373d8Dd48`
  - Base: `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502`
- **0x Protocol**: Same as CowSwap addresses
- **THORChain**: `thor1z63f3mzwv3gpgmh8wvxcsyy3h9q2z3y5m6c3z3`
- **Chainflip**: 
  - `cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi`
  - `cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8`

## 📊 Database Schema

### Comprehensive Database (Main)
```sql
CREATE TABLE comprehensive_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol TEXT NOT NULL,
    chain TEXT NOT NULL,
    tx_hash TEXT NOT NULL,
    block_number INTEGER,
    timestamp INTEGER NOT NULL,
    from_asset TEXT,
    to_asset TEXT,
    from_amount REAL,
    to_amount REAL,
    from_amount_usd REAL,
    to_amount_usd REAL,
    volume_usd REAL,
    affiliate_fee_amount REAL,
    affiliate_fee_usd REAL,
    affiliate_fee_asset TEXT,
    affiliate_address TEXT,
    sender_address TEXT,
    recipient_address TEXT,
    event_type TEXT,
    raw_data TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(protocol, tx_hash, chain)
);
```

### Protocol-Specific Tables

#### Relay
```sql
CREATE TABLE relay_affiliate_fees (
    tx_hash TEXT,
    block_number INTEGER,
    chain TEXT,
    affiliate_address TEXT,
    affiliate_fee_amount TEXT,
    affiliate_fee_token TEXT,
    from_token TEXT,
    to_token TEXT,
    from_amount TEXT,
    to_amount TEXT,
    volume_usd REAL,
    affiliate_fee_usd REAL,
    timestamp INTEGER,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
```

#### Portals
```sql
CREATE TABLE portals_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain TEXT NOT NULL,
    tx_hash TEXT NOT NULL,
    block_number INTEGER NOT NULL,
    block_timestamp INTEGER NOT NULL,
    input_token TEXT,
    output_token TEXT,
    input_amount TEXT,
    output_amount TEXT,
    affiliate_token TEXT,
    affiliate_amount TEXT,
    affiliate_fee_usd REAL,
    volume_usd REAL,
    input_token_name TEXT,
    output_token_name TEXT,
    affiliate_token_name TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(tx_hash, chain)
);
```

## 🔍 Working Detection Logic

### 1. Relay Protocol Detection
```python
def _process_transaction(self, w3: Web3, tx_hash: str, chain_name: str) -> List[Tuple]:
    """Process transaction to find affiliate fees"""
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        # Look for ERC-20 transfers TO the affiliate address
        affiliate_fees = []
        for log in receipt['logs']:
            if len(log['topics']) >= 3:
                # ERC-20 Transfer event signature
                if log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    to_address = '0x' + log['topics'][2][-40:].hex()
                    
                    if to_address.lower() == self.affiliate_address.lower():
                        # Extract amount from data
                        amount = int(log['data'].hex(), 16)
                        token_address = log['address']
                        
                        affiliate_fees.append({
                            'amount': amount,
                            'token': token_address,
                            'from_token': None,
                            'to_token': token_address,
                            'from_amount': None,
                            'to_amount': amount
                        })
        
        return affiliate_fees
    except Exception as e:
        logger.error(f"Error processing transaction {tx_hash}: {e}")
        return []
```

### 2. Portals Protocol Detection
```python
def check_affiliate_involvement(self, receipt: Dict, affiliate_address: str) -> bool:
    """Check if affiliate address is involved in transaction"""
    for log in receipt['logs']:
        for topic in log['topics']:
            if affiliate_address.lower() in topic.hex().lower():
                return True
    return False

def detect_portals_tokens(self, w3: Web3, receipt: Dict, chain_config: Dict) -> Dict:
    """Detect input, output, and affiliate tokens from transaction"""
    tokens = {
        'input_token': None,
        'output_token': None,
        'affiliate_token': None,
        'input_amount': None,
        'output_amount': None,
        'affiliate_amount': None
    }
    
    # Look for ERC-20 transfers
    for log in receipt['logs']:
        if len(log['topics']) >= 3:
            if log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                from_addr = '0x' + log['topics'][1][-40:].hex()
                to_addr = '0x' + log['topics'][2][-40:].hex()
                amount = int(log['data'].hex(), 16)
                token = log['address']
                
                # Determine if this is affiliate-related
                if to_addr.lower() == self.affiliate_address.lower():
                    tokens['affiliate_token'] = token
                    tokens['affiliate_amount'] = amount
                elif from_addr.lower() == self.affiliate_address.lower():
                    tokens['output_token'] = token
                    tokens['output_amount'] = amount
                else:
                    # Assume first significant transfer is input
                    if not tokens['input_token']:
                        tokens['input_token'] = token
                        tokens['input_amount'] = amount
    
    return tokens
```

### 3. THORChain Detection
```python
def process_thorchain_action(self, action: Dict) -> Optional[Dict]:
    """Process THORChain action for affiliate fees"""
    if action.get('type') != 'SWAP':
        return None
    
    # Calculate affiliate fee (55 bps = 0.55%)
    affiliate_fee_percentage = 0.0055
    usd_value = float(action.get('in', {}).get('coins', [{}])[0].get('amountUSD', 0))
    affiliate_fee = usd_value * affiliate_fee_percentage
    
    return {
        'tx_hash': action.get('in', {}).get('txID', ''),
        'from_asset': action.get('in', {}).get('coins', [{}])[0].get('asset', ''),
        'to_asset': action.get('out', {}).get('coins', [{}])[0].get('asset', ''),
        'from_amount': action.get('in', {}).get('coins', [{}])[0].get('amount', ''),
        'to_amount': action.get('out', {}).get('coins', [{}])[0].get('amount', ''),
        'volume_usd': usd_value,
        'affiliate_fee_usd': affiliate_fee,
        'affiliate_fee_asset': 'RUNE'
    }
```

### 4. CowSwap Detection
```python
def calculate_affiliate_fee(self, trade: Dict) -> float:
    """Calculate affiliate fee based on trade data"""
    usd_value = float(trade.get('usd_value', 0))
    affiliate_fee_percentage = 0.0055  # 55 bps
    return usd_value * affiliate_fee_percentage
```

## 🗄️ Database Consolidation Logic

```python
def map_to_comprehensive_schema(self, row_dict: Dict, protocol: str) -> Optional[Dict]:
    """Map protocol-specific row to comprehensive schema"""
    return {
        'protocol': protocol,
        'chain': row_dict.get('chain', 'unknown'),
        'tx_hash': row_dict.get('tx_hash', row_dict.get('transaction_hash', '')),
        'block_number': row_dict.get('block_number', 0),
        'timestamp': row_dict.get('timestamp', row_dict.get('block_timestamp', 0)),
        'from_asset': row_dict.get('from_asset', row_dict.get('input_token', row_dict.get('sell_token', ''))),
        'to_asset': row_dict.get('to_asset', row_dict.get('output_token', row_dict.get('buy_token', ''))),
        'from_amount': self.safe_float(row_dict.get('from_amount', row_dict.get('input_amount', 0))),
        'to_amount': self.safe_float(row_dict.get('to_amount', row_dict.get('output_amount', 0))),
        'from_amount_usd': self.safe_float(row_dict.get('from_amount_usd', 0)),
        'to_amount_usd': self.safe_float(row_dict.get('to_amount_usd', 0)),
        'volume_usd': self.safe_float(row_dict.get('volume_usd', 0)),
        'affiliate_fee_amount': self.safe_float(row_dict.get('affiliate_fee_amount', 0)),
        'affiliate_fee_usd': self.safe_float(row_dict.get('affiliate_fee_usd', 0)),
        'affiliate_fee_asset': row_dict.get('affiliate_fee_asset', ''),
        'affiliate_address': row_dict.get('affiliate_address', row_dict.get('partner', '')),
        'sender_address': row_dict.get('sender', row_dict.get('from_address', '')),
        'recipient_address': row_dict.get('recipient', row_dict.get('to_address', '')),
        'event_type': row_dict.get('event_type', 'transaction'),
        'raw_data': str(row_dict)
    }
```

## 🔧 Token Identification System

### Cross-Chain Token Mappings
```python
cross_chain_tokens = {
    'BTC': {
        'ethereum': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',  # WBTC
        'polygon': '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6',   # WBTC
        'arbitrum': '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f',  # WBTC
        'optimism': '0x68f180fcce6836688e9084f035309e29bf0a2095',  # WBTC
        'base': '0x4200000000000000000000000000000000000006',       # WETH
        'avalanche': '0x50b7545627a5162f82a992c33b87adc75187b218', # WBTC
        'bsc': '0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c'        # BTCB
    },
    'ETH': {
        'ethereum': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',  # WETH
        'polygon': '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619',   # WETH
        'arbitrum': '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',  # WETH
        'optimism': '0x4200000000000000000000000000000000000006',   # WETH
        'base': '0x4200000000000000000000000000000000000006',       # WETH
        'avalanche': '0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab', # WETH
        'bsc': '0x2170ed0880ac9a755fd29b2688956bd959f933f8'        # WETH
    },
    'USDC': {
        'ethereum': '0xa0b86a33e6441b8c4b8c8c8c8c8c8c8c8c8c8c8',
        'polygon': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
        'arbitrum': '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8',
        'optimism': '0x7f5c764cbc14f9669b88837ca1490cca17c31607',
        'base': '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
        'avalanche': '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e',
        'bsc': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d'
    },
    'USDT': {
        'ethereum': '0xdac17f958d2ee523a2206206994597c13d831ec7',
        'polygon': '0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
        'arbitrum': '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9',
        'optimism': '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58',
        'base': '0x50c5725949a6f0c72e6c4a641f24049a917db0cb',
        'avalanche': '0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7',
        'bsc': '0x55d398326f99059ff775485246999027b3197955'
    },
    'DAI': {
        'ethereum': '0x6b175474e89094c44da98b954eedeac495271d0f',
        'polygon': '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063',
        'arbitrum': '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1',
        'optimism': '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1',
        'base': '0x50c5725949a6f0c72e6c4a641f24049a917db0cb',
        'avalanche': '0xd586e7f844cea2f87f50152665bcbc2c279d8d70',
        'bsc': '0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3'
    }
}
```

### Token Lookup Sources
1. **CoinMarketCap API** - For new tokens and pricing
2. **Uniswap V2/V3** - For LP tokens and protocol tokens
3. **Webscraped Data** - CSV/XLSX files for THORChain and CowSwap
4. **Cross-chain mappings** - For major assets (BTC, ETH, USDC, USDT, DAI)

## 📊 Event Signatures

### ERC-20 Transfer
```
0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
```

### Relay Protocol Events
```
SolverCallExecuted: 0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f
SolverNativeTransfer: 0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496
```

### CowSwap Events
```
Trade: 0xa07a543ab8a018198e99ca0184c93fe9050a79400a0a723441f84de1d972cc17
Order: 0xed99827efb37016f2275f98c4bcf71c7551c75d59e9b450f79fa32e60be672c2
```

## 🔄 Master Runner Architecture

```python
class MasterRunner:
    def __init__(self):
        self.listeners = {
            'relay': RelayListener(),
            'portals': PortalsListener(),
            'thorchain': THORChainListener(),
            'chainflip': ChainflipBrokerListener(),
            'cowswap': CowSwapDuneListener(),
            'zerox': ZeroXListener(),
        }
    
    def run_all_listeners(self, blocks_to_scan: int = 2000, limit: int = 100):
        """Run all protocol listeners"""
        for protocol, listener in self.listeners.items():
            if protocol in ['thorchain', 'chainflip']:
                listener.run_listener(limit)
            else:
                listener.run_listener(blocks_to_scan)
    
    def consolidate_databases(self):
        """Consolidate all protocol databases into comprehensive database"""
        # Map each protocol's database to comprehensive schema
        # Handle different column names and data formats
```

## 🛠️ Required Dependencies

```python
# Core dependencies
web3==6.11.3
requests==2.31.0
pandas==2.1.4
pyyaml==6.0.1
python-dotenv==1.0.0
eth-abi==4.2.1

# Optional for analysis
matplotlib==3.8.2
numpy==1.24.3
openpyxl==3.1.2
```

## 🔑 Environment Variables

```bash
# Required API Keys
INFURA_API_KEY=your_infura_key
ALCHEMY_API_KEY=your_alchemy_key
COINMARKETCAP_API_KEY=your_coinmarketcap_key

# Optional
THORCHAIN_API_KEY=your_thorchain_key
```

## 📁 Project Structure

```
shapeshift-affiliate-tracker/
├── listeners/
│   ├── relay_listener.py
│   ├── portals_listener.py
│   ├── thorchain_listener.py
│   ├── chainflip_listener.py
│   ├── cowswap_listener_dune.py
│   ├── zerox_listener.py
│   └── master_runner.py
├── shared/
│   ├── token_cache.py
│   ├── block_tracker.py
│   ├── custom_logging.py
│   ├── token_lookup_enhanced.py
│   └── token_lookup_with_webscrape.py
├── databases/
│   ├── comprehensive_affiliate.db
│   ├── relay_transactions.db
│   ├── portals_transactions.db
│   └── ...
├── scripts/
│   ├── debug/
│   └── analysis/
└── webscrape/
    ├── viewblock_thorchain_combined_dedup_2025-07-29.csv
    └── CoW Swap Partner Dashboard Table.xlsx
```

## 🎯 Key Success Factors

1. **Multi-chain support** - Handle different RPC endpoints and chain IDs
2. **Robust error handling** - Graceful fallbacks for API failures
3. **Token identification** - Multiple lookup sources for unknown tokens
4. **Database consolidation** - Unified schema across all protocols
5. **Rate limiting** - Respect API limits and implement delays
6. **Block tracking** - Resume from last processed block
7. **Affiliate detection** - Multiple methods to identify ShapeShift involvement

## 🚀 Quick Start Commands

```bash
# Run all listeners
python listeners/master_runner.py --blocks 2000 --limit 100

# Run individual listeners
python listeners/relay_listener.py --chain ethereum --blocks 1000
python listeners/portals_listener.py --blocks 1000

# Debug unknown tokens
python scripts/debug/identify_unknown_tokens.py

# Generate reports
python scripts/analysis/july_2025_analysis.py
```

This export contains all the working logic, configurations, and architecture needed to rebuild the ShapeShift affiliate fee tracking system from scratch. 