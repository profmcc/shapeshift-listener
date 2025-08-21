# ShapeShift Affiliate Tracker
# ===========================
# 
# HISTORY & LEARNING:
# - Originally started as a simple affiliate fee tracking system
# - Evolved through multiple iterations with different approaches
# - Previous attempts at centralized configuration failed due to validation issues
# - Database approach led to complexity and maintenance problems
# - Current approach: CSV-based storage with hybrid configuration system
#
# WHAT THIS PROJECT IS ATTEMPTING:
# - Track ShapeShift affiliate fees across multiple DeFi protocols
# - Monitor transactions on various EVM chains (Ethereum, Polygon, Base, etc.)
# - Provide comprehensive data for affiliate revenue analysis
# - Enable easy analysis and reporting of affiliate performance
#
# WHY THIS APPROACH:
# - CSV storage is simpler than database management
# - Easy to analyze with standard tools (Excel, Python, R)
# - Portable and human-readable format
# - Better for data science and analysis workflows
# - Hybrid config system supports both centralized and legacy approaches
#
# CURRENT STATUS:
# - Working CSV-based listeners for all major protocols
# - Hybrid configuration system implemented and functional
# - No volume thresholds for comprehensive tracking
# - Ready for production use with proper API keys
#
# PROTOCOLS SUPPORTED:
# - ButterSwap: DEX aggregator with affiliate fees
# - Relay: Cross-chain aggregation protocol
# - CoW Swap: MEV-protected DEX
# - Portals: Cross-chain bridge protocol
# - ThorChain: Cross-chain liquidity protocol

## Overview

The ShapeShift Affiliate Tracker is a comprehensive system for monitoring and analyzing affiliate fees received by ShapeShift across various DeFi protocols and blockchain networks. This system tracks transactions in real-time, identifies affiliate fee payments, and provides detailed analytics for revenue analysis.

## Key Features

- **Multi-Protocol Support**: Tracks affiliate fees from ButterSwap, Relay, CoW Swap, Portals, and ThorChain
- **Multi-Chain Coverage**: Monitors Ethereum, Polygon, Optimism, Arbitrum, Base, Avalanche, and BSC
- **CSV-Based Storage**: Simple, portable data storage for easy analysis
- **Hybrid Configuration**: Supports both centralized configuration and legacy hardcoded approaches
- **Real-Time Monitoring**: Continuously scans blockchain for new affiliate transactions
- **Comprehensive Analytics**: Provides detailed reporting and statistics

## Architecture

### Configuration System
The project uses a hybrid configuration approach:
- **Centralized Config**: Main configuration in `config/shapeshift_config.yaml`
- **Legacy Support**: Hardcoded configurations in individual listener files
- **Flexible Loading**: Graceful fallbacks when configuration sections are missing

### Data Storage
- **CSV Files**: Each protocol stores data in separate CSV files
- **Consolidated Data**: Master runner combines all data into unified datasets
- **Block Tracking**: Prevents re-processing of already scanned blocks

### Listener System
- **Protocol Listeners**: Specialized listeners for each DeFi protocol
- **Event Filtering**: Identifies relevant blockchain events for affiliate fees
- **Rate Limiting**: Respects RPC provider limits and API constraints

## Quick Start

### Prerequisites
- Python 3.8+
- Web3.py library
- API keys for blockchain RPC providers (Alchemy recommended)

### Installation
```bash
# Clone the repository
git clone https://github.com/profmcc/shapeshift-affiliate-tracker.git
cd shapeshift-affiliate-tracker

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys
```

### Configuration
1. **API Keys**: Set your Alchemy API key in the `.env` file
2. **Addresses**: Verify affiliate addresses in `config/shapeshift_config.yaml`
3. **Chains**: Configure which blockchain networks to monitor

### Running the System
```bash
# Run all listeners
python csv_master_runner.py

# Run specific listener
python affiliate_listeners_csv/csv_butterswap_listener.py

# Check status
python csv_master_runner.py --status
```

## Configuration Details

### Affiliate Addresses
The system tracks multiple ShapeShift affiliate addresses:
- **Primary**: `0x35339070f178dC4119732982C23F5a8d88D3f8a3` (most protocols)
- **Relay/CoW Swap**: `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502` (Base chain)
- **Legacy**: Various historical addresses found in existing data

### Supported Chains
- **Ethereum**: Chain ID 1, start block ~19,000,000
- **Polygon**: Chain ID 137, start block ~50,000,000
- **Optimism**: Chain ID 10, start block ~50,000,000
- **Arbitrum**: Chain ID 42161, start block ~100,000,000
- **Base**: Chain ID 8453, start block ~32,900,000
- **Avalanche**: Chain ID 43114, start block ~30,000,000
- **BSC**: Chain ID 56, start block varies

