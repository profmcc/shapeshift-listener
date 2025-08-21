# Data Structure Documentation

## CSV File Formats

### **1. CoW Swap Transactions** (`cowswap_transactions.csv`)

**Purpose**: Tracks affiliate fees from CoW Swap DEX aggregator trades with 55 bps validation

**Columns**:
```csv
tx_hash,block_number,block_timestamp,block_date,chain,protocol,user_address,affiliate_address,expected_fee_bps,actual_fee_bps,affiliate_fee_token,affiliate_fee_amount,affiliate_fee_usd,input_token,input_amount,input_amount_usd,output_token,output_amount,output_amount_usd,volume_usd,gas_used,gas_price,created_at,created_date
```

**Example Row**:
```csv
0x0840bba848e991cdcfbf2b71b8e1cb94fb72d6343ad4bb182f7ee1c48612221d,15000000,1640995200,2022-01-01,ethereum,cowswap,0x123...,0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be,55,55,WETH,0.133,454.00,UNI-V2,3000.0,69948.00,USDC,56980.0,56980.00,69948.00,150000,20000000000,2024-01-01 00:00:00,2024-01-01
```

**Data Sources**:
- **Chains**: Ethereum, Polygon, Optimism, Arbitrum, Base
- **Events**: `Trade` events from CoW Swap settlement contracts
- **Affiliate Address**: `0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be` (ShapeShift)

---

### **2. THORChain Transactions** (`thorchain_transactions.csv`)

**Purpose**: Tracks affiliate fees from THORChain cross-chain swaps with 55 bps validation

**Columns**:
```csv
tx_id,date,height,from_address,to_address,affiliate_address,expected_fee_bps,actual_fee_bps,affiliate_fee_amount,affiliate_fee_usd,from_asset,to_asset,from_amount,to_amount,from_amount_usd,to_amount_usd,volume_usd,swap_path,is_streaming_swap,liquidity_fee,swap_slip,timestamp,created_at,created_date
```

**Example Row**:
```csv
thor1abc...,2024-01-01,12345678,thor1def...,thor1ghi...,thor1z8s0yk6q86nqwsc2gagv4n9yt9c0hk9qtszt0p,55,55,0.001,3.25,ETH,USDC,0.1,180.0,200.00,180.00,190.00,ETH>USDC,false,0.005,0.02,1640995200,2024-01-01 00:00:00,2024-01-01
```

**Data Sources**:
- **API**: THORChain Midgard API
- **Affiliate IDs**: `ss`, `thor1z8s0yk6q86nqwsc2gagv4n9yt9c0hk9qtszt0p`
- **Coverage**: All THORChain mainnet swaps

---

### **3. Consolidated Transactions** (`consolidated_affiliate_transactions.csv`)

**Purpose**: Single file combining all protocol data for analysis with 55 bps validation

**Columns**:
```csv
source,chain,tx_hash,block_number,block_timestamp,block_date,input_token,input_amount,input_amount_usd,output_token,output_amount,output_amount_usd,sender,recipient,affiliate_address,expected_fee_bps,actual_fee_bps,affiliate_token,affiliate_amount,affiliate_fee_usd,volume_usd,created_at,created_date
```

**Example Row**:
```csv
cowswap,ethereum,0x0840bba848e991cdcfbf2b71b8e1cb94fb72d6343ad4bb182f7ee1c48612221d,15000000,1640995200,2022-01-01,UNI-V2,3000.0,69948.00,USDC,56980.0,56980.00,0x123...,0xdef...,0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be,55,55,WETH,0.133,454.00,69948.00,2024-01-01 00:00:00,2024-01-01
```

---

### **4. Block Trackers** (`block_trackers/`)

**Purpose**: Track scanning progress to prevent duplicate work

**Files**:
- `cowswap_block_tracker.csv` - CoW Swap scanning progress
- `thorchain_block_tracker.csv` - THORChain scanning progress
- `portals_block_tracker.csv` - Portals scanning progress

