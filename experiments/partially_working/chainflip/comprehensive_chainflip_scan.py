#!/usr/bin/env python3
"""
Comprehensive Chainflip Scan - Multiple detection methods for ShapeShift activity
"""

import requests
import json
import csv
from datetime import datetime, timedelta

class ComprehensiveChainflipScan:
    def __init__(self):
        self.node_url = "http://localhost:9944"
        self.csv_file = "comprehensive_chainflip_scan.csv"
        
        self.shapeshift_brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi"
        ]
        
        self.init_csv()
    
    def init_csv(self):
        headers = [
            'scan_time', 'method', 'broker', 'data_type', 'raw_data', 'parsed_info'
        ]
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    
    def make_rpc_call(self, method, params=None):
        payload = {"id": 1, "jsonrpc": "2.0", "method": method}
        if params:
            payload["params"] = params
            
        try:
            response = requests.post(self.node_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return result['result']
                elif 'error' in result:
                    return f"ERROR: {result['error']}"
            return None
        except Exception as e:
            return f"EXCEPTION: {e}"
    
    def save_result(self, method, broker, data_type, raw_data, parsed_info):
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().isoformat(),
                method,
                broker,
                data_type,
                json.dumps(raw_data),
                parsed_info
            ])
    
    def scan_all_methods(self):
        print("🚀 Comprehensive Chainflip Scan - All Available Methods")
        print("=" * 70)
        
        # Get current block
        current_block = self.make_rpc_call("chain_getBlock")
        if current_block:
            block_num = int(current_block['block']['header']['number'], 16)
            print(f"📦 Current Block: {block_num}")
        
        # Test all available methods
        methods_to_test = [
            # Account methods
            ("cf_accounts", None, "account_list"),
            ("cf_account_info", ["cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi"], "account_info"),
            ("cf_account_info_v2", ["cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi"], "account_info_v2"),
            
            # Swap methods
            ("cf_scheduled_swaps", None, "scheduled_swaps"),
            ("cf_prewitness_swaps", None, "prewitness_swaps"),
            ("cf_monitoring_pending_swaps", None, "pending_swaps"),
            
            # Pool methods
            ("cf_available_pools", None, "available_pools"),
            ("cf_pool_info", None, "pool_info"),
            ("cf_pool_orders", None, "pool_orders"),
            
            # Asset methods
            ("cf_supported_assets", None, "supported_assets"),
            ("cf_asset_balances", None, "asset_balances"),
            ("cf_free_balances", None, "free_balances"),
            
            # Monitoring methods
            ("cf_monitoring_data", None, "monitoring_data"),
            ("cf_monitoring_epoch_state", None, "epoch_state"),
            ("cf_monitoring_external_chains_block_height", None, "external_heights"),
            
            # Transaction methods
            ("cf_get_transaction_screening_events", None, "screening_events"),
            ("cf_get_open_deposit_channels", None, "deposit_channels"),
            ("cf_all_open_deposit_channels", None, "all_deposit_channels"),
            
            # Affiliate methods
            ("cf_get_affiliates", None, "affiliates"),
            
            # System methods
            ("system_health", None, "system_health"),
            ("system_syncState", None, "sync_state"),
            ("cf_environment", None, "environment"),
            ("cf_current_epoch", None, "current_epoch")
        ]
        
        results = []
        
        for method, params, data_type in methods_to_test:
            print(f"\n🔍 Testing: {method}")
            print("-" * 50)
            
            result = self.make_rpc_call(method, params)
            
            if result and not str(result).startswith("ERROR") and not str(result).startswith("EXCEPTION"):
                print(f"✅ SUCCESS: {data_type}")
                
                # Check for ShapeShift broker involvement
                broker_found = False
                for broker in self.shapeshift_brokers:
                    if broker in str(result):
                        print(f"🎯 SHAPESHIFT BROKER FOUND: {broker}")
                        broker_found = True
                
                # Parse and save result
                parsed_info = self.parse_result(method, result)
                self.save_result(method, "all", data_type, result, parsed_info)
                
                results.append({
                    'method': method,
                    'data_type': data_type,
                    'result': result,
                    'broker_found': broker_found
                })
                
                # Show key data
                if isinstance(result, dict) and len(result) < 1000:
                    print(f"   Data: {result}")
                elif isinstance(result, list) and len(result) < 10:
                    print(f"   Items: {len(result)}")
                    for i, item in enumerate(result[:3]):
                        print(f"     {i+1}: {item}")
                else:
                    print(f"   Data size: {len(str(result))} characters")
                    
            else:
                print(f"❌ FAILED: {result}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SCAN SUMMARY")
        print("=" * 70)
        
        successful_methods = [r for r in results if not str(r['result']).startswith("ERROR")]
        broker_methods = [r for r in results if r['broker_found']]
        
        print(f"✅ Successful methods: {len(successful_methods)}/{len(methods_to_test)}")
        print(f"🎯 Methods with ShapeShift brokers: {len(broker_methods)}")
        print(f"💾 Data saved to: {self.csv_file}")
        
        if broker_methods:
            print(f"\n🎯 SHAPESHIFT ACTIVITY DETECTED IN:")
            for r in broker_methods:
                print(f"   • {r['method']} - {r['data_type']}")
        
        return results
    
    def parse_result(self, method, result):
        """Parse result into human-readable format"""
        try:
            if isinstance(result, dict):
                if 'role' in result:
                    return f"Account role: {result['role']}"
                elif 'asset_balances' in result:
                    return f"Asset balances: {len(result['asset_balances'])} chains"
                elif 'pools' in result:
                    return f"Pools: {len(result['pools'])} available"
                else:
                    return f"Data with {len(result)} keys"
            elif isinstance(result, list):
                return f"List with {len(result)} items"
            else:
                return str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        except:
            return "Could not parse"

if __name__ == "__main__":
    scanner = ComprehensiveChainflipScan()
    results = scanner.scan_all_methods()
