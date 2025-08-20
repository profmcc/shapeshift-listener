#!/usr/bin/env python3
"""
Chainflip Transaction Listener - Captures actual swap transactions and affiliate activity
through ShapeShift brokers, not just balance queries
"""

import requests
import json
import csv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ChainflipTransactionListener:
    def __init__(self):
        self.node_url = "http://localhost:9944"
        self.csv_file = "chainflip_actual_transactions.csv"
        
        # ShapeShift broker addresses
        self.shapeshift_brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
        ]
        
        # Initialize CSV
        self.init_csv()
        
    def init_csv(self):
        """Initialize CSV file for actual transactions"""
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
            
        print(f"📁 Created transaction CSV file: {self.csv_file}")
    
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
    
    def get_recent_blocks(self, blocks_back=100):
        """Get recent blocks to scan for transactions"""
        try:
            current_block = self.make_rpc_call("chain_getBlock")
            if current_block:
                block_number = int(current_block['block']['header']['number'], 16)
                return list(range(max(0, block_number - blocks_back), block_number + 1))
            return []
        except Exception as e:
            print(f"❌ Error getting recent blocks: {e}")
            return []
    
    def get_block_transactions(self, block_number):
        """Get all transactions from a specific block"""
        try:
            block_hash = self.make_rpc_call("chain_getBlockHash", [block_number])
            if block_hash:
                block = self.make_rpc_call("chain_getBlock", [block_hash])
                if block and 'block' in block:
                    return block['block']['extrinsics']
            return []
        except Exception as e:
            print(f"❌ Error getting block {block_number}: {e}")
            return []
    
    def get_scheduled_swaps(self):
        """Get scheduled swaps that might involve ShapeShift brokers"""
        try:
            swaps = self.make_rpc_call("cf_scheduled_swaps")
            if swaps:
                return swaps
            return []
        except Exception as e:
            print(f"❌ Error getting scheduled swaps: {e}")
            return []
    
    def get_prewitness_swaps(self):
        """Get prewitness swaps that might involve ShapeShift brokers"""
        try:
            swaps = self.make_rpc_call("cf_prewitness_swaps")
            if swaps:
                return swaps
            return []
        except Exception as e:
            print(f"❌ Error getting prewitness swaps: {e}")
            return []
    
    def get_swap_events(self):
        """Get swap events that might involve ShapeShift brokers"""
        try:
            events = self.make_rpc_call("cf_swap_events")
            if events:
                return events
            return []
        except Exception as e:
            print(f"❌ Error getting swap events: {e}")
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
    
    def run_transaction_scan(self):
        """Run comprehensive transaction scan for ShapeShift broker activity"""
        print("🚀 Starting Chainflip transaction scan for ShapeShift brokers...")
        
        all_transactions = []
        
        # Method 1: Get scheduled swaps
        print("🔍 Scanning scheduled swaps...")
        scheduled_swaps = self.get_scheduled_swaps()
        if scheduled_swaps:
            transactions = self.analyze_swap_data(scheduled_swaps, "scheduled_swaps")
            all_transactions.extend(transactions)
            print(f"✅ Found {len(transactions)} scheduled swap transactions")
        
        # Method 2: Get prewitness swaps
        print("🔍 Scanning prewitness swaps...")
        prewitness_swaps = self.get_prewitness_swaps()
        if prewitness_swaps:
            transactions = self.analyze_swap_data(prewitness_swaps, "prewitness_swaps")
            all_transactions.extend(transactions)
            print(f"✅ Found {len(transactions)} prewitness swap transactions")
        
        # Method 3: Get swap events
        print("🔍 Scanning swap events...")
        swap_events = self.get_swap_events()
        if swap_events:
            transactions = self.analyze_swap_data(swap_events, "swap_events")
            all_transactions.extend(transactions)
            print(f"✅ Found {len(transactions)} swap event transactions")
        
        # Method 4: Scan recent blocks for transactions
        print("🔍 Scanning recent blocks for transactions...")
        recent_blocks = self.get_recent_blocks(50)  # Last 50 blocks
        for block_number in recent_blocks:
            block_txs = self.get_block_transactions(block_number)
            if block_txs:
                # Look for transactions involving ShapeShift brokers
                for tx in block_txs:
                    if any(broker in str(tx) for broker in self.shapeshift_brokers):
                        # This is a simplified approach - would need more sophisticated parsing
                        transaction = {
                            'timestamp': datetime.now().isoformat(),
                            'block_number': block_number,
                            'transaction_hash': f"block_{block_number}_{int(time.time())}",
                            'broker_address': 'Found in block',
                            'transaction_type': 'block_transaction',
                            'source_asset': 'Unknown',
                            'destination_asset': 'Unknown',
                            'amount_in': 'Unknown',
                            'amount_out': 'Unknown',
                            'affiliate_fee': 'Unknown',
                            'fee_asset': 'Unknown',
                            'source_chain': 'Unknown',
                            'destination_chain': 'Unknown',
                            'swap_id': f"block_{block_number}",
                            'swap_state': 'confirmed',
                            'user_address': 'Unknown',
                            'raw_data': str(tx)[:500],  # Truncate long data
                            'detection_method': 'block_scan'
                        }
                        all_transactions.append(transaction)
        
        # Save all found transactions
        if all_transactions:
            self.save_transactions(all_transactions)
            print(f"\n🎯 Transaction scan completed!")
            print(f"   Total transactions found: {len(all_transactions)}")
            print(f"   CSV file: {self.csv_file}")
        else:
            print("\n⚠️  No transactions found involving ShapeShift brokers")
            print("   This could mean:")
            print("   1. No recent broker activity")
            print("   2. Brokers are not actively processing swaps")
            print("   3. Different detection method needed")
        
        return len(all_transactions)

def main():
    """Main function"""
    try:
        listener = ChainflipTransactionListener()
        total_transactions = listener.run_transaction_scan()
        
        print(f"\n📊 Transaction Scan Results:")
        print(f"   Transactions found: {total_transactions}")
        
        if total_transactions > 0:
            print(f"\n💡 To view the transactions:")
            print(f"   cat {listener.csv_file}")
        
    except Exception as e:
        print(f"❌ Error running transaction listener: {e}")

if __name__ == "__main__":
    main()
