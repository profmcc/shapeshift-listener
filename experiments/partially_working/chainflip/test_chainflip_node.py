#!/usr/bin/env python3
"""
Test script to check if we can query the Chainflip node directly
for recent transactions involving ShapeShift brokers
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

def test_connection():
    """Test if we can connect to the node"""
    print("🔗 Testing Chainflip node connection...")
    
    # Get current block
    block = make_rpc_call("chain_getBlock")
    if block:
        print(f"✅ Connected! Current block: {block['block']['header']['number']}")
        return True
    else:
        print("❌ Failed to connect to node")
        return False

def list_available_methods():
    """Try to get list of available RPC methods"""
    print("\n📋 Checking available RPC methods...")
    
    # Try some common methods
    methods_to_try = [
        "rpc_methods",
        "system_name", 
        "system_version",
        "chain_getBlock",
        "chain_getHeader",
        "state_getMetadata",
        "author_pendingExtrinsics"
    ]
    
    for method in methods_to_try:
        result = make_rpc_call(method)
        if result:
            print(f"✅ {method}: Available")
            if method == "rpc_methods":
                print(f"   Available methods: {result}")
        else:
            print(f"❌ {method}: Not available")

def check_recent_blocks():
    """Check recent blocks for any pattern we can identify"""
    print("\n🔍 Checking recent blocks...")
    
    # Get current block
    current_block = make_rpc_call("chain_getBlock")
    if not current_block:
        print("❌ Could not get current block")
        return
    
    current_number = int(current_block['block']['header']['number'], 16)
    print(f"📦 Current block: {current_number}")
    
    # Check last few blocks for extrinsics
    for i in range(5):
        block_number = current_number - i
        print(f"\n📦 Block {block_number}:")
        
        # Try to get block by number (convert to hex)
        block_hex = hex(block_number)
        result = make_rpc_call("chain_getBlock", [block_hex])
        
        if result:
            extrinsics = result['block']['extrinsics']
            print(f"   📝 {len(extrinsics)} extrinsics found")
            
            # Look for any extrinsics that might be swaps
            for j, ext in enumerate(extrinsics[:3]):  # Check first 3
                # Convert hex to see if we can find readable data
                if isinstance(ext, str) and len(ext) > 100:
                    # Look for broker addresses in the hex data
                    for broker in shapeshift_brokers:
                        if broker.encode().hex() in ext.lower():
                            print(f"   🎯 Found broker {broker} in extrinsic {j}!")
                            return True
        else:
            print(f"   ❌ Could not fetch block {block_number}")
    
    print("❌ No ShapeShift broker activity found in recent blocks")
    return False

if __name__ == "__main__":
    print("🚀 Chainflip Node Test")
    print("=" * 50)
    
    if test_connection():
        list_available_methods()
        check_recent_blocks()
    else:
        print("💡 Make sure the Chainflip node is running on http://localhost:9944")
