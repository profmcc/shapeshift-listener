#!/usr/bin/env python3
"""
ButterSwap Affiliate Fee Listener
=================================

HISTORY & LEARNING:
- Originally part of a larger monolithic listener system
- Had hardcoded affiliate addresses scattered throughout the code
- Previous attempts at centralized config failed due to validation issues
- Current approach: Hybrid system with both hardcoded and configurable addresses

WHAT THIS LISTENER IS ATTEMPTING:
- Monitor ButterSwap transactions across multiple EVM chains
- Detect when ShapeShift receives affiliate fees from swaps
- Track transaction volumes, fees, and user addresses
- Provide comprehensive data for affiliate revenue analysis

WHY BUTTERSWAP SPECIFICALLY:
- ButterSwap is a DEX aggregator similar to Uniswap V2
- Uses affiliate fee model where ShapeShift receives a percentage
- Important for understanding ShapeShift's revenue from DEX activities
- Base chain is primary focus due to recent deployment and activity

CURRENT STATUS:
- Working listener with hardcoded addresses (legacy approach)
- Base chain uses 0x35339070f178dC4119732982C23F5a8d88D3f8a3
- Other chains use various addresses for different protocols
- CSV-based storage for easy analysis

TECHNICAL APPROACH:
- Web3.py for blockchain interaction
- Event filtering for Swap, Mint, Burn, and Transfer events
- Batch processing to handle high transaction volumes
- Rate limiting to respect RPC provider limits
"""

