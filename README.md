# ShapeShift Affiliate Listener

## Data Persistence Strategy

### CSV Files (Primary)

**All transaction CSVs have consistent columns:**

| Column | Description | Example |
|--------|-------------|---------|
| `tx_hash` | Transaction hash | `0x0840bba848e991cdcfbf2b71b8e1cb94fb72d6343ad4bb182f7ee1c48612221d` |
| `chain` | Blockchain name | `base`, `ethereum`, `polygon` |
| `block_number` | Block number | `15000000` |
| `timestamp` | Block timestamp | `1640995200` |
| `from_address` | Sender address | `0x1234...` |
| `to_address` | Recipient address | `0x5678...` |
| `affiliate_address` | ShapeShift affiliate address | `0x35339070f178dC4119732982C23F5a8d88D3f8a3` |
| `affiliate_fee_amount` | Affiliate fee amount | `0.133` |
| `affiliate_fee_usd` | Affiliate fee in USD | `454.00` |
| `volume_amount` | Transaction volume | `3000.0` |
| `volume_usd` | Volume in USD | `69948.00` |
| `gas_used` | Gas used | `150000` |
| `gas_price` | Gas price | `20000000000` |
| `created_at` | Record creation timestamp | `2024-01-01 00:00:00` |

## Key Summary

**All listener files in the `shapeshift-listener` repository now use the corrected addresses:**

- ✅ **d3f8a3 is isolated to ButterSwap ONLY**
- ✅ **Portals uses the correct Base Safe address**
- ✅ **General affiliate tracking uses chain-specific Safe addresses**
- ✅ **Cross-chain protocols use their native address formats**
- ✅ **No more hardcoded d3f8a3 in non-ButterSwap listeners**
