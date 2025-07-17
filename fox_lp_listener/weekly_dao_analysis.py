#!/usr/bin/env python3
"""
Weekly DAO FOX Pool Activity Analysis for Q2 2025
Analyzes net add/remove activity on a weekly basis with color-coded visualization.
"""

import os
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from web3 import Web3
import requests
import pandas as pd
import numpy as np
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
from colorama import init, Fore, Back, Style
# import matplotlib.pyplot as plt
# import seaborn as sns

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
DB_PATH = 'fox_pools_analysis.db'

# DAO Treasury Addresses (matching the main script)
DAO_TREASURY_ADDRESSES = {
    'ethereum': Web3.to_checksum_address('0x90a48d5cf7343b08da12e067680b4c6dbfe551be'),
    'arbitrum': Web3.to_checksum_address('0x38276553f8fbf2a027d901f8be45f00373d8dd48'),
    'optimism': Web3.to_checksum_address('0x6268d07327f4fb7380732dc6d63d95f88c0e083b'),
}

# RPC endpoints
RPC_ENDPOINTS = {
    'ethereum': 'https://eth.llamarpc.com',
    'arbitrum': 'https://arb1.arbitrum.io/rpc',
    'optimism': 'https://mainnet.optimism.io',
}

# FOX pools to analyze
FOX_POOLS = [
    {
        'chain_name': 'ethereum',
        'pool_address': Web3.to_checksum_address('0x470e8de2ebaef52014a47cb5e6af86884947f08c'),
        'pool_name': 'WETH/FOX V2',
        'type': 'uniswap_v2',
    },
    {
        'chain_name': 'arbitrum',
        'pool_address': Web3.to_checksum_address('0x5f6ce0ca13b87bd738519545d3e018e70e339c24'),
        'pool_name': 'WETH/FOX V2',
        'type': 'uniswap_v2',
    },
    {
        'chain_name': 'arbitrum',
        'pool_address': Web3.to_checksum_address('0x76d4d1eaa0c4b3645e75c46e573c1d4f75e9041e'),
        'pool_name': 'WETH/FOX V3',
        'type': 'uniswap_v3',
    },
]

# Q2 2025 date range (April 1 - June 30, 2025)
# Note: Since we're in July 2025, this period is in the past
Q2_START = datetime(2025, 4, 1)
Q2_END = datetime(2025, 6, 30, 23, 59, 59)

# For demonstration, also analyze recent activity (last 3 months)
RECENT_START = datetime(2025, 4, 1)  # April 2025
RECENT_END = datetime(2025, 7, 9)    # Current date

def get_web3_connection(chain_name: str) -> Web3:
    """Get Web3 connection for a chain"""
    rpc_url = RPC_ENDPOINTS[chain_name]
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if chain_name in ['arbitrum', 'polygon']:
            w3.middleware_onion.add(ExtraDataToPOAMiddleware)
        w3.eth.block_number  # Test connection
        logger.info(f"Connected to {chain_name}: {rpc_url}")
        return w3
    except Exception as e:
        logger.error(f"Failed to connect to {chain_name}: {e}")
        raise

def get_block_by_timestamp(w3: Web3, target_timestamp: int) -> int:
    """Get block number closest to target timestamp using binary search"""
    latest_block = w3.eth.get_block('latest')
    latest_timestamp = latest_block['timestamp']
    
    if target_timestamp >= latest_timestamp:
        return latest_block['number']
    
    # Binary search for the block
    low, high = 0, latest_block['number']
    
    while high - low > 1:
        mid = (low + high) // 2
        try:
            mid_block = w3.eth.get_block(mid)
            mid_timestamp = mid_block['timestamp']
            
            if mid_timestamp < target_timestamp:
                low = mid
            else:
                high = mid
        except Exception as e:
            logger.warning(f"Error getting block {mid}: {e}")
            break
    
    return high

