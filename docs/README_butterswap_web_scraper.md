# ButterSwap Web Scraper

A web-based scraper for extracting transaction data from the [ButterSwap Explorer](https://explorer.butterswap.io/en) interface. This scraper is designed to handle copy-paste operations for full addresses and transaction details.

## Features

- **Web Interface Scraping**: Extracts data directly from the ButterSwap explorer website
- **Copy-Paste Address Handling**: Uses clipboard operations to get full addresses
- **Multi-Chain Support**: Supports Ethereum, Polygon, Optimism, Arbitrum, Base, Avalanche, and BSC
- **ShapeShift Affiliate Detection**: Automatically identifies transactions involving ShapeShift affiliate addresses
- **Database Storage**: Stores scraped data in SQLite database with proper indexing
- **Flexible Configuration**: Configurable chain selection and transaction limits

## Prerequisites

### System Requirements
- Python 3.8+
- Chrome browser installed
- ChromeDriver (automatically managed by Selenium)

### Python Dependencies
Install required packages:

```bash
pip install -r scripts/requirements_butterswap_scraper.txt
```

Or install individually:

```bash
pip install selenium==4.15.2 pyperclip==1.8.2 web3==6.11.3 eth-abi==4.2.1 requests==2.31.0
```

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/profmcc/shapeshift-affiliate-tracker.git
   cd shapeshift-affiliate-tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r scripts/requirements_butterswap_scraper.txt
   ```

3. **Verify installation**:
   ```bash
   python scripts/test_butterswap_scraper.py
   ```

## Usage

### Basic Usage

Run the scraper with default settings (Ethereum chain, 100 transactions):

```bash
python listeners/butterswap_web_scraper.py
```

### Advanced Usage

**Scrape specific chains:**
```bash
python listeners/butterswap_web_scraper.py --chains ethereum polygon --max-tx 200
```

**Run in headless mode:**
```bash
python listeners/butterswap_web_scraper.py --chains ethereum --max-tx 50 --headless
```

**Scrape all supported chains:**
```bash
python listeners/butterswap_web_scraper.py --chains ethereum polygon optimism arbitrum base avalanche bsc --max-tx 100
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--chains` | Chains to scrape (space-separated) | `ethereum` |
| `--max-tx` | Maximum transactions per chain | `100` |
| `--headless` | Run in headless mode | `False` |

## How It Works

### 1. Web Navigation
- Opens Chrome browser and navigates to the ButterSwap explorer
- Automatically selects the specified blockchain network
- Waits for page content to load

### 2. Transaction Detection
- Scans the page for transaction elements
- Extracts basic transaction information (hash, addresses, tokens, amounts)
- Identifies ShapeShift affiliate transactions

### 3. Address Copy-Paste
- Clicks on address elements to select them
- Uses keyboard shortcuts (Cmd+C) to copy addresses to clipboard
- Retrieves full addresses from clipboard for accurate data

### 4. Data Processing
- Parses timestamps (relative and absolute)
- Validates Ethereum addresses
- Calculates affiliate fees and volumes

### 5. Database Storage
- Stores transactions in SQLite database
- Prevents duplicate entries
- Creates indexes for fast queries

## Database Schema

The scraper creates a `butterswap_web_transactions` table with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `chain` | TEXT | Blockchain network |
| `tx_hash` | TEXT | Transaction hash |
| `block_number` | INTEGER | Block number |
| `block_timestamp` | INTEGER | Block timestamp (Unix) |
| `from_address` | TEXT | Sender address |
| `to_address` | TEXT | Recipient address |
| `token_in` | TEXT | Input token |
| `token_out` | TEXT | Output token |
| `amount_in` | TEXT | Input amount |
| `amount_out` | TEXT | Output amount |
| `fee_amount` | TEXT | Fee amount |
| `fee_token` | TEXT | Fee token |
| `affiliate_address` | TEXT | ShapeShift affiliate address |
| `affiliate_fee_usd` | REAL | Affiliate fee in USD |
| `volume_usd` | REAL | Transaction volume in USD |
| `token_in_name` | TEXT | Input token name |
| `token_out_name` | TEXT | Output token name |
| `status` | TEXT | Transaction status |
| `explorer_url` | TEXT | Link to explorer |
| `scraped_at` | INTEGER | Scraping timestamp |

## ShapeShift Affiliate Addresses

The scraper automatically detects transactions involving these ShapeShift affiliate addresses:

| Chain | Address |
|-------|---------|
| Ethereum | `0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be` |
| Polygon | `0xB5F944600785724e31Edb90F9DFa16dBF01Af000` |
| Optimism | `0x6268d07327f4fb7380732dc6d63d95F88c0E083b` |
| Arbitrum | `0x38276553F8fbf2A027D901F8be45f00373d8Dd48` |
| Base | `0x9c9aA90363630d4ab1D9dbF416cc3BBC8d3Ed502` |
| Avalanche | `0x74d63F31C2335b5b3BA7ad2812357672b2624cEd` |
| BSC | `0x8b92b1698b57bEDF2142297e9397875ADBb2297E` |

## Testing

Run the test suite to verify functionality:

```bash
python scripts/test_butterswap_scraper.py
```

Tests cover:
- Scraper initialization
- Database setup
- Address validation
- Timestamp parsing
- Affiliate detection

## Troubleshooting

### Common Issues

**ChromeDriver not found:**
```bash
# Install ChromeDriver via Homebrew (macOS)
brew install chromedriver

# Or download manually from: https://chromedriver.chromium.org/
```

**Selenium connection errors:**
- Ensure Chrome browser is installed
- Check if Chrome is up to date
- Try running without `--headless` flag first

**Address copy-paste not working:**
- Ensure pyperclip is properly installed
- Check clipboard permissions on your system
- The scraper will fall back to direct text extraction

**Page loading timeouts:**
- Increase delays in the scraper code
- Check internet connection
- Verify the explorer URL is accessible

### Debug Mode

For debugging, modify the scraper to run without headless mode and add more logging:

```python
# In butterswap_web_scraper.py
logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG level
```

## Performance Considerations

- **Rate Limiting**: Built-in delays prevent overwhelming the explorer
- **Batch Processing**: Processes transactions in configurable batches
- **Database Indexing**: Optimized queries with proper indexes
- **Memory Management**: Processes transactions one at a time

## Security Notes

- The scraper only reads publicly available data
- No private keys or sensitive information is accessed
- Uses read-only database operations for safety
- Respects website terms of service

## Contributing

To improve the scraper:

1. **Add new chains**: Update `supported_chains` and `shapeshift_affiliates`
2. **Enhance parsing**: Modify `extract_transaction_data` method
3. **Improve detection**: Update `is_shapeshift_affiliate_transaction` logic
4. **Add features**: Extend database schema and processing logic

## License

This project is part of the ShapeShift Affiliate Tracker and follows the same licensing terms.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test output for errors
3. Check the logs for detailed error messages
4. Verify the Butterswap explorer is accessible
