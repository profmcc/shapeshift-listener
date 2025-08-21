# Chainflip API Listener - Setup Guide

## 🎯 **New Approach: Official Chainflip APIs**

Instead of the broken web scraping approach, this new listener uses the **official Chainflip Mainnet APIs** to collect real transaction data directly from the blockchain.

**API Repository**: [https://github.com/chainflip-io/chainflip-mainnet-apis](https://github.com/chainflip-io/chainflip-mainnet-apis)

---

## 🚀 **Quick Start**

### **1. Run Chainflip APIs Locally**

```bash
# Clone the official Chainflip APIs repository
git clone https://github.com/chainflip-io/chainflip-mainnet-apis.git
cd chainflip-mainnet-apis

# Start the APIs with Docker
docker compose up -d

# Wait for node to sync, then start APIs
docker compose up -d
```

### **2. Test the New Listener**

```bash
# Run the API-based listener
python csv_chainflip_api_listener.py
```

---

## 🔧 **Configuration**

### **Environment Variables**

Create a `.env` file with:

```bash
# Chainflip API endpoints (defaults to localhost)
CHAINFLIP_API_URL=http://localhost:10997
CHAINFLIP_NODE_WS=ws://localhost:9944

# Optional: CoinMarketCap API for price data
COINMARKETCAP_API_KEY=your_api_key_here
```

### **Default Endpoints**

- **Broker API**: `http://localhost:10997`
- **LP API**: `http://localhost:10589`
- **Node WebSocket**: `ws://localhost:9944`

---

## 📡 **API Methods Used**

### **Broker Information**
- `broker_getInfo` - Get broker details
- `broker_getTransactions` - Get recent transactions
- `broker_getSwaps` - Get recent swaps
- `broker_getFees` - Get fee information

### **Data Collection**
The listener automatically:
1. **Queries each ShapeShift broker** for recent activity
2. **Collects transaction data** from multiple API endpoints
3. **Standardizes the data** into CSV format
4. **Stores raw API responses** for debugging

---

## 📊 **Data Structure**

### **CSV Output**
- **File**: `csv_data/chainflip_api_transactions.csv`
- **Format**: Standardized transaction records
- **Fields**: 25+ columns including raw API responses

### **Sample Data**
```csv
transaction_id,broker_address,broker_name,swap_type,source_asset,destination_asset,swap_amount,output_amount,broker_fee_amount,broker_fee_asset,source_chain,destination_chain,transaction_hash,block_number,swap_state,timestamp,scraped_at,source_asset_name,destination_asset_name,broker_fee_asset_name,broker_fee_usd,volume_usd,expected_fee_bps,actual_fee_bps,affiliate_fee_usd,created_at,created_date,api_method,raw_response
```

---

## 🔍 **Monitoring ShapeShift Brokers**

### **Known Broker Addresses**
1. **ShapeShift Broker 1**: `cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi`
2. **ShapeShift Broker 2**: `cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8`

### **What We Monitor**
- **Swap transactions** between different assets
- **Broker fee collection** and affiliate revenue
- **Transaction volumes** and success rates
- **Cross-chain activity** and performance

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. API Not Running**
```bash
# Check if APIs are running
docker compose ps

# View logs
docker compose logs -f
```

#### **2. Connection Refused**
```bash
# Verify ports are accessible
curl http://localhost:10997
curl http://localhost:10589
```

#### **3. No Data Found**
- **Check broker addresses** are correct
- **Verify API endpoints** are responding
- **Look for recent activity** on Chainflip

### **Debug Mode**
The listener includes comprehensive logging:
- **API request/response details**
- **Data processing steps**
- **Error handling and recovery**

---

## 📈 **Production Deployment**

### **Local Development**
```bash
# Run with custom settings
CHAINFLIP_API_URL=http://your-api-server:10997 python csv_chainflip_api_listener.py
```

### **Scheduled Monitoring**
```bash
# Add to crontab for regular monitoring
0 */6 * * * cd /path/to/listener && python csv_chainflip_api_listener.py
```

### **Docker Deployment**
```bash
# Run listener in container
docker run -d \
  -e CHAINFLIP_API_URL=http://your-api:10997 \
  -v /path/to/csv_data:/app/csv_data \
  your-listener-image
```

---

## 🔄 **Integration with Other Listeners**

### **Master Runner Compatibility**
This listener follows the same interface as other working listeners:
- **CSV output format** matches existing structure
- **Error handling** follows project standards
- **Logging format** consistent with other listeners

### **Data Consolidation**
- **Same CSV structure** as other protocols
- **Compatible with existing** analysis tools
- **Ready for master runner** integration

---

## 🎉 **Benefits of API Approach**

### **✅ Advantages**
- **Real-time data** from official sources
- **No web scraping** dependencies
- **Structured API responses** with proper error handling
- **Scalable architecture** for production use
- **Official support** from Chainflip team

### **🔄 Migration Path**
1. **Replace broken web scraper** with API listener
2. **Test with local APIs** for development
3. **Deploy to production** with remote API endpoints
4. **Monitor and optimize** based on real usage

---

## 📚 **Next Steps**

### **Immediate Actions**
1. **Test locally** with Docker APIs
2. **Verify data collection** from ShapeShift brokers
3. **Integrate with master runner** for production
4. **Monitor performance** and optimize

### **Future Enhancements**
- **Real-time WebSocket connections** for live updates
- **Price integration** for USD calculations
- **Advanced filtering** and querying capabilities
- **Automated alerts** for significant transactions

---

## 🔗 **Resources**

- **Official APIs**: [https://github.com/chainflip-io/chainflip-mainnet-apis](https://github.com/chainflip-io/chainflip-mainnet-apis)
- **Chainflip Documentation**: [https://docs.chainflip.io/](https://docs.chainflip.io/)
- **API Endpoints**: Local development setup guide above

---

**🎯 Status: READY FOR TESTING - API-based approach replaces broken web scraping**
