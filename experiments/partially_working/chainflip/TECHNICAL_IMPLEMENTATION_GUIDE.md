# 🔧 Chainflip Technical Implementation Guide

## 📋 **Overview**
This document provides detailed technical information about the Chainflip affiliate listener implementation, including architecture, code structure, and troubleshooting.

## 🏗️ **Architecture**

### **System Components**
1. **Chainflip Node Connection**: Direct JSON-RPC communication
2. **Data Collection Layer**: Multiple RPC method implementations
3. **Pattern Matching Engine**: ShapeShift transaction detection logic
4. **Data Export System**: CSV export and logging
5. **Error Handling**: Comprehensive error management and reporting

### **Data Flow**
```
Chainflip Node → RPC Methods → Data Processing → Pattern Matching → CSV Export
```

### **Network Topology**
- **Local Node**: `http://localhost:9944` (Chainflip mainnet)
- **Protocol**: JSON-RPC 2.0
- **Authentication**: None required for public methods
- **Rate Limiting**: Built-in delays between requests

## 💻 **Code Structure**

### **Core Classes and Functions**

#### **RPC Communication**
```python
def make_rpc_call(method, params=None):
    """Make a JSON-RPC call to the Chainflip node"""
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method
    }
    if params:
        payload["params"] = params
    
    response = requests.post("http://localhost:9944", json=payload, timeout=10)
    # Process response and return result
```

#### **ShapeShift Detection**
```python
def search_for_shapeshift_transactions(data, data_type, index=None):
    """Search for ShapeShift transactions based on explorer format"""
    matches = []
    
    # Search for known broker addresses
    shapeshift_broker = "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi"
    if shapeshift_broker in json.dumps(data):
        matches.append(f"Found ShapeShift broker {shapeshift_broker[:20]}...")
    
    # Search for text patterns
    if 'shapeshift' in json.dumps(data).lower():
        matches.append("Found 'shapeshift' text")
    
    return matches
```

#### **Data Export**
```python
def save_transactions_to_csv(transactions, csv_file):
    """Save transactions to CSV file"""
    headers = ['timestamp', 'method', 'data_type', 'index', 'matches', 'raw_data']
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)
```

### **File Organization**
```
chainflip/
├── README.md                           # Main documentation
├── TECHNICAL_IMPLEMENTATION_GUIDE.md  # This file
├── CHAINFLIP_INVESTIGATION_SUMMARY.md # Investigation results
├── csv_chainflip_api_listener.py      # Main API listener
├── chainflip_transaction_listener.py  # Transaction detection
├── chainflip_debug_listener.py        # Debug tool
├── chainflip_final_listener.py        # Final investigation
└── *.csv                              # Data export files
```

## 🔌 **RPC Methods**

### **Working Methods**
| Method | Parameters | Status | Description |
|--------|------------|--------|-------------|
| `cf_lp_get_order_fills` | `[]` | ✅ Working | LP order fill data |
| `cf_get_transaction_screening_events` | `[]` | ✅ Working | Transaction screening |
| `cf_all_open_deposit_channels` | `[]` | ✅ Working | Open deposit channels |
| `cf_monitoring_pending_broadcasts` | `[]` | ✅ Working | Pending broadcasts |
| `cf_monitoring_pending_swaps` | `[]` | ✅ Working | Pending swaps |

### **Failed Methods**
| Method | Parameters | Status | Error | Description |
|--------|------------|--------|-------|-------------|
| `cf_scheduled_swaps` | `[]` | ❌ Failed | Parameter errors | Scheduled swaps |
| `cf_prewitness_swaps` | `[]` | ❌ Failed | Parameter errors | Prewitness swaps |
| `cf_pool_orders` | `[]` | ❌ Failed | Parameter errors | Pool orders |

### **Error Patterns**
1. **`'No more params'`**: Method expects no parameters
2. **`'Expected a valid asset specifier'`**: Method expects asset parameters
3. **`'Method not found'`**: Method doesn't exist

## 🎯 **Detection Logic**

### **Pattern Matching Strategy**
1. **Address Matching**: Search for known ShapeShift broker addresses
2. **Text Pattern Matching**: Search for "shapeshift", "affiliate", "commission"
3. **Data Structure Analysis**: Examine data for transaction patterns
4. **Multi-Method Coverage**: Test all available RPC methods

### **Broker Addresses**
```python
shapeshift_brokers = [
    "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",  # Primary
    "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"   # Secondary
]
```

### **Search Terms**
```python
search_terms = [
    'shapeshift', 'shape shift', 'ss:', 'ss:', 
    'broker', 'affiliate', 'treasury', 'dao', 
    'protocol', 'fee', 'commission', 'swap'
]
```

## 📊 **Data Structures**

### **Transaction Record Format**
```python
transaction = {
    'timestamp': datetime.now().isoformat(),
    'method': 'cf_scheduled_swaps',
    'data_type': 'scheduled_swaps',
    'index': i,
    'matches': matches,
    'raw_data': json.dumps(swap)[:500],
    'detection_method': 'scheduled_swaps_no_params'
}
```

### **CSV Export Format**
| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | ISO timestamp | `2025-08-20T15:30:00` |
| `method` | RPC method used | `cf_scheduled_swaps` |
| `data_type` | Type of data | `scheduled_swaps` |
| `index` | Data index | `0` |
| `matches` | Detection matches | `['Found broker...']` |
| `raw_data` | Raw data (truncated) | `{"key": "value"...}` |
| `detection_method` | Detection method used | `scheduled_swaps_no_params` |