**Structure**:
```csv
chain,last_processed_block,last_processed_date,total_transactions_processed,last_error,last_error_date
ethereum,15000000,2024-01-01,1250,,,
polygon,25000000,2024-01-01,890,,,
```

---

## Data Relationships

### **Transaction Flow**
```
1. User initiates swap → 2. Protocol executes → 3. Affiliate fee calculated → 4. Fee sent to ShapeShift → 5. Listener captures → 6. CSV storage → 7. Analysis ready
```

### **Cross-Protocol Analysis**
- **Volume Comparison**: Compare affiliate revenue across protocols
- **Chain Performance**: Identify most profitable chains
- **User Behavior**: Track user patterns and preferences
- **Fee Optimization**: Analyze fee structures and rates

---

## Data Quality & Validation

### **Required Fields**
- ✅ **Always Present**: tx_hash, block_number, affiliate_fee_usd, volume_usd
- ⚠️ **Sometimes Missing**: gas_used, gas_price (depends on chain)
- 🔍 **Calculated**: created_date (derived from timestamp)

### **55 BPS Validation**
- **Expected Rate**: 55 basis points (0.55%) - ShapeShift standard affiliate rate
- **Actual Rate**: What was actually charged and collected
- **Validation Logic**: Compare expected vs actual to detect rate manipulation
- **Security Purpose**: Prevent modified clients from bypassing affiliate fees
- **Alert Threshold**: Flag any transactions with < 50 bps or 0% fees

### **Data Validation Rules**
1. **Affiliate fees must be > 0** for valid transactions
2. **Volume must be > affiliate fee** (logical consistency)
3. **Timestamps must be recent** (within last 30 days for active scanning)
4. **Addresses must be valid** (checksum format for EVM chains)
5. **Expected vs Actual BPS must match** (55 bps standard, detect rate manipulation)
6. **Fee rate validation** (prevent 0% fee bypass attempts)

### **Error Handling**
- **Missing data**: Logged and skipped, not stored
- **Invalid amounts**: Converted to 0, logged as warning
- **API failures**: Retried with exponential backoff
- **Rate limits**: Automatic delay and retry

---

## Data Access Patterns

### **Common Queries**
```python
# Total affiliate revenue by protocol
df.groupby('source')['affiliate_fee_usd'].sum()

# Daily revenue trends
df.groupby('created_date')['affiliate_fee_usd'].sum()

# Top performing chains
df.groupby('chain')['volume_usd'].sum().sort_values(ascending=False)

# User transaction patterns
df.groupby('sender')['volume_usd'].agg(['count', 'sum'])
```

### **Performance Considerations**
- **File sizes**: Each CSV typically < 100MB for 1 year of data
- **Query speed**: Use pandas for analysis, avoid loading entire files
- **Storage**: CSV format is human-readable and version-control friendly
- **Backup**: Simple file copy operations for data preservation

---

## Fraud Detection & Monitoring

### **55 BPS Rate Validation**
1. **Expected Rate Tracking**: Monitor that all transactions use 55 bps
2. **Anomaly Detection**: Flag transactions with 0% or significantly reduced fees
3. **Client Fingerprinting**: Track which clients/protocols are generating transactions
4. **Rate Manipulation Alerts**: Immediate notification of fee bypass attempts

### **Security Monitoring**
1. **Fee Rate Changes**: Track any deviations from 55 bps standard
2. **Volume Anomalies**: Detect unusual transaction patterns
3. **Address Monitoring**: Watch for suspicious affiliate address changes
4. **Protocol Compliance**: Ensure all protocols enforce affiliate rates

## Future Enhancements

### **Planned Additions**
1. **JSON export** for API consumption
2. **Database integration** for high-volume scenarios
3. **Real-time streaming** via WebSocket connections
4. **Automated reporting** with scheduled exports
5. **Real-time fraud detection** with automated alerts

### **Data Retention**
- **Current**: Keep all historical data
- **Future**: Implement configurable retention policies
- **Archival**: Compress old data, maintain accessibility

---

**Status**: 🟢 **Production Ready** - Data structure stable and well-documented
