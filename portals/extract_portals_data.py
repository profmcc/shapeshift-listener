#!/usr/bin/env python3
"""
Portals Affiliate Data Extractor
Extracts and displays Portals-specific affiliate fee events with correct decimals
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
from shared.token_utils import get_token_decimals
from web3 import Web3

def extract_portals_data():
    """Extract Portals-specific data from the comprehensive database"""
    db_path = "../shared/comprehensive_affiliate_data.db"
    if not os.path.exists(db_path):
        db_path = "portals_affiliate_events.db"
    
    conn = sqlite3.connect(db_path)
    query = '''
    SELECT DISTINCT tx_hash, timestamp, protocol, chain, from_asset, to_asset, 
           from_amount, to_amount, affiliate_fee, affiliate_fee_asset, 
           affiliate_address, pool, status
    FROM affiliate_fees 
    WHERE protocol = 'Portals' AND timestamp IS NOT NULL
    ORDER BY timestamp DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Optionally, set up a web3 instance for mainnet (or None if not available)
    try:
        w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
    except Exception:
        w3 = None

    print("=" * 80)
    print("PORTALS AFFILIATE EVENTS (CORRECTED DISPLAY)")
    print("=" * 80)
    
    if not df.empty:
        for idx, row in df.iterrows():
            # Get token decimals for display purposes only
            input_decimals = get_token_decimals(row['from_asset'], w3)
            output_decimals = get_token_decimals(row['to_asset'], w3)
            fee_decimals = get_token_decimals(row['affiliate_fee_asset'], w3) if row['affiliate_fee_asset'] else 18
            
            # The amounts in the database are already converted to human-readable format
            from_amount = float(row['from_amount']) if pd.notna(row['from_amount']) else 0
            to_amount = float(row['to_amount']) if pd.notna(row['to_amount']) else 0
            affiliate_fee = float(row['affiliate_fee']) if pd.notna(row['affiliate_fee']) else 0
            
            # Format token addresses for readability
            from_token = 'ETH' if row['from_asset'] == '0x0000000000000000000000000000000000000000' else row['from_asset'][:10] + '...'
            to_token = 'USDC' if row['to_asset'] == '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' else 'FOX' if row['to_asset'] == '0xc770eefad204b5180df6a14ee197d99d808ee52d' else row['to_asset'][:10] + '...'
            fee_token = 'USDC' if row['affiliate_fee_asset'] == '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' else 'FOX' if row['affiliate_fee_asset'] == '0xc770eefad204b5180df6a14ee197d99d808ee52d' else row['affiliate_fee_asset'][:10] + '...' if row['affiliate_fee_asset'] else 'None'
            
            print(f"Transaction: {row['tx_hash']}")
            if pd.notna(row['timestamp']) and row['timestamp'] > 0:
                time_str = datetime.fromtimestamp(row['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = "Unknown"
            print(f"Time: {time_str}")
            print(f"Chain: {row.get('chain', 'Ethereum')}")
            print(f"From: {from_amount:.8f} {from_token}")
            print(f"To: {to_amount:.8f} {to_token}")
            print(f"Affiliate Fee: {affiliate_fee:.8f} {fee_token}")
            print(f"Affiliate Address: {row.get('affiliate_address', 'N/A')}")
            print("-" * 80)
    else:
        print("No Portals events found")
    
    print(f"\nTotal Portals Events: {len(df)}")
    
    if not df.empty:
        print("\nTotal Affiliate Fees by Token:")
        affiliate_totals = df.groupby('affiliate_fee_asset')['affiliate_fee'].sum()
        for token, amount in affiliate_totals.items():
            if pd.notna(amount) and amount > 0:
                token_name = 'USDC' if token == '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' else 'FOX' if token == '0xc770eefad204b5180df6a14ee197d99d808ee52d' else token[:10] + '...'
                print(f"- {token_name}: {amount}")

if __name__ == "__main__":
    extract_portals_data() 