def fetch_uniswap_v2_events(w3: Web3, pool_address: str, start_block: int, end_block: int, dao_address: str) -> List[Dict]:
    """Fetch Uniswap V2 Mint/Burn events for DAO address"""
    events = []
    
    # Uniswap V2 event signatures
    mint_signature = w3.keccak(text="Mint(address,uint256,uint256)").hex()
    burn_signature = w3.keccak(text="Burn(address,uint256,uint256,address)").hex()
    
    # Query events in chunks to avoid rate limits (max 1000 blocks per request)
    chunk_size = 1000
    for chunk_start in range(start_block, end_block + 1, chunk_size):
        chunk_end = min(chunk_start + chunk_size - 1, end_block)
        
        try:
            # Get Mint events
            mint_filter = {
                'fromBlock': chunk_start,
                'toBlock': chunk_end,
                'address': pool_address,
                'topics': [mint_signature]
            }
            mint_logs = w3.eth.get_logs(mint_filter)
            
            for log in mint_logs:
                tx = w3.eth.get_transaction(log['transactionHash'])
                if tx['from'].lower() == dao_address.lower():
                    events.append({
                        'type': 'mint',
                        'block_number': log['blockNumber'],
                        'tx_hash': log['transactionHash'].hex(),
                        'timestamp': w3.eth.get_block(log['blockNumber'])['timestamp'],
                        'from_address': tx['from'],
                        'data': log['data']
                    })
            
            # Get Burn events  
            burn_filter = {
                'fromBlock': chunk_start,
                'toBlock': chunk_end,
                'address': pool_address,
                'topics': [burn_signature]
            }
            burn_logs = w3.eth.get_logs(burn_filter)
            
            for log in burn_logs:
                tx = w3.eth.get_transaction(log['transactionHash'])
                if tx['from'].lower() == dao_address.lower():
                    events.append({
                        'type': 'burn',
                        'block_number': log['blockNumber'],
                        'tx_hash': log['transactionHash'].hex(),
                        'timestamp': w3.eth.get_block(log['blockNumber'])['timestamp'],
                        'from_address': tx['from'],
                        'data': log['data']
                    })
                    
        except Exception as e:
            logger.warning(f"Error fetching events for blocks {chunk_start}-{chunk_end}: {e}")
            time.sleep(2)  # Rate limit - longer delay on error
            continue  # Skip this chunk and continue with next
            
    return events

def analyze_weekly_activity(chain_name: str, pool_info: Dict, dao_address: str) -> List[Dict]:
    """Analyze weekly DAO activity for a specific pool"""
    logger.info(f"Analyzing {pool_info['pool_name']} on {chain_name}")
    
    w3 = get_web3_connection(chain_name)
    
    # Get block numbers for Q2 2025
    start_timestamp = int(Q2_START.timestamp())
    end_timestamp = int(Q2_END.timestamp())
    
    start_block = get_block_by_timestamp(w3, start_timestamp)
    end_block = get_block_by_timestamp(w3, end_timestamp)
    
    logger.info(f"Analyzing blocks {start_block} to {end_block}")
    
    # Fetch events
    events = fetch_uniswap_v2_events(w3, pool_info['pool_address'], start_block, end_block, dao_address)
    
    # Group events by week
    weekly_data = []
    current_week_start = Q2_START
    
    while current_week_start <= Q2_END:
        week_end = current_week_start + timedelta(days=7)
        if week_end > Q2_END:
            week_end = Q2_END
            
        week_start_ts = int(current_week_start.timestamp())
        week_end_ts = int(week_end.timestamp())
        
        # Filter events for this week
        week_events = [e for e in events if week_start_ts <= e['timestamp'] <= week_end_ts]
        
        mint_count = len([e for e in week_events if e['type'] == 'mint'])
        burn_count = len([e for e in week_events if e['type'] == 'burn'])
        net_change = mint_count - burn_count
        
        weekly_data.append({
            'chain_name': chain_name,
            'pool_name': pool_info['pool_name'],
            'pool_address': pool_info['pool_address'],
            'week_start': current_week_start.strftime('%Y-%m-%d'),
            'week_end': (week_end - timedelta(seconds=1)).strftime('%Y-%m-%d'),
            'adds': mint_count,
            'removes': burn_count,
            'net_change': net_change,
            'events': week_events
        })
        
        current_week_start = week_end
        
    return weekly_data

def get_color_for_value(value: float, max_abs_value: float) -> str:
    """Get color based on value (green for positive, red for negative)"""
    if value == 0:
        return Style.RESET_ALL
    
    intensity = min(abs(value) / max_abs_value, 1.0) if max_abs_value > 0 else 0
    
    if value > 0:
        # Green gradient for additions
        if intensity < 0.3:
            return Fore.GREEN
        elif intensity < 0.7:
            return Fore.GREEN + Style.BRIGHT
        else:
            return Back.GREEN + Fore.WHITE + Style.BRIGHT
    else:
        # Red gradient for removals
        if intensity < 0.3:
            return Fore.RED
        elif intensity < 0.7:
            return Fore.RED + Style.BRIGHT
        else:
            return Back.RED + Fore.WHITE + Style.BRIGHT