### Volume Thresholds
- **Minimum Volume**: $0.00 (comprehensive tracking)
- **Minimum Affiliate Fee**: $0.01 (prevents dust transactions)

## Data Structure

### Transaction Data
Each affiliate transaction includes:
- Timestamp and blockchain information
- User addresses and transaction details
- Token amounts and USD values
- Affiliate fee amounts and calculations

### CSV File Organization
```
csv_data/
├── butterswap_transactions.csv      # ButterSwap affiliate transactions
├── relay_transactions.csv           # Relay protocol transactions
├── cowswap_transactions.csv         # CoW Swap transactions
├── portals_transactions.csv         # Portals bridge transactions
├── thorchain_transactions.csv       # ThorChain swap transactions
├── consolidated_affiliate_transactions.csv  # Combined dataset
└── block_tracking/                  # Block progress tracking
    ├── butterswap_block_tracker_*.csv
    ├── relay_block_tracker_*.csv
    └── ...
```

## Protocol-Specific Details

### ButterSwap
- **Focus**: DEX aggregator affiliate fees
- **Primary Chain**: Base (0x35339070f178dC4119732982C23F5a8d88D3f8a3)
- **Event Types**: Swap, Mint, Burn, Transfer events
- **Contract**: Uniswap V2 compatible router

### Relay
- **Focus**: Cross-chain aggregation affiliate fees
- **Primary Chain**: Base (0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502)
- **Event Types**: Affiliate fee and transfer events
- **Contract**: Relay router with affiliate fee collection

### CoW Swap
- **Focus**: MEV-protected DEX affiliate fees
- **Primary Chain**: Base (0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502)
- **Event Types**: Order settlement and affiliate fee events
- **Contract**: CoW Swap settlement contract

### Portals
- **Focus**: Cross-chain bridge affiliate fees
- **Primary Chain**: All chains (same contract address)
- **Event Types**: Bridge completion and affiliate fee events
- **Contract**: Portals bridge contract

### ThorChain
- **Focus**: Cross-chain liquidity affiliate fees
- **Primary Chain**: ThorChain (native)
- **Event Types**: Swap completion and memo parsing
- **API**: ThorChain Midgard and Thornode APIs

## Usage Examples

### Basic Monitoring
```python
from csv_master_runner import CSVMasterRunner

# Initialize and run all listeners
runner = CSVMasterRunner()
runner.run_all_listeners()
```

### Protocol-Specific Monitoring
```python
from affiliate_listeners_csv.csv_butterswap_listener import CSVButterSwapListener

# Monitor ButterSwap specifically
listener = CSVButterSwapListener()
listener.scan_chain(8453)  # Base chain
```

### Data Analysis
```python
import pandas as pd

# Load consolidated data
df = pd.read_csv('csv_data/consolidated_affiliate_transactions.csv')

# Analyze by protocol
protocol_summary = df.groupby('protocol').agg({
    'affiliate_fee_usd': 'sum',
    'volume_usd': 'sum',
    'transaction_hash': 'count'
}).rename(columns={'transaction_hash': 'transaction_count'})
```

## Troubleshooting

### Common Issues
1. **API Rate Limits**: Reduce batch sizes or increase delays
2. **Configuration Errors**: Check YAML syntax and required fields
3. **RPC Connection Failures**: Verify API keys and network connectivity
4. **File Permission Errors**: Ensure write access to CSV directories

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python csv_master_runner.py
```

### Configuration Validation
```bash
# Test configuration loading
python -c "from shared.config_loader import get_config; print('Config loaded successfully')"
```

## Development

### Project Structure
```
shapeshift-affiliate-tracker/
├── config/                          # Configuration files
├── shared/                          # Shared utilities
├── affiliate_listeners_csv/         # CSV-based listeners
├── listeners/                       # Legacy database listeners
├── csv_data/                        # Data storage
├── scripts/                         # Analysis and utility scripts
└── docs/                           # Documentation
```

### Adding New Protocols
1. Create new listener class in `affiliate_listeners_csv/`
2. Add configuration in `config/shapeshift_config.yaml`
3. Update `csv_master_runner.py` to include new listener
4. Add event signatures and contract addresses

### Testing
```bash
# Run configuration tests
python shared/config_loader.py

# Test individual listeners
python affiliate_listeners_csv/csv_butterswap_listener.py --stats
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add comprehensive comments explaining the purpose and approach
5. Test thoroughly
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed information

## Roadmap

- [ ] Real-time web dashboard
- [ ] Advanced analytics and reporting
- [ ] Mobile app for monitoring
- [ ] Integration with additional protocols
- [ ] Automated alerting system
- [ ] Performance optimization
- [ ] Enhanced error handling and recovery

---

**Note**: This system is designed for monitoring and analysis purposes. Always verify affiliate addresses and transaction data independently before making business decisions based on the collected information. 