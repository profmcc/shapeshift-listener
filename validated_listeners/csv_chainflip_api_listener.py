#!/usr/bin/env python3
"""
Chainflip API Listener for ShapeShift Affiliate Transactions

Uses the official Chainflip Mainnet APIs to monitor broker transactions
and affiliate fees instead of web scraping.

API Documentation: https://github.com/chainflip-io/chainflip-mainnet-apis
"""

import os
import csv
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CSVChainflipAPIListener:
    def __init__(self, csv_dir: str = "csv_data"):
        self.csv_dir = csv_dir
        self.init_csv_structure()
        
        # Chainflip API endpoints
        self.api_base_url = os.getenv('CHAINFLIP_API_URL', 'http://localhost:10997')
        
        # Known ShapeShift broker addresses
        self.shapeshift_brokers = [
            {
                'address': 'cFMeDPtPHccVYdBSJKTtCYuy7rewFNpro3xZBKaCGbSS2xhRi',
                'name': 'ShapeShift Broker 1'
            },
            {
                'address': 'cFK6mYjpajcwPDZ7JUsac8XUoVSJnhjL43ZMZW7YoN8HE4dD8',
                'name': 'ShapeShift Broker 2'
            }
        ]
        
        # CSV file path
        self.csv_file = os.path.join(csv_dir, 'chainflip_api_transactions.csv')
        
        logger.info(f"🔗 Chainflip API Listener initialized")
        logger.info(f"📡 API Base URL: {self.api_base_url}")
        logger.info(f"📊 Monitoring {len(self.shapeshift_brokers)} ShapeShift brokers")
    
    def init_csv_structure(self):
        """Initialize CSV file structure for Chainflip API data"""
        os.makedirs(self.csv_dir, exist_ok=True)
        
        if not os.path.exists(self.csv_file):
            headers = [
                'transaction_id', 'broker_address', 'broker_name', 'swap_type',
                'source_asset', 'destination_asset', 'swap_amount', 'output_amount',
                'broker_fee_amount', 'broker_fee_asset', 'source_chain', 'destination_chain',
                'transaction_hash', 'block_number', 'swap_state', 'timestamp',
                'scraped_at', 'raw_response'
            ]
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
            
            logger.info(f"📁 Created Chainflip API CSV file: {self.csv_file}")
    
    def make_api_request(self, method: str, params: List = None) -> Optional[Dict]:
        """Make a request to the Chainflip API"""
        try:
            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": method
            }
            
            if params:
                payload["params"] = params
            
            logger.info(f"🔗 API Request: {method} with params: {params}")
            
            response = requests.post(
                self.api_base_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    logger.info(f"✅ API Response: {method} successful")
                    return result['result']
                elif 'error' in result:
                    logger.error(f"❌ API Error: {method} - {result['error']}")
                    return None
                else:
                    logger.warning(f"⚠️ Unexpected API response format: {result}")
                    return None
            else:
                logger.error(f"❌ HTTP Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    def get_broker_info(self, broker_address: str) -> Optional[Dict]:
        """Get broker information from the API"""
        try:
            result = self.make_api_request("broker_getInfo", [broker_address])
            if result:
                logger.info(f"✅ Got broker info for {broker_address}")
                return result
            else:
                logger.warning(f"⚠️ No broker info found for {broker_address}")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting broker info: {e}")
            return None
    
    def get_broker_transactions(self, broker_address: str, limit: int = 100) -> List[Dict]:
        """Get broker transactions from the API"""
        try:
            result = self.make_api_request("broker_getTransactions", [broker_address, limit])
            if result:
                logger.info(f"✅ Got {len(result)} transactions for broker {broker_address}")
                return result
            else:
                logger.warning(f"⚠️ No transactions found for broker {broker_address}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting broker transactions: {e}")
            return []
    
    def get_broker_swaps(self, broker_address: str, limit: int = 100) -> List[Dict]:
        """Get broker swaps from the API"""
        try:
            result = self.make_api_request("broker_getSwaps", [broker_address, limit])
            if result:
                logger.info(f"✅ Got {len(result)} swaps for broker {broker_address}")
                return result
            else:
                logger.warning(f"⚠️ No swaps found for broker {broker_address}")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting broker swaps: {e}")
            return []
    
    def create_transaction_record(self, data: Dict, broker: Dict, data_type: str) -> Optional[Dict]:
        """Create a standardized transaction record"""
        try:
            transaction_id = data.get('id', data.get('hash', f"{broker['address']}_{int(time.time())}"))
            
            transaction = {
                'transaction_id': str(transaction_id),
                'broker_address': broker['address'],
                'broker_name': broker['name'],
                'swap_type': data_type,
                'source_asset': data.get('sourceAsset', data.get('fromAsset', '')),
                'destination_asset': data.get('destinationAsset', data.get('toAsset', '')),
                'swap_amount': str(data.get('amount', data.get('swapAmount', '0')),
                'output_amount': str(data.get('outputAmount', data.get('receivedAmount', '0')),
                'broker_fee_amount': str(data.get('brokerFee', data.get('feeAmount', '0')),
                'broker_fee_asset': data.get('feeAsset', data.get('asset', '')),
                'source_chain': data.get('sourceChain', data.get('fromChain', '')),
                'destination_chain': data.get('destinationChain', data.get('toChain', '')),
                'transaction_hash': data.get('hash', data.get('txHash', '')),
                'block_number': data.get('blockNumber', data.get('block', 0)),
                'swap_state': data.get('state', data.get('status', 'unknown')),
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'scraped_at': datetime.now().isoformat(),
                'raw_response': json.dumps(data)
            }
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error creating transaction record: {e}")
            return None
    
    def process_broker_data(self, broker: Dict[str, str]) -> List[Dict]:
        """Process data for a specific broker"""
        transactions = []
        broker_address = broker['address']
        
        logger.info(f"🔍 Processing broker: {broker['name']} ({broker_address})")
        
        # Get broker information
        broker_info = self.get_broker_info(broker_address)
        
        # Get transactions
        broker_txs = self.get_broker_transactions(broker_address)
        
        # Get swaps
        broker_swaps = self.get_broker_swaps(broker_address)
        
        # Process transactions
        for tx in broker_txs:
            transaction = self.create_transaction_record(tx, broker, 'transaction')
            if transaction:
                transactions.append(transaction)
        
        # Process swaps
        for swap in broker_swaps:
            transaction = self.create_transaction_record(swap, broker, 'swap')
            if transaction:
                transactions.append(transaction)
        
        logger.info(f"✅ Processed {len(transactions)} records for {broker['name']}")
        return transactions
    
    def save_transactions_to_csv(self, transactions: List[Dict]):
        """Save transactions to CSV file"""
        if not transactions:
            logger.info("📝 No transactions to save")
            return
        
        try:
            fieldnames = [
                'transaction_id', 'broker_address', 'broker_name', 'swap_type',
                'source_asset', 'destination_asset', 'swap_amount', 'output_amount',
                'broker_fee_amount', 'broker_fee_asset', 'source_chain', 'destination_chain',
                'transaction_hash', 'block_number', 'swap_state', 'timestamp',
                'scraped_at', 'raw_response'
            ]
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                for transaction in transactions:
                    writer.writerow(transaction)
            
            logger.info(f"💾 Saved {len(transactions)} transactions to {self.csv_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving transactions to CSV: {e}")
    
    def run_listener(self):
        """Run the Chainflip API listener"""
        logger.info("🚀 Starting Chainflip API listener...")
        
        all_transactions = []
        
        for broker in self.shapeshift_brokers:
            logger.info(f"\n🔍 Processing {broker['name']}...")
            transactions = self.process_broker_data(broker)
            all_transactions.extend(transactions)
            
            # Rate limiting between brokers
            time.sleep(1)
        
        if all_transactions:
            self.save_transactions_to_csv(all_transactions)
        
        logger.info(f"\n✅ Chainflip API listener completed!")
        logger.info(f"   Total records found: {len(all_transactions)}")
        
        return len(all_transactions)

def main():
    """Main function"""
    try:
        listener = CSVChainflipAPIListener()
        total_transactions = listener.run_listener()
        
        print(f"\n🎯 Chainflip API Listener Results:")
        print(f"   Total transactions processed: {total_transactions}")
        print(f"   CSV file: {listener.csv_file}")
        
        if total_transactions == 0:
            print(f"\n⚠️  No transactions found. This could mean:")
            print(f"   1. Chainflip API is not running")
            print(f"   2. No recent activity for ShapeShift brokers")
            print(f"   3. API endpoints need to be configured")
            print(f"\n💡 To run the Chainflip API locally:")
            print(f"   git clone https://github.com/chainflip-io/chainflip-mainnet-apis.git")
            print(f"   cd chainflip-mainnet-apis")
            print(f"   docker compose up -d")
        
    except Exception as e:
        logger.error(f"❌ Error running Chainflip API listener: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
