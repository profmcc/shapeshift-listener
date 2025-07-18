#!/usr/bin/env python3
"""
Fixed ShapeShift Relay Transaction Tracker

Properly tracks ShapeShift transactions on the relay contract with correct volume calculations
and saves them to a database.
"""

import requests
import time
import sqlite3
from datetime import datetime
from typing import Dict, List
from web3 import Web3
import os

# Configuration
ARBITRUM_RPC = f"https://arbitrum-mainnet.infura.io/v3/{os.getenv('INFURA_API_KEY', '208a3474635e4ebe8ee409cef3fbcd40')}"
CMC_API_KEY = "64dfaca3-439f-440d-8540-f11e06840ccc"
RELAY_CONTRACT = "0xBBbfD134E9b44BfB5123898BA36b01dE7ab93d98"
DB_PATH = "shapeshift_relay_transactions.db"

def init_database():
    """Initialize the database with relay transactions table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relay_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_hash TEXT UNIQUE NOT NULL,
            block_number INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            from_address TEXT NOT NULL,
            volume_usd REAL NOT NULL,
            tokens TEXT NOT NULL,
            raw_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("📁 Database initialized: shapeshift_relay_transactions.db")

def save_transactions_to_db(transactions: List[Dict]):
    """Save transactions to the database"""
    if not transactions:
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    for tx in transactions:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO relay_transactions 
                (tx_hash, block_number, timestamp, from_address, volume_usd, tokens, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tx['hash'],
                tx['block'],
                tx['timestamp'],
                tx['from'],
                tx['volume_usd'],
                ','.join(tx['tokens']),
                str(tx)
            ))
            if cursor.rowcount > 0:
                saved_count += 1
        except Exception as e:
            print(f"   ❌ Error saving transaction {tx['hash'][:16]}...: {e}")
    
    conn.commit()
    conn.close()
    
    if saved_count > 0:
        print(f"💾 Saved {saved_count} new transactions to database")
    else:
        print("💾 No new transactions to save (all already exist)")

def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM relay_transactions")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(volume_usd) FROM relay_transactions WHERE volume_usd > 0")
        total_volume = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM relay_transactions WHERE volume_usd > 0")
        volume_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM relay_transactions")
        time_range = cursor.fetchone()
        
        conn.close()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total transactions: {total_count}")
        print(f"   Total volume: ${total_volume:,.2f}")
        print(f"   Transactions with volume: {volume_count}")
        if time_range[0]:
            print(f"   Time range: {time_range[0]} to {time_range[1]}")
        
    except Exception as e:
        print(f"   ❌ Error getting database stats: {e}")

def get_real_time_prices() -> Dict[str, float]:
    """Get real-time token prices from CoinMarketCap"""
    print("🔄 Fetching real-time prices...")
    
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    params = {'symbol': 'USDC,ETH,USDT,WBTC,UNI,LINK,ARB', 'convert': 'USD'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        prices = {}
        if data['status']['error_code'] == 0:
            for symbol in ['USDC', 'ETH', 'USDT', 'WBTC', 'UNI', 'LINK', 'ARB']:
                if symbol in data['data']:
                    price = data['data'][symbol]['quote']['USD']['price']
                    prices[symbol] = price
                    print(f"   {symbol}: ${price:.4f}")
        
        return prices
        
    except Exception as e:
        print(f"   ❌ Price fetch failed: {e}")
        return {}

def parse_transfers_fixed(receipt, tokens) -> List[Dict]:
    """Parse ERC20 Transfer events with FIXED signature comparison"""
    transfers = []
    # FIXED: Remove 0x prefix from expected signature to match log format
    TRANSFER_SIG = "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    
    for log in receipt['logs']:
        try:
            if len(log['topics']) >= 3:
                # Get first topic (event signature) and normalize format
                topic0 = log['topics'][0]
                if hasattr(topic0, 'hex'):
                    topic0_str = topic0.hex()
                else:
                    topic0_str = str(topic0)
                
                # Remove 0x prefix if present for comparison
                if topic0_str.startswith('0x'):
                    topic0_str = topic0_str[2:]
                
                if topic0_str.lower() == TRANSFER_SIG.lower():
                    # Parse the transfer
                    from_topic = log['topics'][1]
                    to_topic = log['topics'][2]
                    
                    if hasattr(from_topic, 'hex'):
                        from_hex = from_topic.hex()
                    else:
                        from_hex = str(from_topic)
                        
                    if hasattr(to_topic, 'hex'):
                        to_hex = to_topic.hex()
                    else:
                        to_hex = str(to_topic)
                    
                    from_addr = "0x" + from_hex[-40:]
                    to_addr = "0x" + to_hex[-40:]
                    
                    # Parse amount from data
                    data = log['data']
                    if hasattr(data, 'hex'):
                        data_hex = data.hex()
                    else:
                        data_hex = str(data)
                        
                    if data_hex.startswith('0x'):
                        data_hex = data_hex[2:]
                        
                    amount = int(data_hex, 16) if data_hex else 0
                    
                    # Check if we know this token
                    token_addr = log['address'].lower()
                    token_info = tokens.get(token_addr)
                    
                    transfers.append({
                        "token": log['address'],
                        "from": from_addr,
                        "to": to_addr,
                        "amount": amount,
                        "token_info": token_info
                    })
                    
        except Exception as e:
            continue
            
    return transfers

def find_last_20_shapeshift_transactions():
    """Find the last 20 ShapeShift transactions with proper volume calculation"""
    
    w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
    token_prices = get_real_time_prices()
    
    # Arbitrum token addresses with real-time prices
    tokens = {
        "0xaf88d065e77c8cc2239327c5edb3a432268e5831": {"symbol": "USDC", "decimals": 6, "price": token_prices.get('USDC', 1.0)},
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1": {"symbol": "WETH", "decimals": 18, "price": token_prices.get('ETH', 3400)},
        "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": {"symbol": "USDT", "decimals": 6, "price": token_prices.get('USDT', 1.0)},
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8": {"symbol": "USDC.e", "decimals": 6, "price": token_prices.get('USDC', 1.0)},
        "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f": {"symbol": "WBTC", "decimals": 8, "price": token_prices.get('WBTC', 65000)},
        "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0": {"symbol": "UNI", "decimals": 18, "price": token_prices.get('UNI', 8)},
        "0xf97f4df75117a78c1a5a0dbb814af92458539fb4": {"symbol": "LINK", "decimals": 18, "price": token_prices.get('LINK', 15)},
        "0x912ce59144191c1204e64559fe8253a0e49e6548": {"symbol": "ARB", "decimals": 18, "price": token_prices.get('ARB', 0.8)},
    }
    
    print(f"\n🔍 Searching for last 20 ShapeShift transactions...")
    print(f"   Relay contract: {RELAY_CONTRACT}")
    print(f"   Chain: Arbitrum")
    
    try:
        latest_block = w3.eth.block_number
        print(f"   Latest block: {latest_block}")
        
        found_transactions = []
        blocks_scanned = 0
        max_blocks = 5000
        
        for block_num in range(latest_block, latest_block - max_blocks, -1):
            blocks_scanned += 1
            
            if blocks_scanned % 500 == 0:
                print(f"   Scanned {blocks_scanned} blocks, found {len(found_transactions)} transactions...")
            
            try:
                block = w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block['transactions']:
                    to_addr = tx['to'].lower() if tx['to'] else ""
                    
                    if to_addr == RELAY_CONTRACT.lower():
                        # Get transaction receipt
                        receipt = w3.eth.get_transaction_receipt(tx['hash'])
                        
                        if receipt['status'] == 1:  # Successful transaction
                            transfers = parse_transfers_fixed(receipt, tokens)
                            
                            # Calculate volume from first transfer
                            volume_usd = 0.0
                            tokens_involved = []
                            
                            if transfers:
                                first_transfer = transfers[0]
                                if first_transfer['token_info']:
                                    token_info = first_transfer['token_info']
                                    amount = first_transfer['amount'] / (10 ** token_info['decimals'])
                                    volume_usd = amount * token_info['price']
                                
                                # Collect all token symbols
                                for transfer in transfers:
                                    if transfer['token_info']:
                                        tokens_involved.append(transfer['token_info']['symbol'])
                            
                            # Get timestamp
                            timestamp = block['timestamp']
                            readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))
                            
                            tx_info = {
                                'hash': tx['hash'].hex(),
                                'block': block_num,
                                'timestamp': readable_time,
                                'from': tx['from'],
                                'volume_usd': volume_usd,
                                'tokens': list(set(tokens_involved)),
                                'transfer_count': len(transfers)
                            }
                            
                            found_transactions.append(tx_info)
                            
                            volume_str = f"${volume_usd:.2f}" if volume_usd > 0 else "NO VOLUME"
                            print(f"   ✅ Found #{len(found_transactions)}: {tx['hash'].hex()[:10]}... {volume_str}")
                            
                            if len(found_transactions) >= 20:
                                break
                                
            except Exception as e:
                continue
                
            if len(found_transactions) >= 20:
                break
                
            time.sleep(0.01)  # Rate limiting
            
        return found_transactions
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def display_results(transactions: List[Dict]):
    """Display results in a formatted table"""
    
    if not transactions:
        print("❌ No transactions found")
        return
        
    print(f"\n🎯 Last {len(transactions)} ShapeShift Relay Transactions:")
    print("=" * 80)
    
    total_volume = 0
    volume_count = 0
    
    for i, tx in enumerate(transactions, 1):
        tokens_str = ','.join(tx['tokens'][:4]) if tx['tokens'] else 'Unknown'
        from_short = tx['from'][:6] + "..." + tx['from'][-4:]
        
        volume_str = f"${tx['volume_usd']:.2f}" if tx['volume_usd'] > 0 else "NO VOLUME"
        
        print(f"\n#{i}: {tx['hash']}")
        print(f"   Block: {tx['block']}")
        print(f"   Time: {tx['timestamp']}")
        print(f"   Volume: {volume_str}")
        print(f"   Tokens: {tokens_str}")
        print(f"   From: {from_short}")
        print(f"   Arbiscan: https://arbiscan.io/tx/{tx['hash']}")
        
        if tx['volume_usd'] > 0:
            total_volume += tx['volume_usd']
            volume_count += 1
    
    print("=" * 80)
    print(f"Total Volume: ${total_volume:,.2f} ({volume_count} transactions with volume)")
    if volume_count > 0:
        print(f"Average Volume: ${total_volume/volume_count:.2f}")
    
    # Show issues
    no_volume_count = len(transactions) - volume_count
    if no_volume_count > 0:
        print(f"\n⚠️  {no_volume_count} transactions show NO VOLUME")
        print("   Likely causes: Unknown tokens not in our price dictionary")

def main():
    init_database() # Initialize database at the start
    transactions = find_last_20_shapeshift_transactions()
    save_transactions_to_db(transactions) # Save transactions to database
    display_results(transactions)
    get_database_stats() # Display database statistics

if __name__ == "__main__":
    main() 