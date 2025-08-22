#!/usr/bin/env python3
"""
Chainflip Explorer Investigation - Find out why we're missing ShapeShift transactions
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

def search_for_shapeshift_patterns(data, search_term):
    """Search for any patterns that might indicate ShapeShift activity"""
    matches = []
    
    try:
        data_str = json.dumps(data).lower()
        search_lower = search_term.lower()
        
        if search_lower in data_str:
            matches.append(f"Found '{search_term}' in data")
        
        # Also search for variations
        variations = ['shapeshift', 'shape shift', 'ss', 'broker', 'affiliate']
        for var in variations:
            if var in data_str:
                matches.append(f"Found '{var}' in data")
        
        return matches
    except Exception as e:
        return [f"Error searching: {e}"]

def main():
    """Main function"""
    print("🔍 Chainflip Explorer Investigation - Finding ShapeShift Transactions")
    print("=" * 70)
    
    # ShapeShift broker addresses
    brokers = [
        "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
        "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
    ]
    
    print(f"\n🎯 Searching for ShapeShift activity in Chainflip data...")
    print(f"   Brokers: {len(brokers)}")
    print(f"   Search patterns: shapeshift, broker, affiliate, ss")
    
    all_matches = []
    
    # Method 1: Get LP order fills and search for patterns
    print(f"\n🔍 Method 1: LP Order Fills")
    print("-" * 30)
    lp_fills = make_rpc_call("cf_lp_get_order_fills", [])
    if lp_fills:
        print(f"   Found {len(lp_fills)} LP order fills")
        
        # Search for ShapeShift patterns
        for i, fill in enumerate(lp_fills):
            if isinstance(fill, dict):
                matches = search_for_shapeshift_patterns(fill, "shapeshift")
                if matches:
                    print(f"   ✅ Fill {i}: {matches}")
                    all_matches.extend(matches)
                    
                    # Show the actual data
                    print(f"   Raw data: {json.dumps(fill, indent=2)[:300]}...")
        
        # Also search for broker addresses
        for i, fill in enumerate(lp_fills):
            if isinstance(fill, dict):
                fill_str = json.dumps(fill)
                for broker in brokers:
                    if broker in fill_str:
                        print(f"   🎯 Fill {i}: Found broker {broker[:20]}...")
                        print(f"   Raw data: {fill_str[:300]}...")
                        all_matches.append(f"Broker found in LP fill {i}")
    else:
        print(f"   ❌ No LP fills found")
    
    # Method 2: Get transaction screening events
    print(f"\n🔍 Method 2: Transaction Screening Events")
    print("-" * 40)
    screening_events = make_rpc_call("cf_get_transaction_screening_events", [])
    if screening_events:
        print(f"   Found {len(screening_events)} screening events")
        
        for i, event in enumerate(screening_events):
            if isinstance(event, dict):
                matches = search_for_shapeshift_patterns(event, "shapeshift")
                if matches:
                    print(f"   ✅ Event {i}: {matches}")
                    all_matches.extend(matches)
                    
                    # Show the actual data
                    print(f"   Raw data: {json.dumps(event, indent=2)[:300]}...")
        
        # Also search for broker addresses
        for i, event in enumerate(screening_events):
            if isinstance(event, dict):
                event_str = json.dumps(event)
                for broker in brokers:
                    if broker in broker:
                        print(f"   🎯 Event {i}: Found broker {broker[:20]}...")
                        print(f"   Raw data: {event_str[:300]}...")
                        all_matches.append(f"Broker found in screening event {i}")
    else:
        print(f"   ❌ No screening events found")
    
    # Method 3: Get pool orders (try different parameters)
    print(f"\n🔍 Method 3: Pool Orders (Testing Parameters)")
    print("-" * 40)
    
    # Try different parameter combinations
    test_params = [
        [],
        [""],
        ["all"],
        ["ETH"],
        ["BTC"],
        ["USDC"]
    ]
    
    for params in test_params:
        try:
            orders = make_rpc_call("cf_pool_orders", params)
            if orders:
                print(f"   ✅ Pool orders with params {params}: {len(orders)} found")
                
                # Search for ShapeShift patterns
                for i, order in enumerate(orders[:5]):  # Limit to first 5
                    if isinstance(order, dict):
                        matches = search_for_shapeshift_patterns(order, "shapeshift")
                        if matches:
                            print(f"      Order {i}: {matches}")
                            all_matches.extend(matches)
                
                # Search for broker addresses
                for i, order in enumerate(orders[:5]):
                    if isinstance(order, dict):
                        order_str = json.dumps(order)
                        for broker in brokers:
                            if broker in order_str:
                                print(f"      🎯 Order {i}: Found broker {broker[:20]}...")
                                all_matches.append(f"Broker found in pool order {i}")
                
                break  # Found working parameters
            else:
                print(f"   ❌ Pool orders with params {params}: No data")
        except Exception as e:
            print(f"   ❌ Pool orders with params {params}: Error - {e}")
    
    # Method 4: Get scheduled swaps (try different parameters)
    print(f"\n🔍 Method 4: Scheduled Swaps (Testing Parameters)")
    print("-" * 40)
    
    test_params = [
        [],
        [""],
        ["all"],
        ["active"],
        ["pending"]
    ]
    
    for params in test_params:
        try:
            swaps = make_rpc_call("cf_scheduled_swaps", params)
            if swaps:
                print(f"   ✅ Scheduled swaps with params {params}: {len(swaps)} found")
                
                # Search for ShapeShift patterns
                for i, swap in enumerate(swaps[:5]):  # Limit to first 5
                    if isinstance(order, dict):
                        matches = search_for_shapeshift_patterns(swap, "shapeshift")
                        if matches:
                            print(f"      Swap {i}: {matches}")
                            all_matches.extend(matches)
                
                # Search for broker addresses
                for i, swap in enumerate(swaps[:5]):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap)
                        for broker in brokers:
                            if broker in swap_str:
                                print(f"      🎯 Swap {i}: Found broker {broker[:20]}...")
                                all_matches.append(f"Broker found in scheduled swap {i}")
                
                break  # Found working parameters
            else:
                print(f"   ❌ Scheduled swaps with params {params}: No data")
        except Exception as e:
            print(f"   ❌ Scheduled swaps with params {params}: Error - {e}")
    
    # Method 5: Get prewitness swaps (try different parameters)
    print(f"\n🔍 Method 5: Prewitness Swaps (Testing Parameters)")
    print("-" * 40)
    
    test_params = [
        [],
        [""],
        ["all"],
        ["active"],
        ["pending"]
    ]
    
    for params in test_params:
        try:
            swaps = make_rpc_call("cf_prewitness_swaps", params)
            if swaps:
                print(f"   ✅ Prewitness swaps with params {params}: {len(swaps)} found")
                
                # Search for ShapeShift patterns
                for i, swap in enumerate(swaps[:5]):  # Limit to first 5
                    if isinstance(swap, dict):
                        matches = search_for_shapeshift_patterns(swap, "shapeshift")
                        if matches:
                            print(f"      Swap {i}: {matches}")
                            all_matches.extend(matches)
                
                # Search for broker addresses
                for i, swap in enumerate(swaps[:5]):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap)
                        for broker in brokers:
                            if broker in swap_str:
                                print(f"      🎯 Swap {i}: Found broker {broker[:20]}...")
                                all_matches.append(f"Broker found in prewitness swap {i}")
                
                break  # Found working parameters
            else:
                print(f"   ❌ Prewitness swaps with params {params}: No data")
        except Exception as e:
            print(f"   ❌ Prewitness swaps with params {params}: Error - {e}")
    
    # Method 6: Check recent blocks for any ShapeShift activity
    print(f"\n🔍 Method 6: Recent Block Analysis")
    print("-" * 30)
    
    try:
        current_block = make_rpc_call("chain_getBlock")
        if current_block:
            block_number = int(current_block['block']['header']['number'], 16)
            print(f"   Current block: {block_number}")
            
            # Check more blocks for activity
            blocks_checked = 0
            for check_block in range(block_number - 50, block_number + 1):  # Check last 50 blocks
                if blocks_checked >= 10:  # Limit to 10 blocks to avoid timeout
                    break
                    
                block_hash = make_rpc_call("chain_getBlockHash", [check_block])
                if block_hash:
                    block = make_rpc_call("chain_getBlock", [block_hash])
                    if block:
                        block_str = json.dumps(block)
                        
                        # Search for ShapeShift patterns
                        matches = search_for_shapeshift_patterns(block, "shapeshift")
                        if matches:
                            print(f"      🎯 Block {check_block}: {matches}")
                            all_matches.extend(matches)
                        
                        # Search for broker addresses
                        for broker in brokers:
                            if broker in block_str:
                                print(f"      🎯 Block {check_block}: Found broker {broker[:20]}...")
                                all_matches.append(f"Broker found in block {check_block}")
                        
                        blocks_checked += 1
        else:
            print(f"   ❌ Could not get current block")
    except Exception as e:
        print(f"   ❌ Error checking blocks: {e}")
    
    # Summary
    print(f"\n🎯 Investigation Summary")
    print("=" * 50)
    print(f"   Total matches found: {len(all_matches)}")
    
    if all_matches:
        print(f"\n✅ Found ShapeShift activity in:")
        for match in all_matches:
            print(f"   - {match}")
    else:
        print(f"\n⚠️  No ShapeShift activity found")
        print(f"   This suggests:")
        print(f"   1. Different detection method needed")
        print(f"   2. Brokers using different addresses")
        print(f"   3. Transactions in different format")
        print(f"   4. Need to query different endpoints")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Check Chainflip explorer for actual transaction format")
    print(f"   2. Look for different broker addresses")
    print(f"   3. Try different RPC methods")
    print(f"   4. Check if transactions use different naming")

if __name__ == "__main__":
    main()
