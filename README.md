# ShapeShift Affiliate Fee Tracker

A comprehensive system for tracking and collecting affiliate fee data from multiple blockchain sources including EVM chains (Ethereum and Polygon), Chainflip, and THORChain.

## Features

- **Multi-chain Support**: Collects data from Ethereum, Polygon, Chainflip, and THORChain
- **Real-time Processing**: Efficient event listening and data collection
- **Comprehensive Database**: SQLite-based storage with merged data from all sources
- **Docker Support**: Containerized deployment with Colima
- **Progress Tracking**: Real-time monitoring and logging

## Project Structure

```
.
├── run_all_listeners.py              # Main data collection script
├── evm_listeners/                    # EVM chain listeners
├── chainflip/                        # Chainflip scraper
├── thorchain/                        # THORChain listener
├── affiliate_fee_listener/           # Core affiliate fee tracking
├── fox_lp_listener/                  # FOX LP pool analysis
├── shapeshift_affiliate_fees_comprehensive.db  # Main database
├── docker-compose.yml                # Docker configuration
├── Dockerfile                        # Container definition
└── requirements.txt                  # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Colima (for containerized deployment)
- Infura API key (for Ethereum access)
- Polygon RPC URL

### Environment Variables

Create a `.env` file with:

```bash
INFURA_API_KEY=your_infura_api_key_here
POLYGON_RPC_URL=https://polygon-rpc.com
```

## Running the Collector with Colima

1. **Start Colima**  
   ```bash
   colima start --cpu 2 --memory 4
   ```

2. **Navigate to your project**  
   ```bash
   cd ~/profmcc/shapeshift-affiliate-tracker
   ```

3. **Bring up the collector**  
   ```bash
   docker compose up -d
   ```

4. **Verify it's running**  
   ```bash
   docker compose ps
   ```

5. **Tail the logs**  
   ```bash
   docker compose logs -f
   ```

6. **Rebuild on changes**  
   ```bash
   docker compose up -d --build
   ```

### Optional: Health Check

The service includes a health check that monitors the collector log file:

```bash
docker compose ps  # shows HEALTH status
```

## Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Data Collection

```bash
python run_all_listeners.py
```

### Individual Components

- **EVM Listener**: `python evm_listeners/run_evm_listener.py`
- **Chainflip Scraper**: `python chainflip/run_chainflip_scraper.py`
- **THORChain Listener**: `python thorchain/run_thorchain_listener.py`

## Data Output

The system generates:

- **Comprehensive Database**: `shapeshift_affiliate_fees_comprehensive.db`
- **Progress Logs**: `comprehensive_collection.log`
- **Individual Chain Data**: Separate databases for each chain
- **CSV/JSON Exports**: Chainflip data in multiple formats

## Monitoring

- Real-time progress tracking
- Performance metrics
- Error handling and retry logic
- Rate limiting protection

## Troubleshooting

### Common Issues

1. **Infura Authentication**: Ensure your Infura API key is valid
2. **Rate Limiting**: The system includes exponential backoff for RPC calls
3. **Database Locks**: SQLite databases are properly handled with connection pooling

### Logs

Check logs for detailed information:

```bash
# Docker logs
docker compose logs -f

# Local logs
tail -f comprehensive_collection.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.