## 🚨 **Error Handling**

### **Common Errors and Solutions**

#### **Connection Errors**
```python
try:
    response = requests.post(url, json=payload, timeout=10)
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection failed: {e}")
    # Handle connection failure
```

#### **RPC Errors**
```python
if 'error' in result:
    print(f"❌ API Error: {method} - {result['error']}")
    # Handle RPC error
```

#### **Data Processing Errors**
```python
try:
    data_str = json.dumps(data)
except Exception as e:
    print(f"❌ Error processing data: {e}")
    # Handle processing error
```

### **Error Recovery Strategies**
1. **Retry Logic**: Implement exponential backoff for failed requests
2. **Fallback Methods**: Try alternative RPC methods if primary fails
3. **Data Validation**: Validate data before processing
4. **Graceful Degradation**: Continue operation with partial data

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Chainflip node endpoint
CHAINFLIP_API_URL=http://localhost:9944

# Request timeout (seconds)
REQUEST_TIMEOUT=10

# Rate limiting delay (seconds)
RATE_LIMIT_DELAY=0.1
```

### **Configuration File**
```python
config = {
    'node_url': os.getenv('CHAINFLIP_API_URL', 'http://localhost:9944'),
    'timeout': int(os.getenv('REQUEST_TIMEOUT', 10)),
    'rate_limit_delay': float(os.getenv('RATE_LIMIT_DELAY', 0.1)),
    'max_retries': 3,
    'csv_directory': 'csv_data'
}
```

## 📈 **Performance Optimization**

### **Rate Limiting**
```python
import time

def make_rpc_call_with_rate_limit(method, params=None):
    result = make_rpc_call(method, params)
    time.sleep(0.1)  # Rate limiting
    return result
```

### **Batch Processing**
```python
def process_multiple_methods(methods):
    results = []
    for method in methods:
        result = make_rpc_call(method)
        if result:
            results.append(result)
        time.sleep(0.1)  # Rate limiting
    return results
```

### **Data Caching**
```python
import functools

@functools.lru_cache(maxsize=128)
def cached_rpc_call(method, params=None):
    return make_rpc_call(method, params)
```

## 🧪 **Testing and Debugging**

### **Debug Mode**
```python
DEBUG_MODE = True

def debug_log(message):
    if DEBUG_MODE:
        print(f"🔍 DEBUG: {message}")
```

### **Data Validation**
```python
def validate_data(data):
    """Validate data structure and content"""
    if not isinstance(data, dict):
        return False
    
    required_fields = ['timestamp', 'method', 'data_type']
    return all(field in data for field in required_fields)
```

### **Performance Monitoring**
```python
import time

def timed_rpc_call(method, params=None):
    start_time = time.time()
    result = make_rpc_call(method, params)
    end_time = time.time()
    
    if DEBUG_MODE:
        print(f"⏱️ {method} took {end_time - start_time:.3f} seconds")
    
    return result
```

## 🔍 **Troubleshooting Guide**

### **Common Issues**

#### **1. Connection Failed**
- **Symptom**: `Connection failed: [Errno 61] Connection refused`
- **Cause**: Chainflip node not running
- **Solution**: Start Chainflip mainnet node

#### **2. RPC Method Not Found**
- **Symptom**: `Method not found`
- **Cause**: Method name incorrect or not available
- **Solution**: Check method name and node version

#### **3. Parameter Errors**
- **Symptom**: `Invalid params` or `Expected a valid asset specifier`
- **Cause**: Wrong parameters for RPC method
- **Solution**: Check method documentation and test parameters

#### **4. No Data Found**
- **Symptom**: Methods return empty results
- **Cause**: No data available or wrong parameters
- **Solution**: Verify network status and method usage

### **Debugging Steps**
1. **Check Node Status**: Verify Chainflip node is running and synced
2. **Test Basic Methods**: Test simple methods like `system_health`
3. **Verify Parameters**: Check method parameter requirements
4. **Examine Error Messages**: Analyze specific error details
5. **Check Network**: Verify network connectivity and firewall settings

## 📚 **API Reference**

### **Chainflip RPC Methods**
- **System Methods**: `system_health`, `system_syncState`
- **Chain Methods**: `chain_getBlock`, `chain_getBlockHash`
- **State Methods**: `state_getMetadata`, `state_getRuntimeVersion`
- **Custom Methods**: `cf_*` methods for Chainflip-specific functionality

### **HTTP Status Codes**
- **200**: Success
- **400**: Bad Request
- **404**: Method Not Found
- **500**: Internal Server Error

### **JSON-RPC Error Codes**
- **-32601**: Method not found
- **-32602**: Invalid params
- **-32603**: Internal error
- **-32700**: Parse error

## 🔮 **Future Enhancements**

### **Planned Improvements**
1. **WebSocket Support**: Real-time event subscription
2. **Advanced Pattern Matching**: Machine learning-based detection
3. **Multi-Node Support**: Load balancing across multiple nodes
4. **Data Analytics**: Advanced transaction analysis and reporting

### **Scalability Considerations**
1. **Connection Pooling**: Manage multiple RPC connections
2. **Data Streaming**: Process large datasets efficiently
3. **Distributed Processing**: Scale across multiple machines
4. **Caching Layer**: Implement Redis or similar for data caching

---

**Last Updated**: August 20, 2025  
**Version**: 1.0  
**Status**: Partially Working - Infrastructure Ready, Transaction Detection Failed
