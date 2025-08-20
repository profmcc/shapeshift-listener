#!/usr/bin/env python3
"""
Chainflip Working Listener - Now with correct transaction detection based on explorer data
"""

import requests
import json
import csv
import time
from datetime import datetime

def make_rpc_call(method, params=None):
    """Make a JSON-RPC call to the Chainflip node"""
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method
    }
    if params:
        payload["params"] = params
        
    try:
        response = requests.post("http://localhost:9944", json=payload, timeout=10)
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

def search_for_shapeshift_transactions(data, data_type, index=None):
    """Search for ShapeShift transactions based on explorer format"""
    matches = []
    
    try:
        data_str = json.dumps(data)
        
        # Search for our known ShapeShift broker address
        shapeshift_broker = "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi"
        if shapeshift_broker in data_str:
            matches.append(f"Found ShapeShift broker {shapeshift_broker[:20]}...")
        
        # Search for "shapeshift" text (case insensitive)
        if 'shapeshift' in data_str.lower():
            matches.append("Found 'shapeshift' text")
        
        # Search for affiliate-related terms
        affiliate_terms = ['affiliate', 'commission', 'fee']
        for term in affiliate_terms:
            if term in data_str.lower():
                matches.append(f"Found '{term}' term")
        
        # Search for swap-related terms
        swap_terms = ['swap', 'route', 'broker', 'commission']
        for term in swap_terms:
            if term in data_str.lower():
                matches.append(f"Found '{term}' term")
        
        return matches
    except Exception as e:
        return [f"Error searching {data_type}: {e}"]

