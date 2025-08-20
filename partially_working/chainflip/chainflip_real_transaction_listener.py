#!/usr/bin/env python3
"""
Chainflip Real Transaction Listener - Uses correct RPC methods to capture
actual swap transactions and affiliate activity through ShapeShift brokers
"""

import requests
import json
import csv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ChainflipRealTransactionListener:
    def __init__(self):
        self.node_url = "http://localhost:9944"
        self.csv_file = "chainflip_real_transactions.csv"
        
        # ShapeShift broker addresses
        self.shapeshift_brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
        ]
        
        # Initialize CSV
        self.init_csv()
        
    def init_csv(self):
        """Initialize CSV file for real transactions"""
        headers = [
            'timestamp', 'block_number', 'transaction_hash', 'broker_address',
            'transaction_type', 'source_asset', 'destination_asset', 'amount_in',
            'amount_out', 'affiliate_fee', 'fee_asset', 'source_chain',
            'destination_chain', 'swap_id', 'swap_state', 'user_address',
            'raw_data', 'detection_method'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
        print(f"📁 Created real transaction CSV file: {self.csv_file}")
    
    def make_rpc_call(self, method: str, params=None):
        """Make a JSON-RPC call to the Chainflip node"""
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            payload["params"] = params
            
        try:
            response = requests.post(self.node_url, json=payload, timeout=10)
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
    
    def get_scheduled_swaps(self):
        """Get scheduled swaps using correct method"""
        try:
            swaps = self.make_rpc_call("cf_scheduled_swaps", [])
            if swaps:
                print(f"✅ Found {len(swaps)} scheduled swaps")
                return swaps
            return []
        except Exception as e:
            print(f"❌ Error getting scheduled swaps: {e}")
            return []
    
    def get_prewitness_swaps(self):
        """Get prewitness swaps using correct method"""
        try:
            swaps = self.make_rpc_call("cf_prewitness_swaps", [])
            if swaps:
                print(f"✅ Found {len(swaps)} prewitness swaps")
                return swaps
            return []
        except Exception as e:
            print(f"❌ Error getting prewitness swaps: {e}")
            return []
    
    def get_pending_swaps(self):
        """Get pending swaps from monitoring"""
        try:
            pending = self.make_rpc_call("cf_monitoring_pending_swaps", [])
            if pending:
                print(f"✅ Found {len(pending)} pending swaps")
                return pending
            return []
        except Exception as e:
            print(f"❌ Error getting pending swaps: {e}")
            return []
    
    def get_pool_orders(self):
        """Get pool orders that might involve brokers"""
        try:
            orders = self.make_rpc_call("cf_pool_orders", [])
            if orders:
                print(f"✅ Found {len(orders)} pool orders")
                return orders
            return []
        except Exception as e:
            print(f"❌ Error getting pool orders: {e}")
            return []
    
    def get_lp_order_fills(self):
        """Get LP order fills that might involve brokers"""
        try:
            fills = self.make_rpc_call("cf_lp_get_order_fills", [])
            if fills:
                print(f"✅ Found {len(fills)} LP order fills")
                return fills
            return []
        except Exception as e:
            print(f"❌ Error getting LP order fills: {e}")
            return []
    
    def get_transaction_screening_events(self):
        """Get transaction screening events"""
        try:
            events = self.make_rpc_call("cf_get_transaction_screening_events", [])
            if events:
                print(f"✅ Found {len(events)} screening events")
                return events
            return []
        except Exception as e:
            print(f"❌ Error getting screening events: {e}")
            return []
    
    def analyze_swap_data(self, swap_data, data_type):
        """Analyze swap data to find ShapeShift broker involvement"""
        transactions = []
        
        try:
            if isinstance(swap_data, list):
                for swap in swap_data:
                    if isinstance(swap, list) and len(swap) >= 3:
                        broker_address = swap[0]
                        swap_type = swap[1]
                        swap_details = swap[2]
                        
                        # Check if this involves a ShapeShift broker
                        if broker_address in self.shapeshift_brokers:
                            transaction = self.create_transaction_record(
                                swap_details, broker_address, swap_type, data_type
                            )
                            if transaction:
                                transactions.append(transaction)
                                
        except Exception as e:
            print(f"❌ Error analyzing {data_type}: {e}")
            
        return transactions
    
    def create_transaction_record(self, swap_details, broker_address, swap_type, data_type):
        """Create a transaction record from swap data"""
        try:
            # Extract chain account information
            chain_accounts = swap_details.get('chain_accounts', [])
            
            # Find source and destination assets
            source_asset = "Unknown"
            destination_asset = "Unknown"
            source_chain = "Unknown"
            destination_chain = "Unknown"
            
            if len(chain_accounts) >= 2:
                # First chain account is usually source
                first_chain = list(chain_accounts[0].keys())[0] if chain_accounts[0] else "Unknown"
                source_chain = first_chain
                
                # Second chain account is usually destination
                if len(chain_accounts) >= 2:
                    second_chain = list(chain_accounts[1].keys())[0] if chain_accounts[1] else "Unknown"
                    destination_chain = second_chain
                
                # Try to determine assets from chain types
                if first_chain == "Eth":
                    source_asset = "ETH"
                elif first_chain == "Btc":
                    source_asset = "BTC"
                elif first_chain == "Arb":
                    source_asset = "ARB"
                elif first_chain == "Sol":
                    source_asset = "SOL"
                elif first_chain == "Dot":
                    source_asset = "DOT"
                
                if second_chain == "Eth":
                    destination_asset = "ETH"
                elif second_chain == "Btc":
                    destination_asset = "BTC"
                elif second_chain == "Arb":
                    destination_asset = "ARB"
                elif second_chain == "Sol":
                    destination_asset = "SOL"
                elif second_chain == "Dot":
                    destination_asset = "DOT"
            
            transaction = {
                'timestamp': datetime.now().isoformat(),
                'block_number': 'Unknown',  # Will be filled if we can get block info
                'transaction_hash': f"swap_{int(time.time())}_{broker_address[:8]}",
                'broker_address': broker_address,
                'transaction_type': swap_type,
                'source_asset': source_asset,
                'destination_asset': destination_asset,
                'amount_in': 'Unknown',  # Would need more detailed parsing
                'amount_out': 'Unknown',  # Would need more detailed parsing
                'affiliate_fee': 'Unknown',  # Would need fee calculation
                'fee_asset': 'Unknown',
                'source_chain': source_chain,
                'destination_chain': destination_chain,
                'swap_id': f"swap_{int(time.time())}",
                'swap_state': 'active',
                'user_address': 'Unknown',  # Would need user identification
                'raw_data': json.dumps(swap_details),
                'detection_method': data_type
            }
            
            return transaction
            
        except Exception as e:
            print(f"❌ Error creating transaction record: {e}")
            return None
    
    def save_transactions(self, transactions):
        """Save transactions to CSV file"""
        if not transactions:
            return
            
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'timestamp', 'block_number', 'transaction_hash', 'broker_address',
                    'transaction_type', 'source_asset', 'destination_asset', 'amount_in',
                    'amount_out', 'affiliate_fee', 'fee_asset', 'source_chain',
                    'destination_chain', 'swap_id', 'swap_state', 'user_address',
                    'raw_data', 'detection_method'
                ])
                
                for transaction in transactions:
                    writer.writerow(transaction)
                    
            print(f"💾 Saved {len(transactions)} transactions to {self.csv_file}")
            
        except Exception as e:
            print(f"❌ Error saving transactions: {e}")
    
    def run_real_transaction_scan(self):
        """Run comprehensive transaction scan using correct RPC methods"""
        print("🚀 Starting Chainflip REAL transaction scan for ShapeShift brokers...")
        print("   Using correct RPC methods to capture actual swap activity")
        
        all_transactions = []
        
        # Method 1: Get scheduled swaps (correct method)
        print("\n🔍 Method 1: Scanning scheduled swaps...")
        scheduled_swaps = self.get_scheduled_swaps()
        if scheduled_swaps:
            transactions = self.analyze_swap_data(scheduled_swaps, "scheduled_swaps")
            all_transactions.extend(transactions)
            print(f"   Found {len(transactions)} ShapeShift broker transactions")
        
        # Method 2: Get prewitness swaps (correct method)
        print("\n🔍 Method 2: Scanning prewitness swaps...")
        prewitness_swaps = self.get_prewitness_swaps()
        if prewitness_swaps:
            transactions = self.analyze_swap_data(prewitness_swaps, "prewitness_swaps")
            all_transactions.extend(transactions)
            print(f"   Found {len(transactions)} ShapeShift broker transactions")
        
        # Method 3: Get pending swaps from monitoring
        print("\n🔍 Method 3: Scanning pending swaps...")
        pending_swaps = self.get_pending_swaps()
        if pending_swaps:
            transactions = self.analyze_swap_data(pending_swaps, "pending_swaps")
            all_transactions.extend(transactions)
            print(f"   Found {len(transactions)} ShapeShift broker transactions")
        
        # Method 4: Get pool orders
        print("\n🔍 Method 4: Scanning pool orders...")
        pool_orders = self.get_pool_orders()
        if pool_orders:
            # Look for broker involvement in pool orders
            broker_orders = []
            for order in pool_orders:
                if isinstance(order, dict) and any(broker in str(order) for broker in self.shapeshift_brokers):
                    broker_orders.append(order)
            
            if broker_orders:
                print(f"   Found {len(broker_orders)} pool orders involving ShapeShift brokers")
                # Convert to transaction format
                for order in broker_orders:
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'block_number': 'Unknown',
                        'transaction_hash': f"pool_order_{int(time.time())}",
                        'broker_address': 'Found in pool order',
                        'transaction_type': 'pool_order',
                        'source_asset': 'Unknown',
                        'destination_asset': 'Unknown',
                        'amount_in': 'Unknown',
                        'amount_out': 'Unknown',
                        'affiliate_fee': 'Unknown',
                        'fee_asset': 'Unknown',
                        'source_chain': 'Unknown',
                        'destination_chain': 'Unknown',
                        'swap_id': f"pool_{int(time.time())}",
                        'swap_state': 'pending',
                        'user_address': 'Unknown',
                        'raw_data': json.dumps(order),
                        'detection_method': 'pool_orders'
                    }
                    all_transactions.append(transaction)
        
        # Method 5: Get LP order fills
        print("\n🔍 Method 5: Scanning LP order fills...")
        lp_fills = self.get_lp_order_fills()
        if lp_fills:
            # Look for broker involvement in LP fills
            broker_fills = []
            for fill in lp_fills:
                if isinstance(fill, dict) and any(broker in str(fill) for broker in self.shapeshift_brokers):
                    broker_fills.append(fill)
            
            if broker_fills:
                print(f"   Found {len(broker_fills)} LP fills involving ShapeShift brokers")
                # Convert to transaction format
                for fill in broker_fills:
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'block_number': 'Unknown',
                        'transaction_hash': f"lp_fill_{int(time.time())}",
                        'broker_address': 'Found in LP fill',
                        'transaction_type': 'lp_fill',
                        'source_asset': 'Unknown',
                        'destination_asset': 'Unknown',
                        'amount_in': 'Unknown',
                        'amount_out': 'Unknown',
                        'affiliate_fee': 'Unknown',
                        'fee_asset': 'Unknown',
                        'source_chain': 'Unknown',
                        'destination_chain': 'Unknown',
                        'swap_id': f"lp_{int(time.time())}",
                        'swap_state': 'filled',
                        'user_address': 'Unknown',
                        'raw_data': json.dumps(fill),
                        'detection_method': 'lp_fills'
                    }
                    all_transactions.append(transaction)
        
        # Method 6: Get transaction screening events
        print("\n🔍 Method 6: Scanning transaction screening events...")
        screening_events = self.get_transaction_screening_events()
        if screening_events:
            # Look for broker involvement in screening events
            broker_events = []
            for event in screening_events:
                if isinstance(event, dict) and any(broker in str(event) for broker in self.shapeshift_brokers):
                    broker_events.append(event)
            
            if broker_events:
                print(f"   Found {len(broker_events)} screening events involving ShapeShift brokers")
                # Convert to transaction format
                for event in broker_events:
                    transaction = {
                        'timestamp': datetime.now().isoformat(),
                        'block_number': 'Unknown',
                        'transaction_hash': f"screening_{int(time.time())}",
                        'broker_address': 'Found in screening event',
                        'transaction_type': 'screening_event',
                        'source_asset': 'Unknown',
                        'destination_asset': 'Unknown',
                        'amount_in': 'Unknown',
                        'amount_out': 'Unknown',
                        'affiliate_fee': 'Unknown',
                        'fee_asset': 'Unknown',
                        'source_chain': 'Unknown',
                        'destination_chain': 'Unknown',
                        'swap_id': f"screening_{int(time.time())}",
                        'swap_state': 'screened',
                        'user_address': 'Unknown',
                        'raw_data': json.dumps(event),
                        'detection_method': 'screening_events'
                    }
                    all_transactions.append(transaction)
        
        # Save all found transactions
        if all_transactions:
            self.save_transactions(all_transactions)
            print(f"\n🎯 REAL Transaction scan completed!")
            print(f"   Total transactions found: {len(all_transactions)}")
            print(f"   CSV file: {self.csv_file}")
        else:
            print("\n⚠️  No transactions found involving ShapeShift brokers")
            print("   This could mean:")
            print("   1. No recent broker activity")
            print("   2. Brokers are not actively processing swaps")
            print("   3. Different detection method needed")
            print("   4. Brokers might be using different addresses")
        
        return len(all_transactions)

def main():
    """Main function"""
    try:
        listener = ChainflipRealTransactionListener()
        total_transactions = listener.run_real_transaction_scan()
        
        print(f"\n📊 REAL Transaction Scan Results:")
        print(f"   Transactions found: {total_transactions}")
        
        if total_transactions > 0:
            print(f"\n💡 To view the transactions:")
            print(f"   cat {listener.csv_file}")
        
    except Exception as e:
        print(f"❌ Error running real transaction listener: {e}")

if __name__ == "__main__":
    main()
