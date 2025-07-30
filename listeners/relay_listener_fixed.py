#!/usr/bin/env python3
"""
ShapeShift Relay Affiliate Fee Tracker - Conservative Version

Tracks only actual affiliate fee transfers, not all transactions involving the affiliate address.
"""

import yaml
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3._utils.events import get_event_data, event_abi_to_log_topic
import os
import sys
import argparse
from dotenv import load_dotenv

# Add shared directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.custom_logging import setup_logger, get_logger
from shared.block_tracker import get_start_block, set_last_processed_block, init_database as init_block_tracker
from shared.token_name_resolver import TokenNameResolver

load_dotenv()
setup_logger("relay_listener_fixed")
logger = get_logger(__name__)

class FixedRelayListener:
    def __init__(self, config_path: str = "listeners/relay_listener_config.yaml"):
        """Initialize the Relay Listener"""
        self.config = self._load_config(config_path)
        self._init_database()
        
        # Initialize token name resolver
        self.token_resolver = TokenNameResolver()
        
        # Load the ABI
        with open("shared/abis/relay/ERC20Router.json", "r") as f:
            self.abi = json.load(f)
        
        # Get affiliate and claiming addresses
        self.affiliate_address = self.config['affiliate_address'].lower()
        self.claiming_address = self.config['claiming_address'].lower()
        
        logger.info(f"Fixed Relay Listener initialized")
        logger.info(f"Affiliate address: {self.affiliate_address}")
        logger.info(f"Claiming address: {self.claiming_address}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Replace environment variables in RPC URLs
        for chain in config['chains']:
            rpc_url = chain['rpc_url']
            if '${ALCHEMY_API_KEY}' in rpc_url:
                chain['rpc_url'] = rpc_url.replace('${ALCHEMY_API_KEY}', os.getenv('ALCHEMY_API_KEY', ''))
                if not chain['rpc_url'] or '${ALCHEMY_API_KEY}' in chain['rpc_url']:
                    raise ValueError("ALCHEMY_API_KEY environment variable not set")
        
        return config
    
    def _init_database(self):
        """Initialize the database and create tables"""
        db_path = self.config['db']['path']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create relay_affiliate_fees table for tracking actual affiliate fee events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relay_affiliate_fees_fixed (
                tx_hash TEXT,
                log_index INTEGER,
                chain TEXT,
                block_number INTEGER,
                timestamp INTEGER,
                event_type TEXT,
                affiliate_address TEXT,
                amount TEXT,
                token_address TEXT,
                token_address_name TEXT,
                solver_call_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (tx_hash, log_index)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relay_affiliate_fees_fixed_chain_block ON relay_affiliate_fees_fixed(chain, block_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relay_affiliate_fees_fixed_affiliate_addr ON relay_affiliate_fees_fixed(affiliate_address)')
        
        conn.commit()
        conn.close()
    
    def _get_chain_config(self, chain_name: str) -> Optional[Dict]:
        """Get configuration for a specific chain"""
        for chain in self.config['chains']:
            if chain['name'] == chain_name:
                return chain
        return None
    
    def _save_affiliate_fees(self, fees: List[Tuple]):
        """Save affiliate fee events to database"""
        if not fees:
            return
        
        conn = sqlite3.connect(self.config['db']['path'])
        cursor = conn.cursor()
        
        try:
            cursor.executemany('''
                INSERT OR IGNORE INTO relay_affiliate_fees_fixed 
                (tx_hash, log_index, chain, block_number, timestamp, event_type, affiliate_address, amount, token_address, token_address_name, solver_call_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', fees)
            
            conn.commit()
            logger.info(f"💾 Saved {len(fees)} Fixed Relay affiliate fees to database")
        except Exception as e:
            logger.error(f"Error saving affiliate fee events: {e}")
        finally:
            conn.close()
    
    def _is_actual_affiliate_fee(self, w3: Web3, receipt: Dict, amount: int) -> bool:
        """Check if this is actually an affiliate fee, not just any transfer"""
        # Only consider it an affiliate fee if:
        # 1. The amount is reasonable (between 0.001 ETH and 1 ETH in gwei)
        # 2. There's evidence of affiliate involvement in the transaction
        
        min_fee = 10**15  # 0.001 ETH in wei
        max_fee = 10**18  # 1 ETH in wei
        
        if amount < min_fee or amount > max_fee:
            return False
        
        # Check if there are any transfers to the affiliate address
        affiliate_involved = False
        for log in receipt['logs']:
            if not log['topics'] or len(log['topics']) < 3:
                continue
            
            # ERC-20 Transfer event
            if log['topics'][0].hex() == 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                to_addr = '0x' + log['topics'][2][-20:].hex()
                if to_addr.lower() == self.affiliate_address.lower():
                    affiliate_involved = True
                    break
        
        return affiliate_involved
    
    def _detect_affiliate_token(self, w3: Web3, receipt: Dict) -> str:
        """Detect the token involved in an affiliate transaction"""
        # Look for ERC-20 transfers to the affiliate address
        for log in receipt['logs']:
            if not log['topics'] or len(log['topics']) < 3:
                continue
            
            # ERC-20 Transfer event signature
            if log['topics'][0].hex() == 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                to_addr = '0x' + log['topics'][2][-20:].hex()
                
                # Check if this transfer is to the affiliate address
                if to_addr.lower() == self.affiliate_address.lower():
                    token_address = log['address']
                    logger.info(f"Found affiliate ERC-20 token: {token_address}")
                    return token_address
        
        # If no ERC-20 transfer found, it's likely a native token
        return '0x0000000000000000000000000000000000000000'

    def _process_transaction(self, w3: Web3, tx_hash: str, chain_name: str) -> List[Tuple]:
        """Process a single transaction for actual affiliate fee events"""
        fees = []
        
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            block = w3.eth.get_block(receipt['blockNumber'])
            timestamp = block['timestamp']
            
            # Only look for direct transfers to the affiliate address
            for log_index, log in enumerate(receipt['logs']):
                if not log['topics'] or len(log['topics']) < 3:
                    continue
                
                # ERC-20 Transfer event
                if log['topics'][0].hex() == 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    to_addr = '0x' + log['topics'][2][-20:].hex()
                    
                    # Check if this is a transfer to the affiliate address
                    if to_addr.lower() == self.affiliate_address.lower() and len(log['data']) >= 32:
                        try:
                            amount = int.from_bytes(log['data'][:32], 'big')
                            if amount > 0 and self._is_actual_affiliate_fee(w3, receipt, amount):
                                logger.info(f"Found ERC-20 affiliate fee in {tx_hash}: {amount} tokens")
                                
                                token_address = log['address']
                                token_name = self.token_resolver.get_token_name(token_address, chain_name)
                                
                                fees.append((
                                    tx_hash,
                                    log_index,
                                    chain_name,
                                    receipt['blockNumber'],
                                    timestamp,
                                    'ERC20Transfer',
                                    self.affiliate_address,
                                    str(amount),
                                    token_address,
                                    token_name,
                                    f"ERC-20 affiliate fee: {amount} tokens"
                                ))
                        except:
                            pass
            
            # Also check for native token transfers to affiliate address
            tx = w3.eth.get_transaction(tx_hash)
            if tx['to'] and tx['to'].lower() == self.affiliate_address.lower() and tx['value'] > 0:
                if self._is_actual_affiliate_fee(w3, receipt, tx['value']):
                    logger.info(f"Found native affiliate fee in {tx_hash}: {tx['value']} wei")
                    
                    fees.append((
                        tx_hash,
                        0,  # No log index for native transfers
                        chain_name,
                        receipt['blockNumber'],
                        timestamp,
                        'NativeTransfer',
                        self.affiliate_address,
                        str(tx['value']),
                        '0x0000000000000000000000000000000000000000',
                        'ETH',
                        f"Native affiliate fee: {tx['value']} wei"
                    ))
                
        except Exception as e:
            logger.error(f"Error processing transaction {tx_hash}: {e}")
        
        return fees
    
    def _scan_chain_blocks(self, chain_name: str, start_block: int, end_block: int, 
                          router_addresses: List[str]) -> List[Tuple]:
        """Scan blocks for actual affiliate fee transfers"""
        # Connect to RPC
        chain_config = self._get_chain_config(chain_name)
        if not chain_config:
            logger.error(f"Chain {chain_name} not found in configuration")
            return []
        
        w3 = Web3(Web3.HTTPProvider(chain_config['rpc_url']))
        logger.info(f"Connecting to {chain_name} RPC: {chain_config['rpc_url'][:50]}...")
        if not w3.is_connected():
            logger.error(f"Failed to connect to {chain_name} RPC")
            return []
        logger.info(f"Successfully connected to {chain_name} RPC")
        
        fees = []
        current_block = start_block
        
        while current_block <= end_block:
            batch_size = min(50, end_block - current_block + 1)
            batch_end = current_block + batch_size - 1
            
            print(f"Processing blocks {current_block}-{batch_end}...")
            
            # Get all transactions in this block range
            for block_num in range(current_block, batch_end + 1):
                try:
                    block = w3.eth.get_block(block_num, full_transactions=True)
                    
                    for tx in block['transactions']:
                        # Check if this transaction involves the affiliate address
                        if tx['to'] and tx['to'].lower() == self.affiliate_address.lower():
                            fees.extend(self._process_transaction(w3, tx['hash'].hex(), chain_name))
                        
                        # Also check transaction receipt for ERC-20 transfers to affiliate
                        receipt = w3.eth.get_transaction_receipt(tx['hash'])
                        for log in receipt['logs']:
                            if (log['topics'] and len(log['topics']) >= 3 and
                                log['topics'][0].hex() == 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'):
                                
                                to_addr = '0x' + log['topics'][2][-20:].hex()
                                if to_addr.lower() == self.affiliate_address.lower():
                                    fees.extend(self._process_transaction(w3, tx['hash'].hex(), chain_name))
                                    break
                
                except Exception as e:
                    logger.error(f"Error processing block {block_num}: {e}")
                    continue
            
            current_block = batch_end + 1
            logger.info(f"Processed {chain_name} blocks {current_block-batch_size}-{batch_end}")
            time.sleep(0.1)  # Add small delay between batches
            
        return fees
    
    def scan_chain(self, chain_name: str, start_block: Optional[int] = None, 
                  end_block: Optional[int] = None) -> int:
        """Scan a specific chain for actual affiliate fees"""
        print(f"Starting conservative scan for {chain_name}...")
        
        chain_config = self._get_chain_config(chain_name)
        if not chain_config:
            print(f"Chain {chain_name} not found in configuration")
            return 0
        
        if start_block is None:
            start_block = chain_config['start_block']
        if end_block is None:
            end_block = start_block + 1000  # Default to 1000 blocks
        
        print(f"Scanning {chain_name} from block {start_block} to {end_block}")
        print(f"Total blocks to scan: {end_block - start_block + 1}")
        logger.info(f"Scanning {chain_name} from block {start_block} to {end_block}")
        
        fees = self._scan_chain_blocks(
            chain_name, 
            start_block, 
            end_block, 
            chain_config['router_addresses']
        )
        
        if fees:
            self._save_affiliate_fees(fees)
        
        print(f"Found {len(fees)} actual affiliate fee events on {chain_name}")
        logger.info(f"Found {len(fees)} actual affiliate fee events on {chain_name}")
        return len(fees)
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.config['db']['path'])
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM relay_affiliate_fees_fixed")
        total_fees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT tx_hash) FROM relay_affiliate_fees_fixed")
        total_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT chain) FROM relay_affiliate_fees_fixed")
        chains_with_fees = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT chain, COUNT(*) as fee_count, COUNT(DISTINCT tx_hash) as tx_count
            FROM relay_affiliate_fees_fixed 
            GROUP BY chain
        """)
        chain_stats = {}
        for row in cursor.fetchall():
            chain_stats[row[0]] = {'fee_count': row[1], 'tx_count': row[2]}
        
        conn.close()
        
        return {
            'total_fees': total_fees,
            'total_transactions': total_transactions,
            'chains_with_fees': chains_with_fees,
            'chain_stats': chain_stats
        }

def main():
    parser = argparse.ArgumentParser(description='ShapeShift Relay Affiliate Fee Tracker - Conservative')
    parser.add_argument('--chain', required=True, help='Chain to scan (base, optimism, avalanche, polygon)')
    parser.add_argument('--from', dest='start_block', type=int, help='Start block number')
    parser.add_argument('--to', dest='end_block', type=str, default='latest', 
                       help='End block number or "latest"')
    parser.add_argument('--config', default='listeners/relay_listener_config.yaml',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        listener = FixedRelayListener(args.config)
        
        # Handle "latest" end block
        end_block = None
        if args.end_block != 'latest':
            end_block = int(args.end_block)
        
        fee_count = listener.scan_chain(args.chain, args.start_block, end_block)
        
        # Print statistics
        stats = listener.get_stats()
        logger.info(f"Scan complete. Database stats: {stats}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 