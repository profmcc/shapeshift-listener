# ThorChain Block 22,470,673 - ShapeShift Affiliate Transaction Found!

## Overview
Successfully found and processed a ShapeShift affiliate transaction in ThorChain block 22,470,673.

## Key Findings

### 🎯 ShapeShift Affiliate Transaction
- **Block Height**: `22,470,673`
- **Date**: `1755630741968723825` (ThorChain timestamp)
- **Memo Pattern**: `=:b:bc1q5mvrqhv5s4yhw0ly5nj3g9v6gxr5w6xy9yegsk:0/10/0:ss:55`
- **Affiliate Pattern**: Ends with `:ss:55` (confirming ShapeShift affiliate)

### 📊 Transaction Details
- **From**: `48,800,000,000 BTC` (48.8 BTC)
- **To**: `209,213,486 BTC` (0.209 BTC)
- **Pool**: `BTC` (Bitcoin)
- **Affiliate Address**: `thor122h9hlrugzdny9ct95z6g7afvpzu34s73uklju`
- **Affiliate Fee Token**: `BTC`

### 🔍 Additional ShapeShift Affiliate Transaction
Also found another ShapeShift affiliate transaction:
- **Block**: `22,457,158`
- **Memo**: `=:r:thor1dcjjcaeux4u7ukrcvlhjjmeyu9r3m48gxkfq6f:6869015443:ss:55`
- **Pattern**: Also ends with `:ss:55`

## Technical Implementation

### API Search Strategy
1. **Direct Block API**: Failed (501 error)
2. **Recent Actions**: Limited to recent blocks
3. **Offset-based Search**: Successfully found target block at offset 2000

### Key Discovery
- **Offset 2000**: Contains block 22,470,673
- **Memo Pattern**: `:ss:55` indicates ShapeShift affiliate with 55 basis points
- **Asset Patterns**: 
  - `=:b:` = Bitcoin transactions
  - `=:r:` = RUNE transactions

### Data Saved
Successfully saved both transactions to:
- **File**: `csv_data/transactions/thorchain_transactions.csv`
- **Status**: 3 rows (header + 2 transactions)

## Results Summary

✅ **SUCCESS**: Found 1 ShapeShift affiliate transaction in block 22,470,673

**Transaction Details**:
- **Block**: 22,470,673
- **Type**: Bitcoin swap with ShapeShift affiliate
- **Volume**: 48.8 BTC
- **Affiliate Pattern**: `:ss:55` (55 basis points)

**Additional Findings**:
- **Block 22,457,158**: RUNE swap with ShapeShift affiliate (`:ss:55`)
- **Pattern Confirmation**: `:ss:` memo pattern consistently identifies ShapeShift affiliate transactions

## Pattern Analysis

### ShapeShift Affiliate Memo Patterns
1. **`:ss:0`** - ShapeShift affiliate with 0 basis points (block 22,456,113)
2. **`:ss:55`** - ShapeShift affiliate with 55 basis points (blocks 22,470,673, 22,457,158)

### Asset Type Indicators
- **`=:b:`** = Bitcoin transactions
- **`=:r:`** = RUNE transactions  
- **`=:THOR.TCY:`** = THORChain TCY transactions

## Next Steps
- Use `:ss:` memo pattern detection in main ThorChain listener
- Implement offset-based historical data retrieval
- Consider 55 basis points as standard ShapeShift affiliate fee
- Expand search to find more historical affiliate transactions
