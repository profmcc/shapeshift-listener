#!/usr/bin/env python3
"""
Chainflip Transaction Discovery - Find any transactions and search for ShapeShift patterns
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

def search_for_shapeshift_patterns(data, data_type, index=None):
    """Search for any patterns that might indicate ShapeShift activity"""
    matches = []
    
    try:
        data_str = json.dumps(data).lower()
        
        # Search for various ShapeShift indicators
        search_terms = [
            'shapeshift', 'shape shift', 'ss:', 'ss:', 'broker', 'affiliate',
            'treasury', 'dao', 'protocol', 'fee', 'commission', 'swap'
        ]
        
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
        
        # Search for any addresses that might be ShapeShift related
        # Look for patterns like "0x..." addresses that might be treasury addresses
        import re
        eth_addresses = re.findall(r'0x[a-fA-F0-9]{40}', json.dumps(data))
        if eth_addresses:
            # Check if any of these might be known ShapeShift addresses
            known_shapeshift_addresses = [
                '0x90A48D5CF7343B08dA12E067680B4C6dbfE551Be',  # ShapeShift DAO Treasury
                '0x9Bf4001d307dFd62B26A2F1307ee0C0307632d59',  # Another known address
            ]
            
            for addr in eth_addresses:
                if addr in known_shapeshift_addresses:
                    matches.append(f"Found known ShapeShift address {addr} in {data_type}")
        
        return matches
    except Exception as e:
        return [f"Error searching {data_type}: {e}"]

def main():
    """Main function"""
    print("🔍 Chainflip Transaction Discovery - Finding Any Transactions with ShapeShift Patterns")
    print("=" * 85)
    
    all_transactions = []
    
    # Method 1: Get LP order fills and examine them
    print(f"\n🔍 Method 1: LP Order Fills (Detailed Examination)")
    print("-" * 50)
    
    fills = make_rpc_call("cf_lp_get_order_fills", [])
    if fills:
        print(f"   ✅ Found {len(fills)} LP order fills")
        
        for i, fill in enumerate(fills):
            if isinstance(fill, dict):
                print(f"      📋 Fill {i}: {list(fill.keys()) if isinstance(fill, dict) else 'Not a dict'}")
                
                # Search for ShapeShift patterns
                matches = search_for_shapeshift_patterns(fill, "lp_order_fills", i)
                if matches:
                    print(f"         🎯 Found patterns: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_lp_get_order_fills',
                        'data_type': 'lp_order_fills',
                        'index': i,
                        'keys': list(fill.keys()) if isinstance(fill, dict) else [],
                        'matches': matches,
                        'raw_data': json.dumps(fill)[:500],
                        'detection_method': 'lp_order_fills_detailed'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No LP fills found")
    
    # Method 2: Get transaction screening events and examine them
    print(f"\n🔍 Method 2: Transaction Screening Events (Detailed Examination)")
    print("-" * 60)
    
    events = make_rpc_call("cf_get_transaction_screening_events", [])
    if events:
        print(f"   ✅ Found {len(events)} screening events")
        
        for i, event in enumerate(events):
            if isinstance(event, dict):
                print(f"      📋 Event {i}: {list(event.keys()) if isinstance(event, dict) else 'Not a dict'}")
                
                # Search for ShapeShift patterns
                matches = search_for_shapeshift_patterns(event, "screening_events", i)
                if matches:
                    print(f"         🎯 Found patterns: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_get_transaction_screening_events',
                        'data_type': 'screening_events',
                        'index': i,
                        'keys': list(event.keys()) if isinstance(event, dict) else [],
                        'matches': matches,
                        'raw_data': json.dumps(event)[:500],
                        'detection_method': 'screening_events_detailed'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No screening events found")
    
    # Method 3: Get open deposit channels and examine them
    print(f"\n🔍 Method 3: Open Deposit Channels (Detailed Examination)")
    print("-" * 55)
    
    channels = make_rpc_call("cf_all_open_deposit_channels", [])
    if channels:
        print(f"   ✅ Found {len(channels)} open deposit channels")
        
        # Limit to first 10 to avoid overwhelming output
        for i, channel in enumerate(channels[:10]):
            if isinstance(channel, dict):
                print(f"      📋 Channel {i}: {list(channel.keys()) if isinstance(channel, dict) else 'Not a dict'}")
                
                # Search for ShapeShift patterns
                matches = search_for_shapeshift_patterns(channel, "deposit_channels", i)
                if matches:
                    print(f"         🎯 Found patterns: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_all_open_deposit_channels',
                        'data_type': 'deposit_channels',
                        'index': i,
                        'keys': list(channel.keys()) if isinstance(channel, dict) else [],
                        'matches': matches,
                        'raw_data': json.dumps(channel)[:500],
                        'detection_method': 'deposit_channels_detailed'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No open deposit channels found")
    
    # Method 4: Get pending broadcasts and examine them
    print(f"\n🔍 Method 4: Pending Broadcasts (Detailed Examination)")
    print("-" * 50)
    
    broadcasts = make_rpc_call("cf_monitoring_pending_broadcasts", [])
    if broadcasts:
        print(f"   ✅ Found {len(broadcasts)} pending broadcasts")
        
        for i, broadcast in enumerate(broadcasts):
            if isinstance(broadcast, dict):
                print(f"      📋 Broadcast {i}: {list(broadcast.keys()) if isinstance(broadcast, dict) else 'Not a dict'}")
                
                # Search for ShapeShift patterns
                matches = search_for_shapeshift_patterns(broadcast, "pending_broadcasts", i)
                if matches:
                    print(f"         🎯 Found patterns: {matches}")
                    
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'method': 'cf_monitoring_pending_broadcasts',
                        'data_type': 'pending_broadcasts',
                        'index': i,
                        'keys': list(broadcast.keys()) if isinstance(broadcast, dict) else [],
                        'matches': matches,
                        'raw_data': json.dumps(broadcast)[:500],
                        'detection_method': 'pending_broadcasts_detailed'
                    }
                    all_transactions.append(transaction)
    else:
        print(f"   ❌ No pending broadcasts found")
    
    # Method 5: Try to get recent blocks and examine them
    print(f"\n🔍 Method 5: Recent Block Analysis (Detailed)")
    print("-" * 45)
    
    try:
        current_block = make_rpc_call("chain_getBlock")
        if current_block:
            block_number = int(current_block['block']['header']['number'], 16)
            print(f"   Current block: {block_number}")
            
            # Check a few recent blocks
            for check_block in range(block_number - 3, block_number + 1):
                block_hash = make_rpc_call("chain_getBlockHash", [check_block])
                if block_hash:
                    block = make_rpc_call("chain_getBlock", [block_hash])
                    if block:
                        print(f"      📋 Block {check_block}: {list(block.keys()) if isinstance(block, dict) else 'Not a dict'}")
                        
                        # Search for ShapeShift patterns
                        matches = search_for_shapeshift_patterns(block, f"block_{check_block}")
                        if matches:
                            print(f"         🎯 Found patterns: {matches}")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'chain_getBlock',
                                'data_type': f'block_{check_block}',
                                'index': check_block,
                                'keys': list(block.keys()) if isinstance(block, dict) else [],
                                'matches': matches,
                                'raw_data': json.dumps(block)[:500],
                                'detection_method': 'block_analysis'
                            }
                            all_transactions.append(transaction)
        else:
            print(f"   ❌ Could not get current block")
    except Exception as e:
        print(f"   ❌ Error checking blocks: {e}")
    
    # Summary
    print(f"\n🎯 Transaction Discovery Summary")
    print("=" * 55)
    print(f"   Total transactions with patterns found: {len(all_transactions)}")
    
    if all_transactions:
        print(f"\n✅ Found ShapeShift-related patterns in:")
        for tx in all_transactions:
            print(f"   - {tx['method']} ({tx['data_type']}): {tx['matches']}")
        
        # Save to CSV
        csv_file = "chainflip_transaction_discovery.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'timestamp', 'method', 'data_type', 'index', 'keys', 'matches', 
                'raw_data', 'detection_method'
            ])
            writer.writeheader()
            for tx in all_transactions:
                writer.writerow(tx)
        
        print(f"\n💾 Saved transactions to: {csv_file}")
        
    else:
        print(f"\n⚠️  No ShapeShift-related patterns found")
        print(f"   This suggests:")
        print(f"   1. Brokers using completely different addresses")
        print(f"   2. Transactions in completely different format")
        print(f"   3. Need to check Chainflip explorer for actual format")
        print(f"   4. Brokers might be inactive right now")
        print(f"   5. Different detection method needed")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Check Chainflip explorer for actual transaction format")
    print(f"   2. Look for different broker addresses")
    print(f"   3. Check if brokers use different naming conventions")
    print(f"   4. Try different RPC methods not yet tested")
    print(f"   5. Check if transactions are in a different data structure")

if __name__ == "__main__":
    main()