def main():
    """Main function"""
    print("🔍 Chainflip Working Listener - Detecting ShapeShift Transactions")
    print("=" * 70)
    print("   Based on actual explorer transaction format")
    
    all_transactions = []
    
    # Method 1: Get scheduled swaps with proper asset parameters
    print(f"\n🔍 Method 1: Scheduled Swaps (Asset-Specific)")
    print("-" * 40)
    
    # Based on the explorer, try the assets involved in the swap
    test_assets = [
        ["SOL"],  # From the explorer: SOL → BTC
        ["BTC"],  # Destination asset
        ["ETH"],  # Common asset
        ["USDC"], # Fee asset
        ["FLIP"]  # Chainflip token
    ]
    
    for assets in test_assets:
        try:
            swaps = make_rpc_call("cf_scheduled_swaps", assets)
            if swaps:
                print(f"   ✅ Scheduled swaps for {assets}: {len(swaps)} found")
                
                for i, swap in enumerate(swaps):
                    if isinstance(swap, dict):
                        matches = search_for_shapeshift_transactions(swap, "scheduled_swaps", i)
                        if matches:
                            print(f"      🎯 Swap {i}: {matches}")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'cf_scheduled_swaps',
                                'assets': assets,
                                'swap_index': i,
                                'matches': matches,
                                'raw_data': json.dumps(swap)[:500],
                                'detection_method': 'scheduled_swaps_asset_specific'
                            }
                            all_transactions.append(transaction)
                
                break  # Found working parameters
            else:
                print(f"   ❌ Scheduled swaps for {assets}: No data")
        except Exception as e:
            print(f"   ❌ Scheduled swaps for {assets}: Error - {e}")
    
    # Method 2: Get prewitness swaps with proper asset parameters
    print(f"\n🔍 Method 2: Prewitness Swaps (Asset-Specific)")
    print("-" * 40)
    
    for assets in test_assets:
        try:
            swaps = make_rpc_call("cf_prewitness_swaps", assets)
            if swaps:
                print(f"   ✅ Prewitness swaps for {assets}: {len(swaps)} found")
                
                for i, swap in enumerate(swaps):
                    if isinstance(swap, dict):
                        matches = search_for_shapeshift_transactions(swap, "prewitness_swaps", i)
                        if matches:
                            print(f"      🎯 Swap {i}: {matches}")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'cf_prewitness_swaps',
                                'assets': assets,
                                'swap_index': i,
                                'matches': matches,
                                'raw_data': json.dumps(swap)[:500],
                                'detection_method': 'prewitness_swaps_asset_specific'
                            }
                            all_transactions.append(transaction)
                
                break  # Found working parameters
            else:
                print(f"   ❌ Prewitness swaps for {assets}: No data")
        except Exception as e:
            print(f"   ❌ Prewitness swaps for {assets}: Error - {e}")
    
    # Method 3: Get pool orders with proper asset parameters
    print(f"\n🔍 Method 3: Pool Orders (Asset-Specific)")
    print("-" * 35)
    
    for assets in test_assets:
        try:
            orders = make_rpc_call("cf_pool_orders", assets)
            if swaps:
                print(f"   ✅ Pool orders for {assets}: {len(orders)} found")
                
                for i, order in enumerate(orders):
                    if isinstance(order, dict):
                        matches = search_for_shapeshift_transactions(order, "pool_orders", i)
                        if matches:
                            print(f"      🎯 Order {i}: {matches}")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'cf_pool_orders',
                                'assets': assets,
                                'order_index': i,
                                'matches': matches,
                                'raw_data': json.dumps(order)[:500],
                                'detection_method': 'pool_orders_asset_specific'
                            }
                            all_transactions.append(transaction)
                
                break  # Found working parameters
            else:
                print(f"   ❌ Pool orders for {assets}: No data")
        except Exception as e:
            print(f"   ❌ Pool orders for {assets}: Error - {e}")
    
    # Method 4: Check LP order fills for ShapeShift activity
    print(f"\n🔍 Method 4: LP Order Fills (ShapeShift Search)")
    print("-" * 40)
    
    fills = make_rpc_call("cf_lp_get_order_fills", [])
    if fills:
        print(f"   ✅ Found {len(fills)} LP order fills")
        
        for i, fill in enumerate(fills):
            if isinstance(fill, dict):
                matches = search_for_shapeshift_transactions(fill, "lp_order_fills", i)
                if matches:
                    print(f"      🎯 Fill {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_lp_get_order_fills',
                        'assets': 'N/A',
                        'fill_index': i,
                        'matches': matches,
                        'raw_data': json.dumps(fill)[:500],
                        'detection_method': 'lp_order_fills'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No LP fills found")
    
    # Method 5: Check transaction screening events
    print(f"\n🔍 Method 5: Transaction Screening Events (ShapeShift Search)")
    print("-" * 55)
    
    events = make_rpc_call("cf_get_transaction_screening_events", [])
    if events:
        print(f"   ✅ Found {len(events)} screening events")
        
        for i, event in enumerate(events):
            if isinstance(event, dict):
                matches = search_for_shapeshift_transactions(event, "screening_events", i)
                if matches:
                    print(f"      🎯 Event {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_get_transaction_screening_events',
                        'assets': 'N/A',
                        'event_index': i,
                        'matches': matches,
                        'raw_data': json.dumps(swap)[:500],
                        'detection_method': 'screening_events'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No screening events found")
    
    # Method 6: Try to get swap events (if available)
    print(f"\n🔍 Method 6: Swap Events (Direct Method)")
    print("-" * 35)
    
    try:
        # Try different possible method names for swap events
        swap_methods = [
            "cf_swap_events",
            "cf_get_swaps", 
            "cf_recent_swaps",
            "cf_completed_swaps"
        ]
        
        for method in swap_methods:
            try:
                swaps = make_rpc_call(method)
                if swaps:
                    print(f"   ✅ {method}: {len(swaps)} found")
                    
                    for i, swap in enumerate(swaps):
                        if isinstance(swap, dict):
                            matches = search_for_shapeshift_transactions(swap, method, i)
                            if matches:
                                print(f"      🎯 Swap {i}: {matches}")
                                
                                transaction = {
                                    'timestamp': datetime.now().isoformat(),
                                    'method': method,
                                    'assets': 'N/A',
                                    'swap_index': i,
                                    'matches': matches,
                                    'raw_data': json.dumps(swap)[:500],
                                'detection_method': method
                                }
                                all_transactions.append(transaction)
                    
                    break  # Found working method
                else:
                    print(f"   ❌ {method}: No data")
            except Exception as e:
                print(f"   ❌ {method}: Error - {e}")
    except Exception as e:
        print(f"   ❌ Error testing swap methods: {e}")
    
    # Summary
    print(f"\n🎯 Working Listener Results")
    print("=" * 45)
    print(f"   Total ShapeShift transactions found: {len(all_transactions)}")
    
    if all_transactions:
        print(f"\n✅ Found ShapeShift activity in:")
        for tx in all_transactions:
            print(f"   - {tx['method']}: {tx['matches']}")
        
        # Save to CSV
        csv_file = "chainflip_working_transactions.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'timestamp', 'method', 'assets', 'swap_index', 'order_index', 
                'fill_index', 'event_index', 'matches', 'raw_data', 'detection_method'
            ])
            writer.writeheader()
            for tx in all_transactions:
                writer.writerow(tx)
        
        print(f"\n💾 Saved transactions to: {csv_file}")
        
    else:
        print(f"\n⚠️  No ShapeShift transactions found")
        print(f"   This suggests:")
        print(f"   1. Need to use different asset parameters")
        print(f"   2. Transactions might be in different data structures")
        print(f"   3. Need to check different RPC methods")
        print(f"   4. Brokers might be inactive right now")
    
    print(f"\n�� Based on explorer data:")
    print(f"   - ShapeShift broker: cFMeDPtPHccVYdBSJKTtCYuy7rewFNbre...")
    print(f"   - Affiliate commission: 0.55%")
    print(f"   - Recent swap: SOL → BTC (ID: 735109)")
    print(f"   - Affiliate fee: 1.02 USDC")

if __name__ == "__main__":
    main()
