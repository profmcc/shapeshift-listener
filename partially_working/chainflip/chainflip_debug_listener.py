#!/usr/bin/env python3
"""
Chainflip Debug Listener - Examines actual data to find ShapeShift broker activity
"""

import requests
import json
import csv
import time
from datetime import datetime

class ChainflipDebugListener:
    def __init__(self):
        self.node_url = "http://localhost:9944"
        self.csv_file = "chainflip_debug_transactions.csv"
        
        # ShapeShift broker addresses
        self.shapeshift_brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
        ]
        
        # Initialize CSV
        self.init_csv()
        
    def init_csv(self):
        """Initialize CSV file for debug transactions"""
        headers = [
            'timestamp', 'data_type', 'broker_found', 'broker_address', 'data_summary', 'raw_data'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
        print(f"📁 Created debug CSV file: {self.csv_file}")
    
    def make_rpc_call(self, method: str, params=None):
        """Make a JSON-RPC call to the Chainflip node"""
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            payload["params"] = params
            
        try:
            response = requests.post(self.node_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return result['result']
                elif 'error' in result:
                    print(f"❌ API Error: {method} - {result['error']}")
                    return None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def search_for_brokers_in_data(self, data, data_type):
        """Search for ShapeShift brokers in any data structure"""
        broker_matches = []
        
        try:
            # Convert data to string for searching
            data_str = json.dumps(data)
            
            # Check each broker address
            for broker in self.shapeshift_brokers:
                if broker in data_str:
                    broker_matches.append(broker)
            
            if broker_matches:
                print(f"🎯 Found ShapeShift brokers in {data_type}: {broker_matches}")
                
                # Create debug record
                record = {
                    'timestamp': datetime.now().isoformat(),
                    'data_type': data_type,
                    'broker_found': 'YES',
                    'broker_address': ', '.join(broker_matches),
                    'data_summary': f"Found {len(broker_matches)} brokers in {data_type}",
                    'raw_data': data_str[:1000]  # Truncate long data
                }
                
                return record
            else:
                print(f"❌ No ShapeShift brokers found in {data_type}")
                return None
                
        except Exception as e:
            print(f"❌ Error searching {data_type}: {e}")
            return None
    
    def save_debug_record(self, record):
        """Save debug record to CSV"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'timestamp', 'data_type', 'broker_found', 'broker_address', 'data_summary', 'raw_data'
                ])
                writer.writerow(record)
                
        except Exception as e:
            print(f"❌ Error saving debug record: {e}")
    
    def run_debug_scan(self):
        """Run debug scan to find ShapeShift broker activity"""
        print("🚀 Starting Chainflip DEBUG scan to find ShapeShift broker activity...")
        
        debug_records = []
        
        # Method 1: Get LP order fills (this worked before)
        print("\n🔍 Method 1: Examining LP order fills...")
        lp_fills = self.make_rpc_call("cf_lp_get_order_fills", [])
        if lp_fills:
            print(f"   Found {len(lp_fills)} LP order fills")
            record = self.search_for_brokers_in_data(lp_fills, "lp_order_fills")
            if record:
                debug_records.append(record)
                self.save_debug_record(record)
        
        # Method 2: Get transaction screening events (this worked before)
        print("\n🔍 Method 2: Examining transaction screening events...")
        screening_events = self.make_rpc_call("cf_get_transaction_screening_events", [])
        if screening_events:
            print(f"   Found {len(screening_events)} screening events")
            record = self.search_for_brokers_in_data(screening_events, "screening_events")
            if record:
                debug_records.append(record)
                self.save_debug_record(record)
        
        # Method 3: Get current epoch info
        print("\n🔍 Method 3: Examining current epoch...")
        current_epoch = self.make_rpc_call("cf_current_epoch", [])
        if current_epoch:
            print(f"   Current epoch: {current_epoch}")
            record = self.search_for_brokers_in_data(current_epoch, "current_epoch")
            if record:
                debug_records.append(record)
                self.save_debug_record(record)
        
        # Method 4: Get pool info
        print("\n🔍 Method 4: Examining pool info...")
        pool_info = self.make_rpc_call("cf_pool_info", [])
        if pool_info:
            print(f"   Found pool info")
            record = self.search_for_brokers_in_data(pool_info, "pool_info")
            if record:
                debug_records.append(record)
                self.save_debug_record(record)
        
        # Method 5: Get account info for ShapeShift brokers
        print("\n🔍 Method 5: Getting account info for ShapeShift brokers...")
        for broker in self.shapeshift_brokers:
            print(f"   Checking broker: {broker[:20]}...")
            account_info = self.make_rpc_call("cf_account_info", [broker])
            if account_info:
                print(f"   ✅ Got account info for {broker[:20]}")
                record = self.search_for_brokers_in_data(account_info, f"account_info_{broker[:8]}")
                if record:
                    debug_records.append(record)
                    self.save_debug_record(record)
            else:
                print(f"   ❌ No account info for {broker[:20]}")
        
        # Method 6: Get asset balances for ShapeShift brokers
        print("\n🔍 Method 6: Getting asset balances for ShapeShift brokers...")
        for broker in self.shapeshift_brokers:
            print(f"   Checking balances for: {broker[:20]}...")
            balances = self.make_rpc_call("cf_asset_balances", [broker])
            if balances:
                print(f"   ✅ Got balances for {broker[:20]}")
                record = self.search_for_brokers_in_data(balances, f"asset_balances_{broker[:8]}")
                if record:
                    debug_records.append(record)
                    self.save_debug_record(record)
            else:
                print(f"   ❌ No balances for {broker[:20]}")
        
        # Method 7: Get recent blocks and search for broker activity
        print("\n🔍 Method 7: Examining recent blocks for broker activity...")
        try:
            current_block = self.make_rpc_call("chain_getBlock")
            if current_block:
                block_number = int(current_block['block']['header']['number'], 16)
                print(f"   Current block: {block_number}")
                
                # Check a few recent blocks
                for i in range(5):
                    check_block = block_number - i
                    block_hash = self.make_rpc_call("chain_getBlockHash", [check_block])
                    if block_hash:
                        block = self.make_rpc_call("chain_getBlock", [block_hash])
                        if block:
                            record = self.search_for_brokers_in_data(block, f"block_{check_block}")
                            if record:
                                debug_records.append(record)
                                self.save_debug_record(record)
                                break  # Found broker activity, no need to check more blocks
        except Exception as e:
            print(f"   ❌ Error checking blocks: {e}")
        
        # Summary
        print(f"\n🎯 DEBUG scan completed!")
        print(f"   Total broker matches found: {len(debug_records)}")
        print(f"   CSV file: {self.csv_file}")
        
        if debug_records:
            print(f"\n💡 Found ShapeShift broker activity in:")
            for record in debug_records:
                print(f"   - {record['data_type']}: {record['broker_address']}")
        else:
            print(f"\n⚠️  No ShapeShift broker activity found")
            print(f"   This suggests brokers might not be actively processing transactions")
            print(f"   or using different addresses than expected")
        
        return len(debug_records)

def main():
    """Main function"""
    try:
        listener = ChainflipDebugListener()
        total_matches = listener.run_debug_scan()
        
        print(f"\n📊 DEBUG Scan Results:")
        print(f"   Broker matches found: {total_matches}")
        
        if total_matches > 0:
            print(f"\n💡 To view the debug data:")
            print(f"   cat {listener.csv_file}")
        
    except Exception as e:
        print(f"❌ Error running debug listener: {e}")

if __name__ == "__main__":
    main()
