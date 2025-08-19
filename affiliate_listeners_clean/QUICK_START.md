# Quick Start Guide - ShapeShift Affiliate Tracker

## 🚀 Get Running in 5 Minutes

### 1. **Setup Environment**
```bash
# Clone the handoff folder
cd affiliate_listener_handoff

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure API Keys**
```bash
# Copy environment file
cp .env.example .env  # or create .env manually

# Edit .env with your keys:
ALCHEMY_API_KEY=your_alchemy_key_here
INFURA_API_KEY=your_infura_key_here
```

### 3. **Test Individual Listeners**
```bash
# Test CoW Swap listener (Ethereum only)
python csv_cowswap_listener.py --test

# Test THORChain listener
python csv_thorchain_listener.py --test

# Check output in csv_data/ folder
ls csv_data/
```

### 4. **Run Master Runner**
```bash
# Run all listeners together
python csv_master_runner.py

# Check consolidated data
cat csv_data/consolidated_affiliate_transactions.csv | head -5
```

## 📊 What You'll See

### **CSV Output Structure**
```
source,chain,tx_hash,block_number,block_timestamp,block_date,input_token,input_amount,output_token,output_amount,sender,recipient,partner,affiliate_token,affiliate_amount,affiliate_fee_usd,volume_usd,created_at,created_date
cowswap,ethereum,0x123...,15000000,1640995200,2022-01-01,USDC,1000.0,ETH,0.5,0xabc...,0xdef...,cowswap,WETH,0.01,25.50,1000.00,2024-01-01 00:00:00,2024-01-01
```

### **Data Files Created**
- `cowswap_transactions.csv` - CoW Swap affiliate transactions
- `thorchain_transactions.csv` - THORChain affiliate transactions  
- `consolidated_affiliate_transactions.csv` - All protocols combined
- `block_trackers/` - Progress tracking for each protocol

## 🔧 Troubleshooting

### **Common Issues**

#### 1. **API Rate Limits**
```bash
# Check logs for rate limit errors
# Solution: Increase delays in listener config
```

#### 2. **Missing Dependencies**
```bash
# Install missing packages
pip install web3 pandas requests python-dotenv
```

#### 3. **API Key Issues**
```bash
# Verify .env file exists and has correct keys
# Test API connection manually
```

### **Debug Mode**
```bash
# Run with verbose logging
python csv_cowswap_listener.py --debug

# Check log files in current directory
tail -f *.log
```

## 📈 Next Steps

### **Immediate Actions**
1. ✅ **Verify listeners work** with test mode
2. 🔧 **Fix any errors** in logs
3. 📊 **Review sample data** in CSV files
4. 🚀 **Deploy to production** environment

### **Production Checklist**
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups
- [ ] Set up cron jobs for continuous scanning
- [ ] Test error recovery and restart procedures

## 📞 Need Help?

- **Documentation**: See `HANDOFF_DOCUMENTATION.md`
- **Code Issues**: Check GitHub repository
- **Data Questions**: Review CSV structure and examples

---

**Status**: 🟢 **Ready to Run** - All core functionality working
