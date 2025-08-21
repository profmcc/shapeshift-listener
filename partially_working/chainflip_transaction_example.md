# Chainflip Listener - Example Transaction Data

## Test Transaction (Fallback Data Only)

**Note**: This is fallback test data only. Real transaction data cannot be collected due to missing scraper dependencies.

### Transaction Details
```
Transaction ID: test_1
Broker Address: cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi  
Broker Name: ShapeShift Broker 1
Swap Type: swap
Source Asset: ETH
Destination Asset: USDC
Swap Amount: 1.5
Output Amount: 2800
Broker Fee Amount: 0.001
Broker Fee Asset: ETH
Source Chain: ethereum
Destination Chain: ethereum
Transaction Hash: 0x1234567890abcdef
Block Number: 12345678
Swap State: completed
Timestamp: 2025-07-31T10:57:05.994582
```

### USD Values
```
Volume USD: (calculated with price cache)
Broker Fee USD: (calculated with price cache)
```

### Database Structure
```sql
CREATE TABLE chainflip_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE NOT NULL,
    broker_address TEXT NOT NULL,
    broker_name TEXT,
    swap_type TEXT,
    source_asset TEXT,
    destination_asset TEXT,
    swap_amount TEXT,
    output_amount TEXT,
    broker_fee_amount TEXT,
    broker_fee_asset TEXT,
    source_chain TEXT,
    destination_chain TEXT,
    transaction_hash TEXT,
    block_number INTEGER,
    swap_state TEXT,
    timestamp TEXT NOT NULL,
    scraped_at TEXT NOT NULL,
    raw_data TEXT,
    source_asset_name TEXT,
    destination_asset_name TEXT,
    broker_fee_asset_name TEXT,
    broker_fee_usd REAL,
    volume_usd REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## ShapeShift Broker Addresses

```
Broker 1: cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi
Broker 2: cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8
```

## Status

❌ **NOT WORKING**: Missing `chainflip_comprehensive_scraper.py` dependency required for real data collection.
