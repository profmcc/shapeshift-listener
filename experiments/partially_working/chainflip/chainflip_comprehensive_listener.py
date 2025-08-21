#!/usr/bin/env python3
"""
Chainflip Comprehensive Listener - Find ShapeShift transactions using all available methods
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

def search_for_shapeshift_in_data(data, data_type, index=None):
    """Search for ShapeShift activity in data"""
    matches = []
    
    try:
        data_str = json.dumps(data).lower()
        
        # Search for various ShapeShift indicators
        search_terms = ['shapeshift', 'shape shift', 'ss:', 'ss:', 'broker', 'affiliate']
        for term in search_terms:
            if term in data_str:
                matches.append(f"Found '{term}' in {data_type}")
        
        # Search for broker addresses
        brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
        ]
        
        for broker in brokers:
            if broker in json.dumps(data):
                matches.append(f"Found broker {broker[:20]}... in {data_type}")
        
        return matches
    except Exception as e:
        return [f"Error searching {data_type}: {e}"]

def main():
    """Main function"""
    print("🔍 Chainflip Comprehensive Listener - Finding ShapeShift Transactions")
    print("=" * 75)
    
    all_transactions = []
    
    # Method 1: Get scheduled swaps with NO parameters (based on error message)
    print(f"\n🔍 Method 1: Scheduled Swaps (No Parameters)")
    print("-" * 40)
    
    swaps = make_rpc_call("cf_scheduled_swaps")  # No parameters
    if swaps:
        print(f"   ✅ Found {len(swaps)} scheduled swaps")
        
        for i, swap in enumerate(swaps):
            if isinstance(swap, dict):
                matches = search_for_shapeshift_in_data(swap, "scheduled_swaps", i)
                if matches:
                    print(f"      🎯 Swap {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_scheduled_swaps',
                        'data_type': 'scheduled_swaps',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(swap)[:500],
                        'detection_method': 'scheduled_swaps_no_params'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No scheduled swaps found")
    
    # Method 2: Get prewitness swaps with NO parameters
    print(f"\n🔍 Method 2: Prewitness Swaps (No Parameters)")
    print("-" * 40)
    
    swaps = make_rpc_call("cf_prewitness_swaps")  # No parameters
    if swaps:
        print(f"   ✅ Found {len(swaps)} prewitness swaps")
        
        for i, swap in enumerate(swaps):
            if isinstance(swap, dict):
                matches = search_for_shapeshift_in_data(swap, "prewitness_swaps", i)
                if matches:
                    print(f"      🎯 Swap {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_prewitness_swaps',
                        'data_type': 'prewitness_swaps',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(swap)[:500],
                        'detection_method': 'prewitness_swaps_no_params'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No prewitness swaps found")
    
    # Method 3: Get pool orders with NO parameters
    print(f"\n🔍 Method 3: Pool Orders (No Parameters)")
    print("-" * 35)
    
    orders = make_rpc_call("cf_pool_orders")  # No parameters
    if orders:
        print(f"   ✅ Found {len(orders)} pool orders")
        
        for i, order in enumerate(orders):
            if isinstance(order, dict):
                matches = search_for_shapeshift_in_data(order, "pool_orders", i)
                if matches:
                    print(f"      🎯 Order {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_pool_orders',
                        'data_type': 'pool_orders',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(order)[:500],
                        'detection_method': 'pool_orders_no_params'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No pool orders found")
    
    # Method 4: Get LP order fills
    print(f"\n🔍 Method 4: LP Order Fills")
    print("-" * 25)
    
    fills = make_rpc_call("cf_lp_get_order_fills", [])
    if fills:
        print(f"   ✅ Found {len(fills)} LP order fills")
        
        for i, fill in enumerate(fills):
            if isinstance(fill, dict):
                matches = search_for_shapeshift_in_data(fill, "lp_order_fills", i)
                if matches:
                    print(f"      🎯 Fill {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_lp_get_order_fills',
                        'data_type': 'lp_order_fills',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(fill)[:500],
                        'detection_method': 'lp_order_fills'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No LP fills found")
    
    # Method 5: Get transaction screening events
    print(f"\n🔍 Method 5: Transaction Screening Events")
    print("-" * 40)
    
    events = make_rpc_call("cf_get_transaction_screening_events", [])
    if events:
        print(f"   ✅ Found {len(events)} screening events")
        
        for i, event in enumerate(events):
            if isinstance(event, dict):
                matches = search_for_shapeshift_in_data(event, "screening_events", i)
                if matches:
                    print(f"      🎯 Event {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_get_transaction_screening_events',
                        'data_type': 'screening_events',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(event)[:500],
                        'detection_method': 'screening_events'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No screening events found")
    
    # Method 6: Try to get all open deposit channels
    print(f"\n�� Method 6: Open Deposit Channels")
    print("-" * 35)
    
    channels = make_rpc_call("cf_all_open_deposit_channels", [])
    if channels:
        print(f"   ✅ Found {len(channels)} open deposit channels")
        
        for i, channel in enumerate(channels):
            if isinstance(channel, dict):
                matches = search_for_shapeshift_in_data(channel, "deposit_channels", i)
                if matches:
                    print(f"      🎯 Channel {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_all_open_deposit_channels',
                        'data_type': 'deposit_channels',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(channel)[:500],
                        'detection_method': 'deposit_channels'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No open deposit channels found")
    
    # Method 7: Try to get pending broadcasts
    print(f"\n🔍 Method 7: Pending Broadcasts")
    print("-" * 30)
    
    broadcasts = make_rpc_call("cf_monitoring_pending_broadcasts", [])
    if broadcasts:
        print(f"   ✅ Found {len(broadcasts)} pending broadcasts")
        
        for i, broadcast in enumerate(broadcasts):
            if isinstance(broadcast, dict):
                matches = search_for_shapeshift_in_data(broadcast, "pending_broadcasts", i)
                if matches:
                    print(f"      🎯 Broadcast {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_monitoring_pending_broadcasts',
                        'data_type': 'pending_broadcasts',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(broadcast)[:500],
                        'detection_method': 'pending_broadcasts'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No pending broadcasts found")
    
    # Method 8: Try to get pending swaps from monitoring
    print(f"\n🔍 Method 8: Pending Swaps (Monitoring)")
    print("-" * 35)
    
    pending_swaps = make_rpc_call("cf_monitoring_pending_swaps", [])
    if pending_swaps:
        print(f"   ✅ Found {len(pending_swaps)} pending swaps")
        
        for i, swap in enumerate(pending_swaps):
            if isinstance(swap, dict):
                matches = search_for_shapeshift_in_data(swap, "pending_swaps", i)
                if matches:
                    print(f"      🎯 Pending Swap {i}: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_monitoring_pending_swaps',
                        'data_type': 'pending_swaps',
                        'index': i,
                        'matches': matches,
                        'raw_data': json.dumps(swap)[:500],
                        'detection_method': 'pending_swaps_monitoring'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No pending swaps found")
    
    # Summary
    print(f"\n🎯 Comprehensive Search Summary")
    print("=" * 55)
    print(f"   Total transactions found: {len(all_transactions)}")
    
    if all_transactions:
        print(f"\n✅ Found ShapeShift activity in:")
        for tx in all_transactions:
            print(f"   - {tx['method']}: {tx['matches']}")
        
        # Save to CSV
        csv_file = "chainflip_comprehensive_transactions.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'timestamp', 'method', 'data_type', 'index', 'matches', 
                'raw_data', 'detection_method'
            ])
            writer.writeheader()
            for tx in all_transactions:
                writer.writerow(tx)
        
        print(f"\n💾 Saved transactions to: {csv_file}")
        
    else:
        print(f"\n⚠️  No ShapeShift transactions found")
        print(f"   This suggests:")
        print(f"   1. Brokers using different addresses than expected")
        print(f"   2. Transactions in different format than expected")
        print(f"   3. Need to check Chainflip explorer for actual format")
        print(f"   4. Brokers might be inactive right now")
        print(f"   5. Different detection method needed")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Check Chainflip explorer for actual transaction format")
    print(f"   2. Look for different broker addresses")
    print(f"   3. Check if brokers use different naming conventions")
    print(f"   4. Try different RPC methods not yet tested")

if __name__ == "__main__":
    main()