def create_color_table(weekly_results: List[Dict]) -> None:
    """Create a color-coded table showing weekly net changes"""
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(weekly_results)
    
    if df.empty:
        print("\n" + "="*100)
        print("WEEKLY DAO NET LIQUIDITY CHANGES - Q2 2025")
        print("(Green = Additions, Red = Removals)")
        print("="*100)
        print("\nNo DAO liquidity events found for Q2 2025 (April-June 2025)")
        print("This is expected as we are currently in July 2025.")
        print("\nSUMMARY:")
        print("- Total Additions:      0")
        print("- Total Removals:       0") 
        print("- Net Change:           0")
        print("\nNote: The DAO may not have made any liquidity changes during Q2 2025")
        print("or the events may not be accessible through the current RPC endpoints.")
        return
    
    # Get unique weeks across all pools
    weeks = sorted(df['week_start'].unique())
    pools = df[['chain_name', 'pool_name']].drop_duplicates()
    
    # Create pivot table
    pivot_data = []
    for _, pool in pools.iterrows():
        pool_data = df[(df['chain_name'] == pool['chain_name']) & 
                      (df['pool_name'] == pool['pool_name'])]
        
        row = [f"{pool['chain_name']}/{pool['pool_name']}"]
        for week in weeks:
            week_data = pool_data[pool_data['week_start'] == week]
            if not week_data.empty:
                net_change = week_data.iloc[0]['net_change']
                row.append(net_change)
            else:
                row.append(0)
        pivot_data.append(row)
    
    # Calculate max absolute value for color intensity
    all_values = [val for row in pivot_data for val in row[1:] if isinstance(val, (int, float))]
    max_abs_value = max(abs(val) for val in all_values) if all_values else 1
    
    print("\n" + "="*100)
    print("WEEKLY DAO NET LIQUIDITY CHANGES - Q2 2025")
    print("(Green = Additions, Red = Removals)")
    print("="*100)
    
    # Header
    header = ["Pool"] + [f"Week {i+1}\n({week})" for i, week in enumerate(weeks)]
    print(f"{'Pool':<25}", end="")
    for i, week in enumerate(weeks):
        print(f"{'Week ' + str(i+1):<12}", end="")
    print()
    
    print(f"{'='*25}", end="")
    for _ in weeks:
        print(f"{'='*12}", end="")
    print()
    
    # Data rows
    for row in pivot_data:
        pool_name = row[0][:24]  # Truncate long names
        print(f"{pool_name:<25}", end="")
        
        for val in row[1:]:
            color = get_color_for_value(val, max_abs_value)
            if val == 0:
                display_val = "    0"
            elif val > 0:
                display_val = f"  +{val:>2}"
            else:
                display_val = f"  {val:>3}"
            print(f"{color}{display_val:<12}{Style.RESET_ALL}", end="")
        print()
    
    # Summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    
    total_adds = df['adds'].sum()
    total_removes = df['removes'].sum()
    total_net = df['net_change'].sum()
    
    print(f"Total Additions:  {Fore.GREEN}{total_adds:>6}{Style.RESET_ALL}")
    print(f"Total Removals:   {Fore.RED}{total_removes:>6}{Style.RESET_ALL}")
    print(f"Net Change:       {get_color_for_value(total_net, max_abs_value)}{total_net:>6}{Style.RESET_ALL}")
    
    # Weekly totals
    print(f"\nWeekly Net Changes:")
    for i, week in enumerate(weeks):
        week_total = sum(row[i+1] for row in pivot_data if isinstance(row[i+1], (int, float)))
        color = get_color_for_value(week_total, max_abs_value)
        print(f"  Week {i+1} ({week}): {color}{week_total:>3}{Style.RESET_ALL}")

def save_results_to_db(weekly_results: List[Dict]) -> None:
    """Save weekly results to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_dao_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_name TEXT,
            pool_name TEXT,
            pool_address TEXT,
            week_start TEXT,
            week_end TEXT,
            adds INTEGER,
            removes INTEGER,
            net_change INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Clear existing data for Q2 2025
    cursor.execute('''
        DELETE FROM weekly_dao_activity 
        WHERE week_start >= '2025-04-01' AND week_end <= '2025-06-30'
    ''')
    
    # Insert new data
    for result in weekly_results:
        cursor.execute('''
            INSERT INTO weekly_dao_activity 
            (chain_name, pool_name, pool_address, week_start, week_end, adds, removes, net_change)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result['chain_name'],
            result['pool_name'],
            result['pool_address'],
            result['week_start'],
            result['week_end'],
            result['adds'],
            result['removes'],
            result['net_change']
        ))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(weekly_results)} weekly activity records to database")

def main():
    """Main analysis function"""
    logger.info("Starting Weekly DAO FOX Pool Activity Analysis for Q2 2025")
    
    all_weekly_results = []
    
    for pool in FOX_POOLS:
        chain_name = pool['chain_name']
        dao_address = DAO_TREASURY_ADDRESSES.get(chain_name)
        
        if not dao_address:
            logger.warning(f"No DAO address found for {chain_name}")
            continue
        
        try:
            weekly_data = analyze_weekly_activity(chain_name, pool, dao_address)
            all_weekly_results.extend(weekly_data)
            
        except Exception as e:
            logger.error(f"Error analyzing {pool['pool_name']} on {chain_name}: {e}")
            continue
    
    if all_weekly_results:
        # Display color-coded table
        create_color_table(all_weekly_results)
        
        # Save to database
        save_results_to_db(all_weekly_results)
        
        logger.info("Weekly analysis complete!")
    else:
        logger.warning("No weekly data collected")

if __name__ == "__main__":
    main() 