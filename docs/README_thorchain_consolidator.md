# THORChain Data Consolidator

A comprehensive tool for consolidating THORChain transaction data from multiple ViewBlock export files (CSV and JSON) into a unified SQLite database with automatic deduplication and incremental updates.

## Features

- **Multi-format Support**: Handles both CSV and JSON export files from ViewBlock
- **Smart Deduplication**: Automatically prevents duplicate transactions based on transaction hash and timestamp
- **Incremental Updates**: Only processes new data when re-running, avoiding re-processing existing records
- **Automatic File Discovery**: Finds all `viewblock_thorchain_data_*` files in your Downloads directory
- **Comprehensive Logging**: Detailed progress tracking and error reporting
- **Database Statistics**: Built-in reporting on data coverage and asset distribution
- **Performance Optimized**: Uses SQLite indexes for fast queries and efficient storage

## Quick Start

### 1. Run the Consolidator

```bash
# From the project root directory
cd scripts
python run_thorchain_consolidator.py
```

### 2. Check Database Statistics

```bash
python thorchain_data_consolidator.py --stats
```

### 3. Advanced Usage

```bash
# Custom paths
python thorchain_data_consolidator.py --downloads /path/to/downloads --database /path/to/databases

# Force reprocessing (ignore existing data)
python thorchain_data_consolidator.py --force
```

## How It Works

### File Discovery
The consolidator automatically finds all files matching the pattern `viewblock_thorchain_data_*` in your Downloads directory, supporting both `.csv` and `.json` extensions.

### Data Processing
1. **CSV Files**: Parsed using Python's built-in CSV reader
2. **JSON Files**: Parsed using Python's JSON module
3. **Data Normalization**: Amounts are converted to floats, timestamps are parsed
4. **Deduplication**: Transactions are identified by `(tx_hash, timestamp)` combination

### Database Schema

```sql
CREATE TABLE thorchain_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash TEXT,                    -- Transaction hash (unique identifier)
    block_height TEXT,               -- Block height
    timestamp TEXT,                  -- Human-readable timestamp
    from_address TEXT,               -- Sender address
    to_address TEXT,                 -- Recipient address
    affiliate_address TEXT,          -- Affiliate address (if any)
    from_asset TEXT,                 -- Source asset (e.g., BTC, ETH)
    to_asset TEXT,                   -- Destination asset
    from_amount REAL,                -- Source amount (normalized)
    to_amount REAL,                  -- Destination amount (normalized)
    status TEXT,                     -- Transaction status
    type TEXT,                       -- Transaction type (e.g., Swap)
    raw_row_text TEXT,               -- Original row data for debugging
    source_file TEXT,                -- Source file name
    file_timestamp TEXT,             -- When the file was processed
    created_at INTEGER,              -- Database record creation time
    updated_at INTEGER               -- Last update time
);
```

### Deduplication Strategy
- **Primary Key**: `(tx_hash, timestamp)` combination
- **Fallback**: If `tx_hash` is null, uses `(block_height, timestamp, from_address)`
- **Smart Updates**: Only inserts new transactions, never overwrites existing ones

## File Format Support

### CSV Format
Expected columns:
- `affiliate_address`, `block_height`, `from_address`, `from_amount`, `from_asset`
- `raw_row_text`, `status`, `timestamp`, `to_address`, `to_amount`, `to_asset`
- `tx_hash`, `type`

### JSON Format
Expected structure:
```json
[
  {
    "affiliate_address": "address",
    "block_height": "height",
    "from_address": "address",
    "from_amount": "amount",
    "from_asset": "asset",
    "raw_row_text": "text",
    "status": "status",
    "timestamp": "timestamp",
    "to_address": "address",
    "to_amount": "amount",
    "to_asset": "asset",
    "tx_hash": "hash",
    "type": "type"
  }
]
```

## Usage Examples

### Basic Consolidation
```bash
# Run with default settings (Downloads directory → databases folder)
python run_thorchain_consolidator.py
```

### Check Current Database Status
```bash
# View statistics without processing new files
python thorchain_data_consolidator.py --stats
```

### Custom Paths
```bash
# Use custom directories
python thorchain_data_consolidator.py \
  --downloads /Users/chrismccarthy/Downloads \
  --database /path/to/custom/databases
```

### Force Reprocessing
```bash
# Reprocess all files (useful for testing or after schema changes)
python thorchain_data_consolidator.py --force
```

## Output and Logging

