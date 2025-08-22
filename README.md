# ShapeShift Affiliate Listener

A comprehensive system for monitoring and tracking ShapeShift affiliate fee events across multiple blockchain protocols and chains.

## Affiliate Address Configuration

### Critical Address Corrections Made

- ✅ **ButterSwap**: Now correctly isolated to use only d3f8a3 address
- ✅ **Portals**: Corrected to use Base Safe address (`0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502`)
- ✅ **General Tracking**: Updated to use proper chain-specific Safe addresses
- ✅ **Chainflip**: Added new affiliate address (`cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi`)

### Affiliate Address Mapping Table

**Protocol-Specific Affiliate Addresses:**

| Protocol | Chain | Affiliate Address | Source | Notes |
|----------|-------|-------------------|---------|-------|
| **ButterSwap** | All | `0x35339070f178dC4119732982C23F5a8d88D3f8a3` | Config | **ONLY protocol using d3f8a3 address** |
| **Portals** | All | `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502` | Config | Portals bridge affiliate |
| **Relay** | Base | `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502` | Config | Relay affiliate on Base chain |
| **CoW Swap** | Base | `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502` | Config | CoW Swap affiliate on Base chain |

**Main Safe Addresses for General Affiliate Tracking (Chain-Specific):**

| Chain | Affiliate Address | Safe Link | Notes |
|-------|-------------------|------------|-------|
| **Ethereum Mainnet** | `0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be` | [Safe Link](https://app.safe.global/home?safe=eth:0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be) | Main Safe for Ethereum |
| **Base** | `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502` | [Safe Link](https://app.safe.global/transactions/history?safe=base:0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502) | Main Safe for Base |

## Key Summary

**All listener files in the `shapeshift-listener` repository now use the corrected addresses:**

- ✅ **d3f8a3 is isolated to ButterSwap ONLY**
- ✅ **Portals uses the correct Base Safe address**
- ✅ **General affiliate tracking uses chain-specific Safe addresses**
- ✅ **Cross-chain protocols use their native address formats**
- ✅ **No more hardcoded d3f8a3 in non-ButterSwap listeners**
