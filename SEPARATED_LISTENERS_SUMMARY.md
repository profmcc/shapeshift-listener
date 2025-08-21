# Separated CSV Listeners - Complete Structure

## 🎯 **Overview**

I've successfully separated the logic for each listener and added comprehensive comments to ensure everything makes sense. Each listener is now completely independent and can be run separately or together via the master runner.

## 📁 **File Structure**

### **Individual Listeners (Completely Separated)**

1. **`csv_portals_listener.py`** - Portals cross-chain bridge affiliate fees
2. **`csv_cowswap_listener.py`** - CoW Swap DEX aggregator affiliate fees  
3. **`csv_thorchain_listener.py`** - THORChain cross-chain swap affiliate fees
4. **`csv_relay_listener.py`** - Relay protocol affiliate fees

### **Master Runner**

- **`csv_master_runner.py`** - Orchestrates all listeners and consolidates data

## 🔧 **Each Listener is Completely Independent**

### **1. CSVPortalsListener** (`csv_portals_listener.py`)

**Purpose:** Tracks ShapeShift affiliate fees from Portals cross-chain bridge transactions

**Key Features:**
- ✅ **Completely separated** from other listeners
- ✅ **Multi-chain support** (Ethereum, Polygon, Arbitrum, Optimism, Base)
- ✅ **Alchemy RPC integration** for reliable blockchain access
- ✅ **Smart affiliate detection** using transaction log analysis
- ✅ **CSV-based storage** with proper headers and structure
- ✅ **Block tracking** to avoid re-scanning processed blocks

**What it does:**
1. Connects to multiple EVM chains via Alchemy RPC providers
2. Monitors Portals router contracts for transaction events
3. Filters for ShapeShift affiliate address involvement
4. Extracts input/output token data and affiliate fee information
5. Saves everything to CSV files for easy analysis

**Configuration:**
- **Portals Router:** `0xbf5A7F3629fB325E2a8453D595AB103465F75E62`
- **ShapeShift Affiliates:** Chain-specific addresses for each supported network
- **Block Scanning:** Configurable chunk sizes and delays per chain

---

### **2. CSVCowSwapListener** (`csv_cowswap_listener.py`)

**Purpose:** Tracks ShapeShift affiliate fees from CoW Swap DEX aggregator trades

**Key Features:**
- ✅ **Completely separated** from other listeners
- ✅ **Multi-chain support** across all major EVM chains
- ✅ **Event decoding** for CoW Swap trade events
- ✅ **Token metadata caching** to avoid repeated lookups
- ✅ **Affiliate fee detection** in trade transactions
- ✅ **CSV-based storage** with comprehensive trade data

**What it does:**
1. Connects to multiple EVM chains via RPC providers
2. Monitors CoW Swap contracts for trade events
3. Filters for ShapeShift affiliate addresses
4. Extracts trade data, fees, and affiliate information
5. Saves everything to CSV files for easy analysis

**Configuration:**
- **CoW Swap Contract:** `0x9008D19f58AAbD9eD0D60971565AA8510560ab41`
- **Event Signatures:** Trade, order, and transfer event detection
- **Token Metadata:** Automatic name, symbol, and decimal extraction

---

### **3. CSVThorChainListener** (`csv_thorchain_listener.py`)

**Purpose:** Tracks ShapeShift affiliate fees from THORChain cross-chain swaps

**Key Features:**
- ✅ **Completely separated** from other listeners
- ✅ **Midgard API integration** for THORChain data
- ✅ **Affiliate ID detection** using multiple identifiers
- ✅ **Swap metadata extraction** including fees and amounts
- ✅ **CSV-based storage** with comprehensive swap data
- ✅ **Rate limiting** to respect API constraints

**What it does:**
1. Connects to THORChain's Midgard API
2. Fetches swap actions and filters for ShapeShift affiliate IDs
3. Extracts affiliate fee data and transaction details
4. Saves everything to CSV files for easy analysis

**Configuration:**
- **Midgard API:** `https://midgard.ninerealms.com`
- **ShapeShift Affiliate IDs:** `['ss', 'thor1z8s0yk6q86nqwsc2gagv4n9yt9c0hk9qtszt0p']`
- **API Rate Limiting:** Configurable delays between requests

---

### **4. CSVRelayListener** (`csv_relay_listener.py`)

**Purpose:** Tracks ShapeShift affiliate fees from Relay protocol transactions

