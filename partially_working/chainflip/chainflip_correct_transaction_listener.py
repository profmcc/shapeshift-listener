#!/usr/bin/env python3
"""
Chainflip Correct Transaction Listener - Uses proper parameters to find ShapeShift transactions
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

def main():
    """Main function"""
    print("🔍 Chainflip Correct Transaction Listener - Finding ShapeShift Transactions")
    print("=" * 70)
    
    # ShapeShift broker addresses
    brokers = [
        "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
        "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
    ]
    
    print(f"\n🎯 Searching for ShapeShift activity with correct parameters...")
    print(f"   Brokers: {len(brokers)}")
    
    all_transactions = []
    
    # Method 1: Get scheduled swaps with proper asset parameters
    print(f"\n🔍 Method 1: Scheduled Swaps (Proper Asset Parameters)")
    print("-" * 50)
    
    # Try different asset combinations based on the error message
    asset_combinations = [
        ["ETH"],
        ["BTC"], 
        ["USDC"],
        ["USDT"],
        ["FLIP"],
        ["DOT"],
        ["SOL"],
        ["ARB"]
    ]
    
    for assets in asset_combinations:
        try:
            swaps = make_rpc_call("cf_scheduled_swaps", assets)
            if swaps:
                print(f"   ✅ Scheduled swaps for {assets}: {len(swaps)} found")
                
                # Search for broker addresses
                for i, swap in enumerate(swaps):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap)
                        for broker in brokers:
                            if broker in swap_str:
                                print(f"      🎯 Swap {i}: Found broker {broker[:20]}...")
                                print(f"      Raw data: {swap_str[:300]}...")
                                
                                # Create transaction record
                                transaction = {
                                    'timestamp': datetime.now().isoformat(),
                                    'method': 'cf_scheduled_swaps',
                                    'assets': assets,
                                    'broker_address': broker,
                                    'swap_index': i,
                                    'raw_data': swap_str[:500],
                                    'detection_method': 'scheduled_swaps'
                                }
                                all_transactions.append(transaction)
                                break
                
                # Also search for "shapeshift" text
                for i, swap in enumerate(swaps):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap).lower()
                        if 'shapeshift' in swap_str or 'ss' in swap_str:
                            print(f"      🎯 Swap {i}: Found 'shapeshift' text")
                            print(f"      Raw data: {json.dumps(swap, indent=2)[:300]}...")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'cf_scheduled_swaps',
                                'assets': assets,
                                'broker_address': 'shapeshift_text_found',
                                'swap_index': i,
                                'raw_data': json.dumps(swap)[:500],
                                'detection_method': 'shapeshift_text_search'
                            }
                            all_transactions.append(transaction)
                
                break  # Found working parameters
            else:
                print(f"   ❌ Scheduled swaps for {assets}: No data")
        except Exception as e:
            print(f"   ❌ Scheduled swaps for {assets}: Error - {e}")
    
    # Method 2: Get prewitness swaps with proper asset parameters
    print(f"\n🔍 Method 2: Prewitness Swaps (Proper Asset Parameters)")
    print("-" * 50)
    
    for assets in asset_combinations:
        try:
            swaps = make_rpc_call("cf_prewitness_swaps", assets)
            if swaps:
                print(f"   ✅ Prewitness swaps for {assets}: {len(swaps)} found")
                
                # Search for broker addresses
                for i, swap in enumerate(swaps):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap)
                        for broker in brokers:
                            if broker in swap_str:
                                print(f"      🎯 Swap {i}: Found broker {broker[:20]}...")
                                print(f"      Raw data: {swap_str[:300]}...")
                                
                                transaction = {
                                    'timestamp': datetime.now().isoformat(),
                                    'method': 'cf_prewitness_swaps',
                                    'assets': assets,
                                    'broker_address': broker,
                                    'swap_index': i,
                                    'raw_data': swap_str[:500],
                                    'detection_method': 'prewitness_swaps'
                                }
                                all_transactions.append(transaction)
                                break
                
                # Also search for "shapeshift" text
                for i, swap in enumerate(swaps):
                    if isinstance(swap, dict):
                        swap_str = json.dumps(swap).lower()
                        if 'shapeshift' in swap_str or 'ss' in swap_str:
                            print(f"      🎯 Swap {i}: Found 'shapeshift' text")
                            print(f"      Raw data: {json.dumps(swap, indent=2)[:300]}...")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'cf_prewitness_swaps',
                                'assets': assets,
                                'broker_address': 'shapeshift_text_found',
                                'swap_index': i,
                                'raw_data': json.dumps(swap)[:500],
                                'detection_method': 'shapeshift_text_search'
                            }
                            all_transactions.append(transaction)
                
                break  # Found working parameters
            else:
                print(f"   ❌ Prewitness swaps for {assets}: No data")
        except Exception as e:
            print(f"   ❌ Prewitness swaps for {assets}: Error - {e}")
    
    # Method 3: Get pool orders with proper asset parameters
    print(f"\n🔍 Method 3: Pool Orders (Proper Asset Parameters)")
    print("-" * 45)
    
    for assets in asset_combinations:
        try:
            orders = make_rpc_call("cf_pool_orders", assets)
            if orders:
                print(f"   ✅ Pool orders for {assets}: {len(orders)} found")
                
                # Search for broker addresses
                for i, order in enumerate(orders):
                    if isinstance(order, dict):
                        order_str = json.dumps(order)
                        for broker in brokers:
                            if broker in order_str:
                                print(f"      🎯 Order {i}: Found broker {broker[:20]}...")
                                print(f"      Raw data: {order_str[:300]}...")
                                
                                transaction = {
                                    'timestamp': datetime.now().isoformat(),
                                    'method': 'cf_pool_orders',
                                    'assets': assets,
                                    'broker_address': broker,
                                    'order_index': i,
                                    'raw_data': order_str[:500],
                                    'detection_method': 'pool_orders'
                                }
                                all_transactions.append(transaction)
                                break
                
                # Also search for "shapeshift" text
                for i, order in enumerate(orders):
                    if isinstance(order, dict):
                        order_str = json.dumps(order).lower()
                        if 'shapeshift' in order_str or 'ss' in order_str:
                            print(f"      🎯 Order {i}: Found 'shapeshift' text")
                            print(f"      Raw data: {json.dumps(order, indent=2)[:300]}...")
                            
                            transaction = {
                                'timestamp': datetime.now().isoformat(),
                                'method': 'cf_pool_orders',
                                'assets': assets,
                                'broker_address': 'shapeshift_text_found',
                                'order_index': i,
                                'raw_data': json.dumps(order)[:500],
                                'detection_method': 'shapeshift_text_search'
                            }
                            all_transactions.append(transaction)
                
                break  # Found working parameters
            else:
                print(f"   ❌ Pool orders for {assets}: No data")
        except Exception as e:
            print(f"   ❌ Pool orders for {assets}: Error - {e}")
    
    # Method 4: Check LP order fills for broker activity
    print(f"\n🔍 Method 4: LP Order Fills (Broker Search)")
    print("-" * 35)
    
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
                        
                        transaction = {
                            'timestamp': datetime.now().isoformat(),
                            'method': 'cf_lp_get_order_fills',
                            'assets': 'N/A',
                            'broker_address': broker,
                            'fill_index': i,
                            'raw_data': fill_str[:500],
                            'detection_method': 'lp_order_fills'
                        }
                        all_transactions.append(transaction)
                        break
    else:
        print(f"   ❌ No LP fills found")
    
    # Method 5: Check transaction screening events
    print(f"\n🔍 Method 5: Transaction Screening Events (Broker Search)")
    print("-" * 50)
    
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
                        
                        transaction = {
                            'timestamp': datetime.now().isoformat(),
                            'method': 'cf_get_transaction_screening_events',
                            'assets': 'N/A',
                            'broker_address': broker,
                            'event_index': i,
                            'raw_data': event_str[:500],
                            'detection_method': 'screening_events'
                        }
                        all_transactions.append(transaction)
                        break
    else:
        print(f"   ❌ No screening events found")
    
    # Summary
    print(f"\n🎯 Transaction Search Summary")
    print("=" * 50)
    print(f"   Total transactions found: {len(all_transactions)}")
    
    if all_transactions:
        print(f"\n✅ Found ShapeShift activity in:")
        for tx in all_transactions:
            print(f"   - {tx['method']}: {tx['broker_address']}")
        
        # Save to CSV
        csv_file = "chainflip_correct_transactions.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'timestamp', 'method', 'assets', 'broker_address', 'swap_index', 
                'order_index', 'fill_index', 'event_index', 'raw_data', 'detection_method'
            ])
            writer.writeheader()
            for tx in all_transactions:
                writer.writerow(tx)
        
        print(f"\n💾 Saved transactions to: {csv_file}")
        
    else:
        print(f"\n⚠️  No ShapeShift transactions found")
        print(f"   This suggests:")
        print(f"   1. Brokers using different addresses")
        print(f"   2. Transactions in different format")
        print(f"   3. Need to check Chainflip explorer for actual format")
        print(f"   4. Brokers might be inactive right now")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Check Chainflip explorer for actual transaction format")
    print(f"   2. Look for different broker addresses")
    print(f"   3. Check if brokers use different naming conventions")

if __name__ == "__main__":
    main()
