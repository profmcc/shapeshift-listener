#!/usr/bin/env python3
"""
Direct Broker Query - See exactly what data we get from ShapeShift brokers
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
    print("🔍 Direct ShapeShift Broker Query")
    print("=" * 50)
    
    # ShapeShift broker addresses
    brokers = [
        "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
        "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
    ]
    
    for i, broker in enumerate(brokers, 1):
        print(f"\n🔍 Broker {i}: {broker[:20]}...")
        print("-" * 30)
        
        # Get account info
        print("📋 Account Info:")
        account_info = make_rpc_call("cf_account_info", [broker])
        if account_info:
            print(f"   ✅ Got account info")
            print(f"   Raw data: {json.dumps(account_info, indent=2)[:500]}...")
        else:
            print(f"   ❌ No account info")
        
        # Get asset balances
        print("\n💰 Asset Balances:")
        balances = make_rpc_call("cf_asset_balances", [broker])
        if balances:
            print(f"   ✅ Got balances")
            print(f"   Raw data: {json.dumps(balances, indent=2)[:500]}...")
        else:
            print(f"   ❌ No balances")
        
        # Get free balances
        print("\n💵 Free Balances:")
        free_balances = make_rpc_call("cf_free_balances", [broker])
        if free_balances:
            print(f"   ✅ Got free balances")
            print(f"   Raw data: {json.dumps(free_balances, indent=2)[:500]}...")
        else:
            print(f"   ❌ No free balances")
        
        # Try to get recent activity
        print("\n🔄 Recent Activity Check:")
        try:
            # Get current block
            current_block = make_rpc_call("chain_getBlock")
            if current_block:
                block_number = int(current_block['block']['header']['number'], 16)
                print(f"   Current block: {block_number}")
                
                # Check if broker appears in recent blocks
                found_in_blocks = []
                for check_block in range(block_number - 10, block_number + 1):
                    block_hash = make_rpc_call("chain_getBlockHash", [check_block])
                    if block_hash:
                        block = make_rpc_call("chain_getBlock", [block_hash])
                        if block and broker in json.dumps(block):
                            found_in_blocks.append(check_block)
                
                if found_in_blocks:
                    print(f"   ✅ Broker found in blocks: {found_in_blocks}")
                else:
                    print(f"   ❌ Broker not found in recent 10 blocks")
        except Exception as e:
            print(f"   ❌ Error checking blocks: {e}")

if __name__ == "__main__":
    main()