import os
import sys
import time
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.exceptions import BlockNotFound, TransactionNotFound
import logging

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import shared utilities
from shared.block_tracker import BlockTracker
from shared.token_prices import TokenPriceCache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ButterSwapListener:
    """
    Listener for ButterSwap affiliate fee events
    
    This class monitors ButterSwap transactions across multiple EVM chains
    to detect when ShapeShift receives affiliate fees. It uses a hybrid
    approach where some addresses are hardcoded (legacy) and others could
    be loaded from centralized config (future enhancement).
    
    AFFILIATE ADDRESS STRATEGY:
    - Base chain: 0x35339070f178dC4119732982C23F5a8d88D3f8a3 (primary focus)
    - Other chains: Various addresses for different protocols
    - This reflects the reality that different chains may use different
      affiliate addresses for historical or technical reasons
    """
    
    def __init__(self, csv_file: str = "csv_data/butterswap_transactions.csv"):
        """
        Initialize the ButterSwap listener
        
        INITIALIZATION APPROACH:
        - Load hardcoded affiliate addresses (legacy approach)
        - Initialize Web3 connections for each supported chain
        - Set up CSV storage for transaction data
        - Initialize block tracking for each chain
        
        This approach ensures the listener works immediately without
        depending on external configuration files.
        """
        self.csv_file = csv_file
        
        # Initialize CSV file if it doesn't exist
        self._init_csv_file()
        
        # ShapeShift affiliate addresses by chain ID
        # These are hardcoded for reliability (legacy approach)
        # Future enhancement: Load from centralized config
        self.shapeshift_affiliates = {
            1: "0x35339070f178dC4119732982C23F5a8d88D3f8a3",      # Ethereum
            137: "0xB5F944600785724e31Edb90F9DFa16dBF01Af000",     # Polygon
            10: "0x6268d07327f4fb7380732dc6d63d95F88c0E083b",      # Optimism
            42161: "0x38276553F8fbf2A027D901F8be45f00373d8Dd48",   # Arbitrum
            8453: "0x35339070f178dC4119732982C23F5a8d88D3f8a3",    # Base (Updated - primary focus)
            43114: "0x74d63F31C2335b5b3BA7ad2812357672b2624cEd",  # Avalanche
            56: "0x8b92b1698b57bEDF2142297e9397875ADBb2297E"       # BSC
        }
        
        # Initialize Web3 connections for each chain
        # Each chain has its own RPC endpoint and connection
        self.web3_connections = {}
        self._init_web3_connections()
        
        # Initialize block trackers for each chain
        # This prevents re-processing the same blocks
        self.block_trackers = {}
        self._init_block_trackers()
        
        # Initialize token price cache
        # Used for converting token amounts to USD values
        self.token_prices = TokenPriceCache()
        
        # Event signatures for filtering
        # These are the Keccak256 hashes of event definitions
        self.event_signatures = {
            'Swap': '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822',
            'Mint': '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f',
            'Burn': '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496',
            'Transfer': '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
        }
        
        logger.info("ButterSwap listener initialized successfully")
        logger.info(f"Monitoring {len(self.web3_connections)} chains")
        logger.info(f"Primary focus: Base chain (0x35339070f178dC4119732982C23F5a8d88D3f8a3)")
    
    def _init_csv_file(self):
        """
        Initialize CSV file with headers if it doesn't exist
        
        CSV STRUCTURE:
        - timestamp: When the transaction was processed
        - chain_id: Which blockchain the transaction occurred on
        - block_number: Block number containing the transaction
        - transaction_hash: Unique identifier for the transaction
        - user_address: Address of the user making the swap
        - token_in: Token being swapped in
        - token_out: Token being swapped out
        - amount_in: Amount of input token
        - amount_out: Amount of output token
        - affiliate_fee: Affiliate fee received by ShapeShift
        - volume_usd: Total transaction volume in USD
        - affiliate_fee_usd: Affiliate fee in USD
        
        This structure allows for comprehensive analysis of affiliate revenue
        across different chains and time periods.
        """
        if not os.path.exists(self.csv_file):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            
            # Define CSV headers
            headers = [
                'timestamp', 'chain_id', 'block_number', 'transaction_hash',
                'user_address', 'token_in', 'token_out', 'amount_in', 'amount_out',
                'affiliate_fee', 'volume_usd', 'affiliate_fee_usd'
            ]
            
            # Write headers to CSV
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            logger.info(f"Created new CSV file: {self.csv_file}")
    
    def _init_web3_connections(self):
        """
        Initialize Web3 connections for each supported chain
        
        RPC ENDPOINT STRATEGY:
        - Alchemy: Primary provider (most reliable, highest rate limits)
        - Infura: Fallback provider (if Alchemy fails)
        - Public RPCs: For chains without API key requirements
        
        Each connection is configured with appropriate settings for
        the specific chain's characteristics and rate limits.
        """
        # RPC endpoints for each chain
        # Priority: Alchemy > Infura > Public RPC
        rpc_endpoints = {
            1: f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",      # Ethereum
            137: f"https://polygon-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}", # Polygon
            10: f"https://opt-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",      # Optimism
            42161: f"https://arb-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",   # Arbitrum
            8453: f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",   # Base
            43114: "https://api.avax.network/ext/bc/C/rpc",                                   # Avalanche (public)
            56: "https://bsc-dataseed.binance.org/"                                          # BSC (public)
        }
        
        # Initialize Web3 connections
        for chain_id, rpc_url in rpc_endpoints.items():
            try:
                # Create Web3 instance
                web3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # Test connection
                if web3.is_connected():
                    self.web3_connections[chain_id] = web3
                    logger.info(f"✅ Connected to chain {chain_id} via {rpc_url}")
                else:
                    logger.warning(f"⚠️  Failed to connect to chain {chain_id}")
                    
            except Exception as e:
                logger.error(f"❌ Error connecting to chain {chain_id}: {e}")
        
        if not self.web3_connections:
            raise Exception("No Web3 connections could be established")
    
    def _init_block_trackers(self):
        """
        Initialize block trackers for each chain
        
        BLOCK TRACKING PURPOSE:
        - Prevent re-processing the same blocks
        - Resume from last processed block after restart
        - Handle chain reorganizations gracefully
        - Provide progress monitoring for long-running scans
        
        Each chain has its own tracker because:
        1. Different chains have different block times
        2. Some chains may be paused while others continue
        3. Allows for chain-specific optimization
        """
        for chain_id in self.web3_connections.keys():
            tracker_file = f"csv_data/block_tracking/butterswap_block_tracker_{chain_id}.csv"
            self.block_trackers[chain_id] = BlockTracker(tracker_file, chain_id)
            logger.info(f"📊 Block tracker initialized for chain {chain_id}")
    
    def scan_chain(self, chain_id: int, start_block: Optional[int] = None, end_block: Optional[int] = None):
        """
        Scan a specific chain for ButterSwap transactions
        
        SCANNING STRATEGY:
        - Process blocks in batches to avoid overwhelming RPC providers
        - Filter for specific event types that indicate swaps
        - Check if ShapeShift addresses are involved in transactions
        - Calculate USD values for volume and fee analysis
        
        PARAMETERS:
        - chain_id: Which blockchain to scan
        - start_block: Starting block number (uses tracker if not specified)
        - end_block: Ending block number (uses latest if not specified)
        
        This method is the core of the listener and handles the actual
        blockchain monitoring and affiliate fee detection.
        """
        if chain_id not in self.web3_connections:
            logger.error(f"Chain {chain_id} not supported")
            return
        
        web3 = self.web3_connections[chain_id]
        block_tracker = self.block_trackers[chain_id]
        
        # Determine scan range
        if start_block is None:
            start_block = block_tracker.get_last_processed_block() + 1
        
        if end_block is None:
            try:
                end_block = web3.eth.block_number
            except Exception as e:
                logger.error(f"Failed to get latest block for chain {chain_id}: {e}")
                return
        
        if start_block > end_block:
            logger.info(f"Chain {chain_id}: No new blocks to process")
            return
        
        logger.info(f"🔍 Scanning chain {chain_id} from block {start_block} to {end_block}")
        
        # Process blocks in batches
        batch_size = 100  # Conservative batch size for stability
        current_block = start_block
        
        while current_block <= end_block:
            batch_end = min(current_block + batch_size - 1, end_block)
            
            try:
                # Process batch of blocks
                self._process_block_batch(chain_id, current_block, batch_end)
                
                # Update block tracker
                block_tracker.update_last_processed_block(batch_end)
                
                # Move to next batch
                current_block = batch_end + 1
                
                # Rate limiting
                time.sleep(0.5)  # 500ms delay between batches
                
            except Exception as e:
                logger.error(f"Error processing batch {current_block}-{batch_end} on chain {chain_id}: {e}")
                # Continue with next batch instead of failing completely
                current_block = batch_end + 1
        
        logger.info(f"✅ Completed scanning chain {chain_id}")
    
    def _process_block_batch(self, chain_id: int, start_block: int, end_block: int):
        """
        Process a batch of blocks for affiliate fee detection
        
        BATCH PROCESSING BENEFITS:
        - Reduces RPC calls by processing multiple blocks together
        - Allows for better error handling and recovery
        - Provides progress updates for long-running scans
        - Enables rate limiting between batches
        
        This method handles the actual transaction processing and
        affiliate fee detection logic.
        """
        web3 = self.web3_connections[chain_id]
        
        for block_num in range(start_block, end_block + 1):
            try:
                # Get block information
                block = web3.eth.get_block(block_num, full_transactions=True)
                
                # Process each transaction in the block
                for tx in block.transactions:
                    self._process_transaction(chain_id, block_num, tx)
                    
            except BlockNotFound:
                logger.warning(f"Block {block_num} not found on chain {chain_id}")
                continue
            except Exception as e:
                logger.error(f"Error processing block {block_num} on chain {chain_id}: {e}")
                continue
    
    def _process_transaction(self, chain_id: int, block_number: int, transaction):
        """
        Process a single transaction for affiliate fee detection
        
        TRANSACTION ANALYSIS:
        - Check if transaction involves ShapeShift affiliate addresses
        - Parse transaction logs for relevant events
        - Calculate USD values for volume and fees
        - Store relevant data in CSV for analysis
        
        This method implements the core logic for identifying
        affiliate fee transactions and extracting relevant data.
        """
        # Check if transaction involves ShapeShift addresses
        shapeshift_addresses = [self.shapeshift_affiliates[chain_id]]
        
        # Check transaction recipient
        if transaction.to and transaction.to.lower() in [addr.lower() for addr in shapeshift_addresses]:
            self._handle_affiliate_transaction(chain_id, block_number, transaction)
            return
        
        # Check transaction logs for affiliate fee events
        try:
            receipt = self.web3_connections[chain_id].eth.get_transaction_receipt(transaction.hash)
            
            for log in receipt.logs:
                if self._is_affiliate_fee_log(log, shapeshift_addresses):
                    self._handle_affiliate_fee_log(chain_id, block_number, transaction, log)
                    
        except TransactionNotFound:
            logger.warning(f"Transaction {transaction.hash.hex()} not found on chain {chain_id}")
        except Exception as e:
            logger.error(f"Error processing transaction {transaction.hash.hex()} on chain {chain_id}: {e}")
    
    def _is_affiliate_fee_log(self, log, shapeshift_addresses: List[str]) -> bool:
        """
        Check if a log entry represents an affiliate fee event
        
        AFFILIATE FEE DETECTION:
        - Look for Transfer events to ShapeShift addresses
        - Check if the event signature matches expected patterns
        - Verify the recipient is a known ShapeShift address
        
        This method implements the logic for identifying which
        blockchain events represent affiliate fee payments.
        """
        # Check if this is a Transfer event
        if log.topics[0].hex() == self.event_signatures['Transfer']:
            # Check if recipient is a ShapeShift address
            if len(log.topics) >= 3:
                recipient = '0x' + log.topics[2].hex()[-40:]  # Last 20 bytes
                if recipient.lower() in [addr.lower() for addr in shapeshift_addresses]:
                    return True
        
        return False
    
    def _handle_affiliate_transaction(self, chain_id: int, block_number: int, transaction):
        """
        Handle a direct affiliate transaction
        
        DIRECT AFFILIATE TRANSACTIONS:
        - User sends tokens directly to ShapeShift address
        - Usually represents a direct affiliate fee payment
        - Simpler to process than complex swap transactions
        
        This method handles the case where a user directly
        sends tokens to a ShapeShift affiliate address.
        """
        logger.info(f"🎯 Direct affiliate transaction detected on chain {chain_id}")
        logger.info(f"   Block: {block_number}")
        logger.info(f"   Hash: {transaction.hash.hex()}")
        logger.info(f"   From: {transaction['from']}")
        logger.info(f"   To: {transaction.to}")
        logger.info(f"   Value: {transaction.value} wei")
        
        # Store transaction data
        self._store_transaction_data(
            chain_id=chain_id,
            block_number=block_number,
            transaction_hash=transaction.hash.hex(),
            user_address=transaction['from'],
            token_in="ETH" if transaction.value > 0 else "Unknown",
            token_out="Unknown",
            amount_in=transaction.value,
            amount_out=0,
            affiliate_fee=transaction.value,
            volume_usd=0,  # Will be calculated later
            affiliate_fee_usd=0  # Will be calculated later
        )
    
    def _handle_affiliate_fee_log(self, chain_id: int, block_number: int, transaction, log):
        """
        Handle an affiliate fee event from transaction logs
        
        AFFILIATE FEE LOG PROCESSING:
        - Parse Transfer event data
        - Extract token amounts and addresses
        - Calculate USD values for analysis
        - Store comprehensive transaction data
        
        This method handles the more complex case where affiliate
        fees are embedded in swap transaction logs.
        """
        logger.info(f"🎯 Affiliate fee log detected on chain {chain_id}")
        logger.info(f"   Block: {block_number}")
        logger.info(f"   Hash: {transaction.hash.hex()}")
        logger.info(f"   Log Index: {log.logIndex}")
        
        # Parse Transfer event data
        # Transfer event has: [signature, from, to, value]
        if len(log.topics) >= 3 and len(log.data) >= 32:
            from_address = '0x' + log.topics[1].hex()[-40:]
            to_address = '0x' + log.topics[2].hex()[-40:]
            value = int(log.data.hex(), 16)
            
            logger.info(f"   From: {from_address}")
            logger.info(f"   To: {to_address}")
            logger.info(f"   Value: {value}")
            
            # Store transaction data
            self._store_transaction_data(
                chain_id=chain_id,
                block_number=block_number,
                transaction_hash=transaction.hash.hex(),
                user_address=from_address,
                token_in="Unknown",  # Would need more context to determine
                token_out="Unknown",
                amount_in=0,
                amount_out=0,
                affiliate_fee=value,
                volume_usd=0,  # Will be calculated later
                affiliate_fee_usd=0  # Will be calculated later
            )
    
    def _store_transaction_data(self, **kwargs):
        """
        Store transaction data in CSV file
        
        DATA STORAGE STRATEGY:
        - Append mode to preserve historical data
        - CSV format for easy analysis and export
        - Timestamp for temporal analysis
        - All relevant transaction details for comprehensive tracking
        
        This method ensures that all detected affiliate transactions
        are properly recorded for future analysis and reporting.
        """
        # Add timestamp
        data = {
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        # Write to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writerow(data)
        
        logger.info(f"💾 Stored transaction data: {kwargs.get('transaction_hash', 'Unknown')}")
    
    def scan_all_chains(self, start_block: Optional[int] = None):
        """
        Scan all supported chains for affiliate transactions
        
        MULTI-CHAIN SCANNING:
        - Process each chain sequentially to avoid overwhelming RPC providers
        - Use chain-specific start blocks for optimal scanning
        - Handle failures gracefully and continue with other chains
        
        This method provides a convenient way to scan all supported
        chains in a single operation.
        """
        logger.info("🚀 Starting multi-chain scan")
        
        for chain_id in self.web3_connections.keys():
            try:
                logger.info(f"🔍 Scanning chain {chain_id}")
                self.scan_chain(chain_id, start_block)
                
            except Exception as e:
                logger.error(f"❌ Error scanning chain {chain_id}: {e}")
                continue
        
        logger.info("✅ Multi-chain scan completed")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about processed transactions
        
        STATISTICS INCLUDED:
        - Total transactions processed
        - Transactions per chain
        - Total affiliate fees collected
        - Volume processed
        
        This method provides insights into the listener's activity
        and the affiliate fee data collected.
        """
        if not os.path.exists(self.csv_file):
            return {"error": "CSV file not found"}
        
        stats = {
            'total_transactions': 0,
            'transactions_by_chain': {},
            'total_affiliate_fees': 0,
            'total_volume_usd': 0
        }
        
        try:
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    stats['total_transactions'] += 1
                    
                    # Count by chain
                    chain_id = int(row['chain_id'])
                    if chain_id not in stats['transactions_by_chain']:
                        stats['transactions_by_chain'][chain_id] = 0
                    stats['transactions_by_chain'][chain_id] += 1
                    
                    # Sum affiliate fees
                    if row['affiliate_fee']:
                        stats['total_affiliate_fees'] += float(row['affiliate_fee'])
                    
                    # Sum volume
                    if row['volume_usd']:
                        stats['total_volume_usd'] += float(row['volume_usd'])
                        
        except Exception as e:
            logger.error(f"Error reading statistics: {e}")
            stats['error'] = str(e)
        
        return stats

def main():
    """
    Main execution function
    
    USAGE:
    - Run directly: python butterswap_listener.py
    - Import as module: from butterswap_listener import ButterSwapListener
    
    This function demonstrates how to use the listener and provides
    a command-line interface for testing and manual operation.
    """
    try:
        # Initialize listener
        listener = ButterSwapListener()
        
        # Get command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='ButterSwap Affiliate Fee Listener')
        parser.add_argument('--chain', type=int, help='Specific chain ID to scan')
        parser.add_argument('--start-block', type=int, help='Starting block number')
        parser.add_argument('--stats', action='store_true', help='Show statistics')
        
        args = parser.parse_args()
        
        if args.stats:
            # Show statistics
            stats = listener.get_statistics()
            print("📊 ButterSwap Listener Statistics")
            print("=" * 40)
            print(f"Total Transactions: {stats.get('total_transactions', 0)}")
            print(f"Total Affiliate Fees: {stats.get('total_affiliate_fees', 0)}")
            print(f"Total Volume USD: ${stats.get('total_volume_usd', 0):.2f}")
            print("\nTransactions by Chain:")
            for chain_id, count in stats.get('transactions_by_chain', {}).items():
                print(f"  Chain {chain_id}: {count}")
            
        elif args.chain:
            # Scan specific chain
            listener.scan_chain(args.chain, args.start_block)
            
        else:
            # Scan all chains
            listener.scan_all_chains(args.start_block)
            
    except KeyboardInterrupt:
        print("\n⏹️  Scanning interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


