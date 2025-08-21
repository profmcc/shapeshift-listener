# OnchainDen Clone - Transaction Analysis & Revenue Tracking

A comprehensive tool for analyzing Zapper addresses, downloading transactions from multiple chains, and categorizing them according to configurable rules for revenue analysis.

## Features

### Core Functionality
- **Multi-chain Transaction Download**: Support for Ethereum, Base, Arbitrum, Polygon, Optimism, BSC, and Avalanche
- **Configurable Categorization**: Define revenue, expense, and ignored addresses with custom rules
- **ERC-20 Token Support**: Parse token transfers and contract interactions
- **Block Tracking**: Resume scanning from last processed block to avoid re-processing
- **Database Storage**: SQLite database with indexed tables for fast queries

### Advanced Features
- **Event Log Parsing**: Parse contract events and method signatures
- **Gas Cost Analysis**: Track gas costs in ETH and USD
- **Protocol Detection**: Automatically identify known DeFi protocols
- **Custom Rules Engine**: Support for address patterns, value thresholds, and method signatures
- **Token Metadata**: Extract token symbols, names, and decimals

### Reporting
- **CSV Export**: Structured transaction data for spreadsheet analysis
- **JSON Export**: Complete data with nested summaries and statistics
- **Multi-format Reports**: Chain summaries, category breakdowns, and token analytics

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Dependencies
```bash
pip install -r requirements_onchainden.txt
```

### Required API Keys
- **Alchemy**: For Ethereum, Polygon, Arbitrum, and Optimism RPC access
- **Block Explorer APIs**: Etherscan, Polygonscan, Basescan, Arbiscan (optional)

## Quick Start

### 1. Create Configuration
```bash
python onchainden_cli.py --create-config
```

This creates a sample configuration file at `config/onchainden_config.json`.

### 2. Edit Configuration
Edit the configuration file with your:
- API keys
- Addresses to track
- Revenue/expense address classifications
- Custom categorization rules

### 3. Validate Configuration
```bash
python onchainden_cli.py --validate-config config/onchainden_config.json
```

### 4. Run Analysis
```bash
# Generate CSV report
python onchainden_cli.py --analyze config/onchainden_config.json --output csv

# Generate JSON report
python onchainden_cli.py --analyze config/onchainden_config.json --output json
```

## Configuration

### Basic Configuration Structure
```json
{
  "rpc_urls": {
    "1": "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
    "137": "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY",
    "8453": "https://mainnet.base.org"
  },
  "api_keys": {
    "etherscan": "YOUR_ETHERSCAN_KEY",
    "polygonscan": "YOUR_POLYGONSCAN_KEY"
  },
  "addresses": [
    "0x90a48d5cf7343b08da12e067680b4c6dbfe551be"
  ],
  "revenue_addresses": [
    "0x90a48d5cf7343b08da12e067680b4c6dbfe551be"
  ],
  "expense_addresses": [],
  "ignored_addresses": [],
  "custom_rules": []
}
```

### Custom Rules
Define custom categorization logic:

```json
{
  "custom_rules": [
    {
      "type": "address_pattern",
      "pattern": "0x1234",
      "category": "Custom",
      "subcategory": "Special"
    },
    {
      "type": "value_threshold",
      "threshold": "1000000000000000000000",
      "category": "Large Transfer",
      "subcategory": "High Value"
    },
    {
      "type": "method_signature",
      "signature": "0xa9059cbb",
      "category": "Token Transfer",
      "subcategory": "ERC-20"
    }
  ]
}
```

### Rule Types
- **`address_pattern`**: Match addresses containing specific patterns
- **`value_threshold`**: Categorize transactions above certain values
- **`method_signature`**: Identify transactions by contract method
- **`token_transfer`**: Detect ERC-20 token transfers

## Usage Examples

### Basic Address Analysis
```python
from enhanced_onchainden import EnhancedOnchainDenAnalyzer

# Initialize analyzer
analyzer = EnhancedOnchainDenAnalyzer("config/onchainden_config.json")

# Analyze addresses
addresses = ["0x90a48d5cf7343b08da12e067680b4c6dbfe551be"]
results = await analyzer.analyze_addresses(addresses)

# Generate reports
csv_report = analyzer.generate_enhanced_report(addresses, "csv")
json_report = analyzer.generate_enhanced_report(addresses, "json")
```

