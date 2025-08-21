# CSV-Based Affiliate Fee Tracking System

This system has been migrated from SQLite databases to CSV files for better portability, easier analysis, and simpler data management.

## 🚀 Quick Start

### 1. Run Individual Listeners

```bash
# Portals listener (ShapeShift affiliate fees from Portals)
python csv_portals_listener.py --blocks 1000

# Relay listener (ShapeShift affiliate fees from Relay)
python csv_relay_listener.py --blocks 1000
```

### 2. Run All Listeners with Master Runner

```bash
# Run all listeners and consolidate data
python csv_master_runner.py --blocks 1000

# Show statistics only
python csv_master_runner.py --stats-only
```

## 📁 CSV File Structure

### Main Transaction Files

- **`portals_transactions.csv`** - Portals affiliate transactions
- **`relay_transactions.csv`** - Relay affiliate transactions  
- **`consolidated_affiliate_transactions.csv`** - Combined data from all sources

### Block Tracking Files

- **`block_tracker.csv`** - Portals block processing status
- **`relay_block_tracker.csv`** - Relay block processing status

### Legacy Data (Converted from Databases)

- **`portals_transactions_combined.csv`** - Historical Portals data
- **`thorchain_consolidated_thorchain_transactions.csv`** - ThorChain data
- **`cowswap_transactions_cowswap_transactions.csv`** - CoW Swap data
- **`comprehensive_affiliate_comprehensive_transactions.csv`** - Comprehensive affiliate data

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
ALCHEMY_API_KEY=your_alchemy_api_key_here
```

### Chain Support

The system supports 5 chains:
- **Ethereum** - Mainnet
- **Polygon** - Polygon PoS
- **Arbitrum** - Arbitrum One
- **Optimism** - Optimism
- **Base** - Base

## 📊 Data Fields

### Common Fields (All Sources)

| Field | Description |
|-------|-------------|
| `source` | Data source (portals, relay) |
| `chain` | Blockchain name |
| `tx_hash` | Transaction hash |
| `block_number` | Block number |
| `block_timestamp` | Unix timestamp |
| `block_date` | Human-readable date |
| `input_token` | Input token address |
| `input_amount` | Input token amount |
| `output_token` | Output token address |
| `output_amount` | Output token amount |
| `affiliate_token` | Affiliate fee token |
| `affiliate_amount` | Affiliate fee amount |
| `affiliate_fee_usd` | Affiliate fee in USD |
| `volume_usd` | Transaction volume in USD |
| `created_at` | Record creation timestamp |
| `created_date` | Record creation date |

### Source-Specific Fields

#### Portals
- `sender` - Transaction sender
- `broadcaster` - Portals broadcaster
- `recipient` - Transaction recipient
- `partner` - ShapeShift affiliate address

#### Relay
- `sender` - Transaction sender
- `recipient` - Transaction recipient
- `partner` - ShapeShift affiliate address
- `relay_fee` - Relay protocol fee
- `relay_fee_token` - Relay fee token

## 🔍 Data Analysis

### Using Python with Pandas

```python
import pandas as pd

# Load consolidated data
df = pd.read_csv('csv_data/consolidated_affiliate_transactions.csv')

# Filter by source
portals_tx = df[df['source'] == 'portals']
relay_tx = df[df['source'] == 'relay']

# Filter by chain
ethereum_tx = df[df['chain'] == 'ethereum']

# Filter by date range
recent_tx = df[df['block_timestamp'] > 1700000000]

# Group by source and chain
summary = df.groupby(['source', 'chain']).size()
```

### Using Command Line Tools

```bash
# Count transactions by source
cut -d',' -f1 csv_data/consolidated_affiliate_transactions.csv | sort | uniq -c

# Count transactions by chain
cut -d',' -f2 csv_data/consolidated_affiliate_transactions.csv | sort | uniq -c

# Show recent transactions
tail -10 csv_data/consolidated_affiliate_transactions.csv
```

## 🧹 Cleanup and Maintenance

### Convert Existing Database Data

```bash
# Convert all databases to CSV
python convert_db_to_csv.py
```

### Clean Up Old Databases

```bash
# Move old databases to backup (recommended)
python cleanup_databases.py

# Or manually remove if you're sure
rm -rf *.db databases/*.db listeners/databases/*.db
```

### Archive Old CSV Data

```bash
# Create monthly archives
mkdir -p csv_data/archives/$(date +%Y-%m)
mv csv_data/*.csv csv_data/archives/$(date +%Y-%m)/
```

## 📈 Monitoring and Alerts

### Check System Status

```bash
# Show current statistics
python csv_master_runner.py --stats-only

# Check file sizes
ls -lh csv_data/*.csv

# Monitor recent activity
tail -f csv_data/consolidated_affiliate_transactions.csv
```

### Automated Monitoring

Create a cron job to run listeners regularly:

```bash
# Add to crontab - run every hour
0 * * * * cd /path/to/shapeshift-affiliate-tracker && python csv_master_runner.py --blocks 1000 >> logs/csv_runner.log 2>&1
```

## 🔒 Data Security

- CSV files are stored locally in `csv_data/` directory
- No sensitive data is exposed in transaction records
- API keys are stored in `.env` file (keep secure)
- Consider encrypting CSV files if storing sensitive information

## 🚨 Troubleshooting

### Common Issues

1. **No transactions found**
   - Check Alchemy API key in `.env`
   - Verify network connectivity
   - Check if blocks contain affiliate transactions

2. **CSV file corruption**
   - Restore from backup
   - Re-run listener to regenerate data

3. **Memory issues with large files**
   - Use pandas chunking for large CSV files
   - Consider archiving old data

### Logs

Check log files for detailed error information:
- `csv_portals_listener.log`
- `csv_relay_listener.log`
- `csv_master_runner.log`

## 📚 API Reference

### CSVPortalsListener

```python
listener = CSVPortalsListener(csv_dir="csv_data")
listener.run_listener(blocks_to_scan=1000)
listener.get_csv_stats()
```

### CSVRelayListener

```python
listener = CSVRelayListener(csv_dir="csv_data")
listener.run_listener(blocks_to_scan=1000)
listener.get_csv_stats()
```

### CSVMasterRunner

```python
runner = CSVMasterRunner(csv_dir="csv_data")
runner.run_all_listeners(blocks_to_scan=1000)
runner.consolidate_csv_data()
runner.show_overall_stats()
```

## 🔄 Migration from Databases

If you're migrating from the old database system:

1. **Backup existing data**
   ```bash
   python convert_db_to_csv.py
   ```

2. **Test CSV system**
   ```bash
   python csv_master_runner.py --stats-only
   ```

3. **Clean up old databases**
   ```bash
   python cleanup_databases.py
   ```

4. **Verify data integrity**
   - Compare CSV row counts with database counts
   - Check sample transactions match

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review log files for error details
- Ensure all dependencies are installed
- Verify environment configuration

---

**Note**: This system replaces the previous SQLite database approach with CSV files for improved portability and easier data analysis. All historical data has been preserved and converted to CSV format.