### Console Output
```
🚀 THORChain Data Consolidator
==================================================
📁 Downloads directory: /Users/chrismccarthy/Downloads
💾 Database directory: databases
==================================================

🔄 Starting consolidation...
📁 Found 15 viewblock data files
🔄 Processing: viewblock_thorchain_data_2025-08-11T22-04-08-799Z.json
📊 Parsed 1,247 transactions from JSON: viewblock_thorchain_data_2025-08-11T22-04-08-799Z.json
💾 Inserted 1,247 new transactions
📈 File viewblock_thorchain_data_2025-08-11T22-04-08-799Z.json: 1,247 new, 0 skipped

✅ Consolidation complete!
📊 Files processed: 15
📈 New transactions: 18,456
⏭️ Skipped (duplicates): 2,341

============================================================
📊 THORCHAIN CONSOLIDATED DATABASE STATISTICS
============================================================
Total Transactions: 18,456
Date Range: Jul 09 2025 05:12:20 PM (GMT-7) to Aug 11 2025 10:04:08 PM (GMT-7)

📁 Source Files (15):
  • viewblock_thorchain_data_2025-08-11T22-04-08-799Z.json: 1,247 transactions (2025-08-11T22:04:08.799000 to 2025-08-11T22:04:08.799000)
  • viewblock_thorchain_data_2025-08-11T17-52-44-583Z.json: 1,156 transactions (2025-08-11T17:52:44.583000 to 2025-08-11T17:52:44.583000)

🪙 Top Assets:
  • BTC: 4,892 transactions
  • ETH: 3,456 transactions
  • RUNE: 2,891 transactions
============================================================
```

### Log File
The consolidator provides detailed logging with timestamps and log levels for debugging and monitoring.

## Database Queries

### Basic Queries

```sql
-- Get all transactions
SELECT * FROM thorchain_transactions ORDER BY timestamp DESC LIMIT 10;

-- Get transactions by asset
SELECT * FROM thorchain_transactions WHERE from_asset = 'BTC' ORDER BY timestamp DESC;

-- Get transactions by date range
SELECT * FROM thorchain_transactions 
WHERE timestamp LIKE 'Jul 22 2025%' 
ORDER BY timestamp DESC;

-- Get transaction count by source file
SELECT source_file, COUNT(*) as count 
FROM thorchain_transactions 
GROUP BY source_file 
ORDER BY count DESC;
```

### Advanced Analytics

```sql
-- Asset distribution
SELECT from_asset, COUNT(*) as count, 
       SUM(from_amount) as total_amount
FROM thorchain_transactions 
WHERE from_asset IS NOT NULL 
GROUP BY from_asset 
ORDER BY count DESC;

-- Daily transaction volume
SELECT DATE(timestamp) as date, COUNT(*) as tx_count
FROM thorchain_transactions 
GROUP BY DATE(timestamp) 
ORDER BY date DESC;

-- Top trading pairs
SELECT from_asset, to_asset, COUNT(*) as pair_count
FROM thorchain_transactions 
WHERE from_asset IS NOT NULL AND to_asset IS NOT NULL
GROUP BY from_asset, to_asset 
ORDER BY pair_count DESC 
LIMIT 10;
```

## Error Handling

The consolidator includes comprehensive error handling:

- **File Reading Errors**: Logged and skipped, processing continues
- **Data Parsing Errors**: Individual row errors logged, file processing continues
- **Database Errors**: Transactions rolled back, detailed error logging
- **Missing Files**: Graceful handling of missing or corrupted files

## Performance Considerations

- **Indexes**: Automatic creation of performance indexes
- **Batch Processing**: Efficient bulk inserts using `executemany`
- **Memory Management**: Processes files one at a time to minimize memory usage
- **Transaction Batching**: Database commits after each file for data safety

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure write access to the databases directory
2. **File Encoding**: Files should be UTF-8 encoded
3. **Database Locks**: Close any other applications using the database
4. **Memory Issues**: For very large files, consider splitting them

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=scripts
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from thorchain_data_consolidator import THORChainDataConsolidator
consolidator = THORChainDataConsolidator('/Users/chrismccarthy/Downloads', 'databases')
consolidator.consolidate_all_files()
"
```

## Integration with Existing Systems

The consolidated database can be easily integrated with:

- **Existing THORChain listeners**: Use as a data source
- **Analytics tools**: Connect via SQLite drivers
- **Reporting systems**: Query for custom reports
- **Data pipelines**: Export to other formats

## Future Enhancements

- **Real-time monitoring**: Watch Downloads directory for new files
- **Data validation**: Enhanced schema validation and data quality checks
- **Export capabilities**: Export to CSV, JSON, or other formats
- **Web interface**: Simple web UI for database exploration
- **API endpoints**: REST API for programmatic access

## Support

For issues or questions:

1. Check the console output and logs for error messages
2. Verify file formats match expected schemas
3. Ensure sufficient disk space for database storage
4. Check file permissions and access rights

The consolidator is designed to be robust and self-documenting, with comprehensive logging to help diagnose any issues.
