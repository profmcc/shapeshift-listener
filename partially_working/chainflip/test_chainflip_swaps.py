#!/usr/bin/env python3
"""
Test script to check if we can find recent ShapeShift swaps
using Chainflip-specific RPC methods
"""

import requests
import json

# Chainflip node RPC endpoint  
node_url = "http://localhost:9944"

# ShapeShift broker addresses to look for
shapeshift_brokers = [
    "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
    "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
]

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
        response = requests.post(node_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                return result['result']
            elif 'error' in result:
                print(f"RPC Error: {result['error']}")
                return None
        else:
            print(f"HTTP Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def check_scheduled_swaps():
    """Check for scheduled swaps"""
    print("🔍 Checking scheduled swaps...")
    result = make_rpc_call("cf_scheduled_swaps")
    if result:
        print(f"✅ Found {len(result)} scheduled swaps")
        for i, swap in enumerate(result[:5]):  # Show first 5
            print(f"   Swap {i+1}: {swap}")
            
            # Check if any involve ShapeShift brokers
            swap_str = str(swap).lower()
            for broker in shapeshift_brokers:
                if broker.lower() in swap_str:
                    print(f"   🎯 FOUND SHAPESHIFT BROKER: {broker}")
                    return True
    else:
        print("❌ Could not get scheduled swaps")
    return False

def check_prewitness_swaps():
    """Check for prewitness swaps"""
    print("\n🔍 Checking prewitness swaps...")
    result = make_rpc_call("cf_prewitness_swaps")
    if result:
        print(f"✅ Found {len(result)} prewitness swaps")
        for i, swap in enumerate(result[:5]):  # Show first 5
            print(f"   Swap {i+1}: {swap}")
            
            # Check if any involve ShapeShift brokers
            swap_str = str(swap).lower()
            for broker in shapeshift_brokers:
                if broker.lower() in swap_str:
                    print(f"   🎯 FOUND SHAPESHIFT BROKER: {broker}")
                    return True
    else:
        print("❌ Could not get prewitness swaps")
    return False

def check_pending_swaps():
    """Check monitoring pending swaps"""
    print("\n🔍 Checking pending swaps...")
    result = make_rpc_call("cf_monitoring_pending_swaps")
    if result:
        print(f"✅ Found pending swaps data")
        print(f"   Data: {result}")
        
        # Check if any involve ShapeShift brokers
        result_str = str(result).lower()
        for broker in shapeshift_brokers:
            if broker.lower() in result_str:
                print(f"   🎯 FOUND SHAPESHIFT BROKER: {broker}")
                return True
    else:
        print("❌ Could not get pending swaps")
    return False

def check_accounts_info():
    """Check account info for our brokers"""
    print("\n🔍 Checking broker account info...")
    
    for broker in shapeshift_brokers:
        print(f"\n📊 Checking {broker}...")
        result = make_rpc_call("cf_account_info", [broker])
        if result:
            print(f"   ✅ Account info: {result}")
            
            # Check if there's any activity
            if result and (result.get('balance', 0) > 0 or result.get('bond', 0) > 0):
                print(f"   🎯 ACTIVE SHAPESHIFT BROKER FOUND: {broker}")
                return True
        else:
            print(f"   ❌ Could not get account info for {broker}")
    
    return False

def check_asset_balances():
    """Check asset balances"""
    print("\n🔍 Checking asset balances...")
    result = make_rpc_call("cf_asset_balances")
    if result:
        print(f"✅ Asset balances: {result}")
    else:
        print("❌ Could not get asset balances")

if __name__ == "__main__":
    print("🚀 Chainflip Swaps Detection Test")
    print("=" * 60)
    
    found_shapeshift = False
    
    found_shapeshift |= check_scheduled_swaps()
    found_shapeshift |= check_prewitness_swaps() 
    found_shapeshift |= check_pending_swaps()
    found_shapeshift |= check_accounts_info()
    
    check_asset_balances()
    
    print("\n" + "=" * 60)
    if found_shapeshift:
        print("🎉 SUCCESS: Found ShapeShift broker activity!")
    else:
        print("⚠️  No ShapeShift broker activity detected in current data")
        print("💡 This could mean:")
        print("   1. No recent activity (last transaction was more than sync window)")
        print("   2. Brokers are not registered with the accounts we're checking")
        print("   3. Need to check historical data or use different methods")