**Key Features:**
- ✅ **Completely separated** from other listeners
- ✅ **Multi-chain support** across EVM networks
- ✅ **Relay router monitoring** for affiliate transactions
- ✅ **Affiliate fee detection** in relay operations
- ✅ **CSV-based storage** with relay-specific data fields

**What it does:**
1. Connects to multiple EVM chains via RPC providers
2. Monitors Relay router contracts for transaction events
3. Filters for ShapeShift affiliate address involvement
4. Extracts relay-specific data and affiliate information
5. Saves everything to CSV files for easy analysis

---

## 🚀 **Master Runner** (`csv_master_runner.py`)

**Purpose:** Orchestrates all listeners and consolidates data into unified CSV files

**Key Features:**
- ✅ **Independent listener execution** - each runs separately
- ✅ **Protocol-specific parameter handling** (e.g., THORChain uses API calls, others use block scanning)
- ✅ **Data consolidation** from all protocols into unified format
- ✅ **Comprehensive statistics** across all sources
- ✅ **Error handling** - one listener failure doesn't affect others

**What it does:**
1. Initializes all protocol-specific listeners
2. Runs each listener independently to scan for affiliate transactions
3. Consolidates all data into a single CSV file
4. Provides comprehensive statistics across all protocols

**Consolidated Data Fields:**
- `source` - Protocol name (portals, cowswap, thorchain, relay)
- `chain` - Blockchain network
- `tx_hash` - Transaction hash
- `block_number` - Block number
- `block_timestamp` - Unix timestamp
- `block_date` - Human-readable date
- `input_token` - Input token address
- `input_amount` - Input token amount
- `output_token` - Output token address
- `output_amount` - Output token amount
- `affiliate_token` - Affiliate fee token
- `affiliate_amount` - Affiliate fee amount
- `affiliate_fee_usd` - Affiliate fee in USD
- `volume_usd` - Transaction volume in USD

## 🔍 **How to Use**

### **Run Individual Listeners**

```bash
# Portals listener only
python csv_portals_listener.py --blocks 1000

# CoW Swap listener only  
python csv_cowswap_listener.py --blocks 1000

# THORChain listener only
python csv_thorchain_listener.py --max-actions 100 --action-limit 50

# Relay listener only
python csv_relay_listener.py --blocks 1000
```

### **Run All Listeners Together**

```bash
# Run all listeners and consolidate data
python csv_master_runner.py --blocks 1000

# Show statistics only
python csv_master_runner.py --stats-only
```

## 📊 **CSV File Structure**

### **Protocol-Specific Files**
- `portals_transactions.csv` - Portals affiliate transactions
- `cowswap_transactions.csv` - CoW Swap affiliate transactions
- `thorchain_transactions.csv` - THORChain affiliate transactions
- `relay_transactions.csv` - Relay affiliate transactions

### **Block Tracking Files**
- `portals_block_tracker.csv` - Portals block processing status
- `cowswap_block_tracker.csv` - CoW Swap block processing status
- `thorchain_block_tracker.csv` - THORChain processing status
- `relay_block_tracker.csv` - Relay block processing status

### **Consolidated Files**
- `consolidated_affiliate_transactions.csv` - Combined data from all protocols

## ✅ **Benefits of Separation**

1. **Modularity** - Each listener can be developed, tested, and maintained independently
2. **Flexibility** - Run only the protocols you need
3. **Maintainability** - Clear separation of concerns makes debugging easier
4. **Scalability** - Easy to add new protocols without affecting existing ones
5. **Testing** - Each listener can be tested in isolation
6. **Deployment** - Can deploy listeners to different servers if needed

## 🔒 **Data Integrity**

- **No shared state** between listeners
- **Independent CSV files** for each protocol
- **Consolidation process** creates unified view without modifying source data
- **Error isolation** - one listener failure doesn't affect others

## 📝 **Comment Quality**

Each listener includes:
- **File-level documentation** explaining purpose and functionality
- **Class-level documentation** describing the listener's role
- **Method-level documentation** with Args/Returns sections
- **Inline comments** explaining complex logic
- **Configuration comments** explaining settings and addresses
- **Error handling comments** explaining fallback behavior

## 🎉 **Summary**

The system is now completely separated with:
- **4 independent listeners** for different protocols
- **1 master runner** for orchestration
- **Comprehensive commenting** throughout
- **No shared dependencies** between listeners
- **Clear separation of concerns**
- **Easy to understand and maintain**

Each listener can be run independently, making the system highly modular and maintainable!
