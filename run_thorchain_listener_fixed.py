#!/usr/bin/env python3
"""
THORChain Affiliate Fee Listener - Fixed Version
Based on actual API structure analysis
"""

import requests
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
THORCHAIN_MIDGARD_URL = 'https://midgard.ninerealms.com'
DB_PATH = 'thorchain_affiliate_fees.db'
SHAPESHIFT_AFFILIATE_IDS = ['ss']  # Based on CRM query

def init_database():
    """Initialize the THORChain affiliate fees database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thorchain_affiliate_fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_id TEXT UNIQUE,
            date TEXT,
            height INTEGER,
            from_address TEXT,
            to_address TEXT,
            affiliate_address TEXT,
            affiliate_fee_basis_points INTEGER,
            affiliate_fee_amount REAL,
            from_asset TEXT,
            to_asset TEXT,
            from_amount REAL,
            to_amount REAL,
            from_amount_usd REAL,
            to_amount_usd REAL,
            swap_path TEXT,
            is_streaming_swap BOOLEAN,
            liquidity_fee REAL,
            swap_slip INTEGER,
            created_at INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_thorchain_tx_id ON thorchain_affiliate_fees(tx_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_thorchain_affiliate ON thorchain_affiliate_fees(affiliate_address)
    ''')
    
    conn.commit()
    conn.close()
    logger.info("THORChain affiliate fees database initialized")

def fetch_thorchain_swap_actions(limit: int = 1000, offset: int = 0) -> List[Dict]:
    """Fetch THORChain swap actions from Midgard API"""
    logger.info(f"Fetching THORChain swap actions (limit: {limit}, offset: {offset})...")
    
    try:
        url = f"{THORCHAIN_MIDGARD_URL}/v2/actions"
        params = {
            'limit': limit,
            'offset': offset,
            'type': 'swap'  # Only swap actions
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        actions = data.get('actions', [])
        
        logger.info(f"Fetched {len(actions)} THORChain swap actions")
        return actions
        
    except Exception as e:
        logger.error(f"Error fetching THORChain actions: {e}")
        return []

def parse_thorchain_swap_for_affiliate(action: Dict) -> Optional[Dict]:
    """Parse a THORChain swap action for ShapeShift affiliate data"""
    try:
        # Extract basic transaction info - TX ID is in the input transaction
        in_txs = action.get('in', [])
        if not in_txs:
            return None
        
        tx_id = in_txs[0].get('txID', '')
        if not tx_id:
            return None
        
        # THORChain uses nanoseconds - convert to seconds
        date_timestamp_raw = action.get('date', 0)
        if not date_timestamp_raw:
            return None
        date_timestamp = int(date_timestamp_raw) / 1000000000
        
        height = action.get('height', 0)
        status = action.get('status', '')
        
        # Only process successful swaps
        if status != 'success':
            return None
        
        # Extract swap metadata
        metadata = action.get('metadata', {})
        swap = metadata.get('swap', {})
        
        # Check for affiliate address
        affiliate_address = swap.get('affiliateAddress', '')
        if affiliate_address not in SHAPESHIFT_AFFILIATE_IDS:
            return None
        
        # Extract affiliate fee information (can be string or int)
        affiliate_fee_raw = swap.get('affiliateFee', 0)
        try:
            affiliate_fee = int(affiliate_fee_raw) if affiliate_fee_raw else 0
        except (ValueError, TypeError):
            affiliate_fee = 0
        
        if affiliate_fee == 0:
            return None
        
        # Extract transaction details
        out_txs = action.get('out', [])
        
        if not out_txs:
            return None
        
        # Input details (we already have in_txs from above)
        in_tx = in_txs[0]
        from_address = in_tx.get('address', '')
        in_coins = in_tx.get('coins', [])
        
        if not in_coins:
            return None
        
        in_coin = in_coins[0]
        from_asset = in_coin.get('asset', '')
        try:
            from_amount_raw = int(in_coin.get('amount', 0))
        except (ValueError, TypeError):
            from_amount_raw = 0
        
        # Output details (find the main output, not affiliate fee)
        main_out = None
        affiliate_out = None
        
        for out_tx in out_txs:
            if out_tx.get('affiliate', False):
                affiliate_out = out_tx
            else:
                main_out = out_tx
        
        if not main_out:
            return None
        
        to_address = main_out.get('address', '')
        out_coins = main_out.get('coins', [])
        
        if not out_coins:
            return None
        
        out_coin = out_coins[0]
        to_asset = out_coin.get('asset', '')
        try:
            to_amount_raw = int(out_coin.get('amount', 0))
        except (ValueError, TypeError):
            to_amount_raw = 0
        
        # Extract USD prices (can be string or float)
        try:
            in_price_usd = float(swap.get('inPriceUSD', 0))
        except (ValueError, TypeError):
            in_price_usd = 0
        
        try:
            out_price_usd = float(swap.get('outPriceUSD', 0))
        except (ValueError, TypeError):
            out_price_usd = 0
        
        # Calculate amounts (THORChain uses 8 decimal places)
        from_amount = from_amount_raw / 1e8
        to_amount = to_amount_raw / 1e8
        
        # Calculate USD values
        from_amount_usd = from_amount * in_price_usd
        to_amount_usd = to_amount * out_price_usd
        
        # Calculate affiliate fee amount in USD
        affiliate_fee_percent = affiliate_fee / 10000  # Convert basis points to percentage
        affiliate_fee_amount = from_amount_usd * affiliate_fee_percent
        
        # Create swap path
        from_asset_name = from_asset.split('.')[-1] if '.' in from_asset else from_asset.split('-')[0]
        to_asset_name = to_asset.split('.')[-1] if '.' in to_asset else to_asset.split('-')[0]
        swap_path = f"{from_asset_name} -> {to_asset_name}"
        
        # Extract additional swap info
        is_streaming_swap = swap.get('isStreamingSwap', False)
        
        # Handle liquidity fee conversion
        liquidity_fee_raw = swap.get('liquidityFee', 0)
        try:
            liquidity_fee = int(liquidity_fee_raw) / 1e8 if liquidity_fee_raw else 0
        except (ValueError, TypeError):
            liquidity_fee = 0
        
        try:
            swap_slip = int(swap.get('swapSlip', 0))
        except (ValueError, TypeError):
            swap_slip = 0
        
        return {
            'tx_id': tx_id,
            'date': datetime.fromtimestamp(date_timestamp).isoformat(),
            'height': height,
            'from_address': from_address,
            'to_address': to_address,
            'affiliate_address': affiliate_address,
            'affiliate_fee_basis_points': affiliate_fee,
            'affiliate_fee_amount': affiliate_fee_amount,
            'from_asset': from_asset,
            'to_asset': to_asset,
            'from_amount': from_amount,
            'to_amount': to_amount,
            'from_amount_usd': from_amount_usd,
            'to_amount_usd': to_amount_usd,
            'swap_path': swap_path,
            'is_streaming_swap': is_streaming_swap,
            'liquidity_fee': liquidity_fee,
            'swap_slip': swap_slip,
            'created_at': int(time.time())
        }
        
    except Exception as e:
        logger.error(f"Error parsing THORChain swap action: {e}")
        return None

def store_thorchain_affiliate_fees(affiliate_swaps: List[Dict]):
    """Store THORChain affiliate fees in the database"""
    if not affiliate_swaps:
        logger.info("No THORChain affiliate fees to store")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stored_count = 0
    try:
        for swap in affiliate_swaps:
            cursor.execute('''
                INSERT OR IGNORE INTO thorchain_affiliate_fees 
                (tx_id, date, height, from_address, to_address, affiliate_address,
                 affiliate_fee_basis_points, affiliate_fee_amount, from_asset, to_asset,
                 from_amount, to_amount, from_amount_usd, to_amount_usd, swap_path,
                 is_streaming_swap, liquidity_fee, swap_slip, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                swap['tx_id'],
                swap['date'],
                swap['height'],
                swap['from_address'],
                swap['to_address'],
                swap['affiliate_address'],
                swap['affiliate_fee_basis_points'],
                swap['affiliate_fee_amount'],
                swap['from_asset'],
                swap['to_asset'],
                swap['from_amount'],
                swap['to_amount'],
                swap['from_amount_usd'],
                swap['to_amount_usd'],
                swap['swap_path'],
                swap['is_streaming_swap'],
                swap['liquidity_fee'],
                swap['swap_slip'],
                swap['created_at']
            ))
            if cursor.rowcount > 0:
                stored_count += 1
        
        conn.commit()
        logger.info(f"Stored {stored_count} new THORChain affiliate fees")
        
    except Exception as e:
        logger.error(f"Error storing THORChain affiliate fees: {e}")
    finally:
        conn.close()

def get_database_stats():
    """Get THORChain affiliate fees database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM thorchain_affiliate_fees")
        total_fees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT tx_id) FROM thorchain_affiliate_fees")
        unique_txs = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(affiliate_fee_amount) FROM thorchain_affiliate_fees")
        total_fee_amount = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(from_amount_usd) FROM thorchain_affiliate_fees")
        total_volume = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT MIN(date), MAX(date) FROM thorchain_affiliate_fees")
        date_range = cursor.fetchone()
        min_date, max_date = date_range if date_range[0] else (None, None)
        
        print(f"\n=== THORChain Affiliate Fees Database Statistics ===")
        print(f"Total affiliate fee records: {total_fees}")
        print(f"Unique transactions: {unique_txs}")
        print(f"Total affiliate fees earned: ${total_fee_amount:.2f}")
        print(f"Total volume processed: ${total_volume:.2f}")
        if min_date and max_date:
            print(f"Date range: {min_date} - {max_date}")
        
        # Show recent affiliate fees
        cursor.execute('''
            SELECT tx_id, date, swap_path, affiliate_fee_amount, from_amount_usd 
            FROM thorchain_affiliate_fees 
            ORDER BY date DESC 
            LIMIT 5
        ''')
        recent_fees = cursor.fetchall()
        
        if recent_fees:
            print(f"\n📋 Recent THORChain Affiliate Fees:")
            for tx_id, date, swap_path, fee_amount, volume in recent_fees:
                print(f"  🔗 {tx_id[:20]}...")
                print(f"     Date: {date}")
                print(f"     Path: {swap_path}")
                print(f"     Volume: ${volume:.2f}")
                print(f"     Fee: ${fee_amount:.4f}")
                print()
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
    finally:
        conn.close()

