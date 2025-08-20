#!/usr/bin/env python3
"""
Simple Chainflip Investigation - Find ShapeShift transactions
"""

import requests
import json

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

def main():
    """Main function"""
    print("🔍 Simple Chainflip Investigation - Finding ShapeShift Transactions")
    print("=" * 60)
    
    # ShapeShift broker addresses
    brokers = [
        "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
        "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
    ]
    
    print(f"\n🎯 Searching for ShapeShift activity...")
    print(f"   Brokers: {len(brokers)}")
    
    # Method 1: Get LP order fills
    print(f"\n🔍 Method 1: LP Order Fills")
    print("-" * 30)
    lp_fills = make_rpc_call("cf_lp_get_order_fills", [])
    if lp_fills:
        print(f"   Found {len(lp_fills)} LP order fills")
        
        # Search for broker addresses
        for i, fill in enumerate(lp_fills):
            if isinstance(fill, dict):
                fill_str = json.dumps(fill)
                for broker in brokers:
                    if broker in fill_str:
                        print(f"   🎯 Fill {i}: Found broker {broker[:20]}...")
                        print(f"   Raw data: {fill_str[:300]}...")
                        break
    else:
        print(f"   ❌ No LP fills found")
    
    # Method 2: Get transaction screening events
    print(f"\n🔍 Method 2: Transaction Screening Events")
    print("-" * 40)
    screening_events = make_rpc_call("cf_get_transaction_screening_events", [])
    if screening_events:
        print(f"   Found {len(screening_events)} screening events")
        
        # Search for broker addresses
        for i, event in enumerate(screening_events):
            if isinstance(event, dict):
                event_str = json.dumps(event)
                for broker in brokers:
                    if broker in event_str:
                        print(f"   🎯 Event {i}: Found broker {broker[:20]}...")
                        print(f"   Raw data: {event_str[:300]}...")
                        break
    else:
        print(f"   ❌ No screening events found")
    
    # Method 3: Try to get scheduled swaps with different parameters
    print(f"\n🔍 Method 3: Scheduled Swaps (Testing Parameters)")
    print("-" * 40)
    
    test_params = [[], [""], ["all"], ["active"], ["pending"]]
    
    for params in test_params:
        try:
            swaps = make_rpc_call("cf_scheduled_swaps", params)
            if swaps:
                print(f"   ✅ Scheduled swaps with params {params}: {len(swaps)} found")
                
                # Search for broker addresses
                for i, swap in enumerate(swaps[:5]):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap)
                        for broker in brokers:
                            if broker in swap_str:
                                print(f"      🎯 Swap {i}: Found broker {broker[:20]}...")
                                print(f"      Raw data: {swap_str[:300]}...")
                                break
                
                break  # Found working parameters
            else:
                print(f"   ❌ Scheduled swaps with params {params}: No data")
        except Exception as e:
            print(f"   ❌ Scheduled swaps with params {params}: Error - {e}")
    
    # Method 4: Try to get prewitness swaps with different parameters
    print(f"\n🔍 Method 4: Prewitness Swaps (Testing Parameters)")
    print("-" * 40)
    
    for params in test_params:
        try:
            swaps = make_rpc_call("cf_prewitness_swaps", params)
            if swaps:
                print(f"   ✅ Prewitness swaps with params {params}: {len(swaps)} found")
                
                # Search for broker addresses
                for i, swap in enumerate(swaps[:5]):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap)
                        for broker in brokers:
                            if broker in swap_str:
                                print(f"      🎯 Swap {i}: Found broker {broker[:20]}...")
                                print(f"      Raw data: {swap_str[:300]}...")
                                break
                
                break  # Found working parameters
            else:
                print(f"   ❌ Prewitness swaps with params {params}: No data")
        except Exception as e:
            print(f"   ❌ Prewitness swaps with params {params}: Error - {e}")
    
    # Method 5: Check recent blocks
    print(f"\n🔍 Method 5: Recent Block Analysis")
    print("-" * 30)
    
    try:
        current_block = make_rpc_call("chain_getBlock")
        if current_block:
            block_number = int(current_block['block']['header']['number'], 16)
            print(f"   Current block: {block_number}")
            
            # Check a few recent blocks
            for check_block in range(block_number - 5, block_number + 1):
                block_hash = make_rpc_call("chain_getBlockHash", [check_block])
                if block_hash:
                    block = make_rpc_call("chain_getBlock", [block_hash])
                    if block:
                        block_str = json.dumps(block)
                        
                        # Search for broker addresses
                        for broker in brokers:
                            if broker in block_str:
                                print(f"      🎯 Block {check_block}: Found broker {broker[:20]}...")
                                break
        else:
            print(f"   ❌ Could not get current block")
    except Exception as e:
        print(f"   ❌ Error checking blocks: {e}")
    
    print(f"\n🎯 Investigation completed!")
    print(f"   If no brokers found, they might be:")
    print(f"   1. Using different addresses")
    print(f"   2. In different data structures")
    print(f"   3. Using different naming conventions")

if __name__ == "__main__":
    main()