### Custom Categorization
```python
from enhanced_onchainden import EnhancedTransactionCategorizer

config = {
    "revenue_addresses": ["0x1234..."],
    "expense_addresses": ["0x5678..."],
    "custom_rules": [
        {
            "type": "method_signature",
            "signature": "0xa9059cbb",
            "category": "Token Transfer",
            "subcategory": "ERC-20"
        }
    ]
}

categorizer = EnhancedTransactionCategorizer(config)
```

### Chain-Specific Analysis
```python
# Analyze specific chains only
chains = [1, 137]  # Ethereum and Polygon
results = await analyzer.analyze_addresses(addresses, chains)
```

## Database Schema

### Enhanced Transactions Table
```sql
CREATE TABLE enhanced_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash TEXT UNIQUE NOT NULL,
    block_number INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    value TEXT NOT NULL,
    gas_used INTEGER NOT NULL,
    gas_price TEXT NOT NULL,
    gas_cost_eth REAL NOT NULL,
    gas_cost_usd REAL,
    chain_id INTEGER NOT NULL,
    chain_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    revenue_type TEXT NOT NULL,
    token_address TEXT,
    token_symbol TEXT,
    token_name TEXT,
    token_decimals INTEGER,
    token_amount TEXT,
    usd_value REAL,
    method_signature TEXT,
    contract_interaction BOOLEAN NOT NULL,
    events TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Output Formats

### CSV Report
- Transaction details in spreadsheet format
- One row per transaction
- All fields as columns
- Suitable for Excel/Google Sheets analysis

### JSON Report
- Complete data structure
- Nested summaries by address, chain, and category
- Token analytics and gas cost breakdowns
- Machine-readable format for further processing

## Advanced Features

### Protocol Detection
Automatically identifies transactions involving known DeFi protocols:
- Uniswap V2/V3
- Aave
- Compound
- Custom protocol definitions

### Event Parsing
- ERC-20 Transfer events
- Contract method signatures
- Custom event types
- Gas usage analysis

### Block Tracking
- Persistent block number storage
- Resume scanning from last processed block
- Avoid re-processing historical data
- Chain-specific tracking

## Performance Considerations

### Optimization Tips
- Use Alchemy RPC endpoints for better performance
- Limit block ranges for initial scans
- Use specific chain selection when possible
- Monitor database size and performance

### Rate Limiting
- Respect RPC provider rate limits
- Implement delays between requests
- Use batch processing when available
- Monitor API usage

## Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check RPC endpoint availability
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
```

#### Configuration Errors
```bash
# Validate configuration
python onchainden_cli.py --validate-config config/onchainden_config.json
```

#### Database Issues
```bash
# Check database integrity
sqlite3 databases/enhanced_onchainden.db "PRAGMA integrity_check;"
```

### Log Files
- `enhanced_onchainden.log`: Main application logs
- `onchainden.log`: Basic version logs
- Check logs for detailed error information

## Development

### Project Structure
```
scripts/
├── enhanced_onchainden.py      # Main enhanced analyzer
├── onchainden_clone.py         # Basic version
├── onchainden_cli.py           # CLI interface
├── requirements_onchainden.txt  # Dependencies
├── config/                     # Configuration files
│   └── onchainden_config.json
└── README_ONCHAINDEN.md        # This file
```

### Extending the System
- Add new rule types in `EnhancedTransactionCategorizer`
- Implement new protocol detection in `_load_known_protocols`
- Add new event parsing in `ERC20Parser`
- Extend database schema for additional fields

### Testing
```bash
# Run with verbose logging
python onchainden_cli.py --analyze config/onchainden_config.json --verbose

# Test specific components
python -c "from enhanced_onchainden import EnhancedOnchainDenAnalyzer; print('Import successful')"
```

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include docstrings for classes and methods
- Add logging for debugging

### Testing
- Test with multiple chains
- Validate configuration parsing
- Test error handling scenarios
- Verify database operations

## License

This project is part of the ShapeShift Affiliate Tracker and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Validate configuration files
4. Test with minimal configuration

## Roadmap

### Planned Features
- **Price Integration**: Real-time USD value calculations
- **HTML Reports**: Interactive web-based reports
- **API Endpoints**: REST API for programmatic access
- **Dashboard**: Web-based monitoring interface
- **Alerting**: Notifications for specific transaction types
- **Batch Processing**: Efficient handling of large address lists
- **Cloud Integration**: AWS/Azure deployment options