def fetch_thorchain_affiliate_fees_batch(max_actions: int = 5000):
    """Fetch THORChain affiliate fees in batches"""
    logger.info(f"Starting THORChain affiliate fee collection (max {max_actions} actions)...")
    
    init_database()
    
    total_processed = 0
    total_affiliate_fees = 0
    offset = 0
    batch_size = 100  # Smaller batches for testing
    
    while total_processed < max_actions:
        # Fetch a batch of actions
        actions = fetch_thorchain_swap_actions(limit=batch_size, offset=offset)
        
        if not actions:
            logger.info("No more actions to fetch")
            break
        
        # Parse for affiliate fees
        affiliate_swaps = []
        debug_count = 0
        for action in actions:
            # Debug info for first few actions
            if debug_count < 3:
                metadata = action.get('metadata', {})
                swap = metadata.get('swap', {})
                affiliate_addr = swap.get('affiliateAddress', '')
                status = action.get('status', '')
                logger.info(f"  Debug action {debug_count}: status={status}, affiliate='{affiliate_addr}'")
                debug_count += 1
            
            parsed = parse_thorchain_swap_for_affiliate(action)
            if parsed:
                affiliate_swaps.append(parsed)
        
        # Store affiliate fees
        store_thorchain_affiliate_fees(affiliate_swaps)
        
        total_processed += len(actions)
        total_affiliate_fees += len(affiliate_swaps)
        
        logger.info(f"Processed {total_processed} actions, found {len(affiliate_swaps)} affiliate fees in this batch")
        
        # Move to next batch
        offset += batch_size
        
        # Short delay to be respectful to the API
        time.sleep(0.5)
    
    logger.info(f"Completed! Processed {total_processed} total actions, found {total_affiliate_fees} affiliate fees")
    get_database_stats()

def main():
    """Main function to run THORChain affiliate fee collection"""
    logger.info("Starting THORChain affiliate fee listener...")
    
    try:
        # Start with a smaller batch for testing
        fetch_thorchain_affiliate_fees_batch(max_actions=2000)
    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    
    logger.info("THORChain affiliate fee collection completed!")

if __name__ == "__main__":
    main() 