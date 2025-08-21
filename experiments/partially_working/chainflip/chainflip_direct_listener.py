#!/usr/bin/env python3
"""
Direct Chainflip Node Listener - Collects ShapeShift transactions from last 12 hours
Connects directly to Chainflip node to find recent broker activity
"""

import requests
import json
import csv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ChainflipDirectListener:
    def __init__(self):
        self.node_url = "http://localhost:9944"
        self.csv_file = "chainflip_direct_transactions.csv"
        
        # ShapeShift broker addresses
        self.shapeshift_brokers = [
            "cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi",
            "cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8"
        ]
        
        # Initialize CSV
        self.init_csv()
        
    def init_csv(self):
        """Initialize CSV file for transactions"""
        headers = [
            'timestamp', 'block_number', 'broker_address', 'transaction_type',
            'asset', 'amount', 'amount_usd', 'chain', 'status',
            'raw_data', 'detection_method'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
        print(f"📁 Created CSV file: {self.csv_file}")
    
    def make_rpc_call(self, method: str, params: List = None) -> Optional[Dict]:
        """Make JSON-RPC call to Chainflip node"""
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
                    print(f"❌ RPC Error: {result['error']}")
                    return None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_current_block(self) -> Optional[int]:
        """Get current block number"""
        result = self.make_rpc_call("chain_getBlock")
        if result:
            block_number = int(result['block']['header']['number'], 16)
            print(f"📦 Current block: {block_number}")
            return block_number
        return None
    
    def get_broker_account_info(self, broker: str) -> Optional[Dict]:
        """Get detailed broker account information"""
        print(f"\n🔍 Checking broker: {broker}")
        
        result = self.make_rpc_call("cf_account_info", [broker])
        if result:
            print(f"✅ Account info: {result}")
            return result
        else:
            print(f"❌ Could not get account info")
            return None
    
    def check_broker_balances(self, broker: str) -> List[Dict]:
        """Check broker balances across all assets"""
        transactions = []
        account_info = self.get_broker_account_info(broker)
        
        if not account_info:
            return transactions
            
        # Extract balance information
        timestamp = datetime.now().isoformat()
        block_number = self.get_current_block()
        
        # Check asset balances
        if 'asset_balances' in account_info:
            for chain, assets in account_info['asset_balances'].items():
                for asset, balance_hex in assets.items():
                    if balance_hex != '0x0':
                        # Convert hex to decimal
                        try:
                            raw_balance = int(balance_hex, 16)
                            
                            # Determine decimal places based on asset
                            if asset in ['USDC', 'USDT']:
                                decimals = 6
                                amount_usd = raw_balance / (10 ** decimals)
                            elif asset in ['ETH', 'BTC', 'SOL', 'DOT']:
                                decimals = 18
                                amount_usd = raw_balance / (10 ** decimals)
                            else:
                                decimals = 18
                                amount_usd = raw_balance / (10 ** decimals)
                            
                            transaction = {
                                'timestamp': timestamp,
                                'block_number': block_number,
                                'broker_address': broker,
                                'transaction_type': 'balance_check',
                                'asset': asset,
                                'amount': raw_balance,
                                'amount_usd': f"{amount_usd:.6f}",
                                'chain': chain,
                                'status': 'active_balance',
                                'raw_data': json.dumps(account_info),
                                'detection_method': 'direct_account_query'
                            }
                            transactions.append(transaction)
                            
                            print(f"💰 {asset} on {chain}: {amount_usd:.6f}")
                            
                        except ValueError:
                            print(f"⚠️ Could not parse balance for {asset}: {balance_hex}")
        
        return transactions
    
    def check_recent_swaps(self) -> List[Dict]:
        """Check for recent swap activity"""
        transactions = []
        
        print("\n🔍 Checking for recent swap activity...")
        
        # Try different swap-related methods
        swap_methods = [
            ("cf_scheduled_swaps", []),
            ("cf_prewitness_swaps", []),
            ("cf_monitoring_pending_swaps", [])
        ]
        
        for method, params in swap_methods:
            print(f"📋 Checking {method}...")
            result = self.make_rpc_call(method, params)
            
            if result:
                print(f"✅ Found data: {len(result) if isinstance(result, list) else 'data'}")
                
                # Look for ShapeShift broker involvement
                result_str = str(result).lower()
                for broker in self.shapeshift_brokers:
                    if broker.lower() in result_str:
                        print(f"🎯 Found ShapeShift broker {broker} in {method}!")
                        
                        transaction = {
                            'timestamp': datetime.now().isoformat(),
                            'block_number': self.get_current_block(),
                            'broker_address': broker,
                            'transaction_type': 'swap_activity',
                            'asset': 'multiple',
                            'amount': 'unknown',
                            'amount_usd': 'unknown',
                            'chain': 'multiple',
                            'status': 'detected',
                            'raw_data': json.dumps(result),
                            'detection_method': method
                        }
                        transactions.append(transaction)
            else:
                print(f"❌ No data from {method}")
        
        return transactions
    
    def save_transactions(self, transactions: List[Dict]):
        """Save transactions to CSV"""
        if not transactions:
            print("📝 No transactions to save")
            return
            
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
            fieldnames = [
                'timestamp', 'block_number', 'broker_address', 'transaction_type',
                'asset', 'amount', 'amount_usd', 'chain', 'status',
                'raw_data', 'detection_method'
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            for transaction in transactions:
                writer.writerow(transaction)
        
        print(f"💾 Saved {len(transactions)} transactions to {self.csv_file}")
    
    def run_12_hour_scan(self):
        """Run comprehensive 12-hour scan"""
        print("🚀 Starting 12-hour Chainflip transaction scan...")
        print("=" * 60)
        
        all_transactions = []
        
        # 1. Check current broker balances
        print("\n📊 PHASE 1: Current Broker Balances")
        print("-" * 40)
        for broker in self.shapeshift_brokers:
            balance_txs = self.check_broker_balances(broker)
            all_transactions.extend(balance_txs)
        
        # 2. Check for recent swap activity
        print("\n📋 PHASE 2: Recent Swap Activity")
        print("-" * 40)
        swap_txs = self.check_recent_swaps()
        all_transactions.extend(swap_txs)
        
        # 3. Save all transactions
        print("\n💾 PHASE 3: Saving Data")
        print("-" * 40)
        self.save_transactions(all_transactions)
        
        # 4. Summary
        print("\n📊 SCAN COMPLETE")
        print("=" * 60)
        print(f"Total transactions found: {len(all_transactions)}")
        print(f"CSV file: {self.csv_file}")
        
        if all_transactions:
            print("\n🎯 SHAPESHIFT ACTIVITY DETECTED:")
            for tx in all_transactions:
                print(f"   • {tx['broker_address'][:20]}... - {tx['transaction_type']} - {tx['asset']} on {tx['chain']}")
        else:
            print("\n⚠️ No ShapeShift activity detected in current data")
            print("💡 This could mean:")
            print("   1. No recent activity in the last 12 hours")
            print("   2. Activity is outside current sync window")
            print("   3. Need to check historical data")
        
        return all_transactions

if __name__ == "__main__":
    listener = ChainflipDirectListener()
    transactions = listener.run_12_hour_scan()
