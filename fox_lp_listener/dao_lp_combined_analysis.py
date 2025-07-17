#!/usr/bin/env python3
"""
Combined DAO and LP Analysis System
Integrates DAO treasury position tracking with comprehensive LP event monitoring.
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
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
from colorama import init, Fore, Back, Style
from eth_abi import decode

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
DAO_DB_PATH = 'fox_pools_analysis.db'
LP_DB_PATH = 'shapeshift_lp_positions.db'

# DAO Treasury Addresses
DAO_TREASURY_ADDRESSES = {
    'ethereum': Web3.to_checksum_address('0x90a48d5cf7343b08da12e067680b4c6dbfe551be'),
    'arbitrum': Web3.to_checksum_address('0x38276553f8fbf2a027d901f8be45f00373d8dd48'),
    'optimism': Web3.to_checksum_address('0x6268d07327f4fb7380732dc6d63d95f88c0e083b'),
}

# RPC endpoints
RPC_ENDPOINTS = {
    'ethereum': 'https://eth.llamarpc.com',
    'arbitrum': 'https://arb1.arbitrum.io/rpc',
    'optimism': 'https://mainnet.optimism.io'
}

# FOX pools to analyze
FOX_POOLS = [
    {
        'chain_name': 'ethereum',
        'pool_address': Web3.to_checksum_address('0x470e8de2ebaef52014a47cb5e6af86884947f08c'),
        'pool_name': 'WETH/FOX V2',
        'type': 'uniswap_v2',
        'rpc': 'https://eth.llamarpc.com'
    },
    {
        'chain_name': 'arbitrum',
        'pool_address': Web3.to_checksum_address('0x5f6ce0ca13b87bd738519545d3e018e70e339c24'),
        'pool_name': 'WETH/FOX V2',
        'type': 'uniswap_v2',
        'rpc': 'https://arb1.arbitrum.io/rpc'
    },
    {
        'chain_name': 'arbitrum',
        'pool_address': Web3.to_checksum_address('0x76d4d1eaa0c4b3645e75c46e573c1d4f75e9041e'),
        'pool_name': 'WETH/FOX V3',
        'type': 'uniswap_v3',
        'rpc': 'https://arb1.arbitrum.io/rpc'
    },
]

# LP tracking contract configurations
LP_CONTRACTS = {
    1: {  # Ethereum
        'uniswap_v3_pools': [
            ('0x470e8de2eBaef52014A47Cb5E6aF86884947F08c', 'WETH/FOX LP Pool'),
            ('0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640', 'WETH/USDC V3'),
            ('0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36', 'WETH/USDT V3'),
        ]
    }
}

# Event signatures for Uniswap V3 LP events
LP_EVENT_SIGNATURES = {
    'increase_liquidity': '0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f',
    'decrease_liquidity': '0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4',
    'collect': '0x40d0efd1a53d60ecbf40971b9d9e18502887ace780a0564668d6d65605f3c5de'
}

# Uniswap V3 NFT Position Manager
UNIV3_NFT_MANAGER = Web3.to_checksum_address('0xC36442b4a4522E871399CD717aBDD847Ab11FE88')

# Uniswap V3 NFT ABI fragments
UNIV3_NFT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "index", "type": "uint256"}
        ],
        "name": "tokenOfOwnerByIndex",
        "outputs": [{"name": "tokenId", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "positions",
        "outputs": [
            {"name": "nonce", "type": "uint96"},
            {"name": "operator", "type": "address"},
            {"name": "token0", "type": "address"},
            {"name": "token1", "type": "address"},
            {"name": "fee", "type": "uint24"},
            {"name": "tickLower", "type": "int24"},
            {"name": "tickUpper", "type": "int24"},
            {"name": "liquidity", "type": "uint128"},
            {"name": "feeGrowthInside0LastX128", "type": "uint256"},
            {"name": "feeGrowthInside1LastX128", "type": "uint256"},
            {"name": "tokensOwed0", "type": "uint128"},
            {"name": "tokensOwed1", "type": "uint128"}
        ],
        "type": "function"
    }
]

UNISWAP_V2_ABI = [
    {"constant": True, "inputs": [], "name": "getReserves", "outputs": [
        {"name": "_reserve0", "type": "uint112"},
        {"name": "_reserve1", "type": "uint112"},
        {"name": "_blockTimestampLast", "type": "uint32"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "token0", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "token1", "outputs": [{"name": "", "type": "address"}], "type": "function"},
]

def setup_databases():
    """Setup both DAO and LP databases"""
    # Setup DAO database
    conn = sqlite3.connect(DAO_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dao_position_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_name TEXT,
            pool_name TEXT,
            pool_address TEXT,
            dao_address TEXT,
            dao_balance REAL,
            dao_lp_balance REAL,
            total_lp_supply REAL,
            ownership_percentage REAL,
            token0_amt REAL,
            token1_amt REAL,
            token0_price REAL,
            token1_price REAL,
            fox_amt REAL,
            weth_amt REAL,
            fox_price REAL,
            weth_price REAL,
            dao_usd_value REAL,
            timestamp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Setup LP database
    conn = sqlite3.connect(LP_DB_PATH)
    cursor = conn.cursor()
    
    # Uniswap V3 IncreaseLiquidity events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS increase_liquidity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER,
            pool_address TEXT,
            pool_name TEXT,
            block_number INTEGER,
            tx_hash TEXT,
            log_index INTEGER,
            owner TEXT,
            tick_lower INTEGER,
            tick_upper INTEGER,
            amount TEXT,
            amount0 TEXT,
            amount1 TEXT,
            timestamp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Uniswap V3 DecreaseLiquidity events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decrease_liquidity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER,
            pool_address TEXT,
            pool_name TEXT,
            block_number INTEGER,
            tx_hash TEXT,
            log_index INTEGER,
            owner TEXT,
            tick_lower INTEGER,
            tick_upper INTEGER,
            amount TEXT,
            amount0 TEXT,
            amount1 TEXT,
            timestamp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Combined analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dao_lp_combined_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_date TEXT,
            dao_total_value REAL,
            dao_ethereum_value REAL,
            dao_arbitrum_value REAL,
            lp_total_events INTEGER,
            lp_add_events INTEGER,
            lp_remove_events INTEGER,
            dao_net_change REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info("Both databases setup complete")

def get_web3_connection(rpc_url: str) -> Web3:
    """Get Web3 connection"""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if 'arbitrum' in rpc_url or 'polygon' in rpc_url:
            w3.middleware_onion.add(ExtraDataToPOAMiddleware)
        w3.eth.block_number  # Test connection
        logger.info(f"Connected to {rpc_url}")
        return w3
    except Exception as e:
        logger.error(f"Failed to connect to {rpc_url}: {e}")
        raise

def get_token_balance(w3: Web3, token_address: str, wallet_address: str) -> float:
    """Get token balance for a wallet using ERC20 ABI"""
    try:
        erc20_abi = [{
            "constant": True,
            "inputs": [{"name": "owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }]
        contract = w3.eth.contract(address=token_address, abi=erc20_abi)
        balance = contract.functions.balanceOf(wallet_address).call()
        return balance / 1e18
    except Exception as e:
        logger.error(f"Error getting balance for {wallet_address} on {token_address}: {e}")
        return 0

def get_token_price_coingecko(token_address: str, chain: str) -> float:
    """Fetch token price in USD from Coingecko"""
    coingecko_chain = {
        'ethereum': 'ethereum',
        'arbitrum': 'arbitrum-one',
        'optimism': 'optimism',
        'polygon': 'polygon-pos',
        'gnosis': 'xdai',
    }.get(chain, 'ethereum')
    url = f"https://api.coingecko.com/api/v3/simple/token_price/{coingecko_chain}?contract_addresses={token_address}&vs_currencies=usd"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return 0.0
        price_info = list(data.values())[0]
        if 'usd' in price_info:
            return price_info['usd']
        else:
            return 0.0
    except Exception as e:
        logger.error(f"Error fetching price for {token_address}: {e}")
        return 0.0

def get_current_dao_positions() -> List[Dict]:
    """Get current DAO positions across all pools"""
    results = []
    
    logger.info("Fetching current DAO positions...")
    
    for pool in FOX_POOLS:
        chain_name = pool['chain_name']
        pool_address = pool['pool_address']
        pool_name = pool['pool_name']
        pool_type = pool['type']
        
        dao_address = DAO_TREASURY_ADDRESSES.get(chain_name)
        if not dao_address:
            logger.warning(f"No DAO treasury address found for {chain_name}")
            continue
            
        try:
            w3 = get_web3_connection(pool['rpc'])
            
            if pool_type == 'uniswap_v2':
                contract = w3.eth.contract(address=pool_address, abi=UNISWAP_V2_ABI)
                lp_balance = get_token_balance(w3, pool_address, dao_address)
                total_supply = contract.functions.totalSupply().call() / 1e18
                reserves = contract.functions.getReserves().call()
                token0 = contract.functions.token0().call()
                token1 = contract.functions.token1().call()
                
                # Get prices
                price0 = get_token_price_coingecko(token0, chain_name)
                price1 = get_token_price_coingecko(token1, chain_name)
                
                # DAO share
                share = lp_balance / total_supply if total_supply > 0 else 0
                amt0 = reserves[0] / 1e18 * share
                amt1 = reserves[1] / 1e18 * share
                usd_value = amt0 * price0 + amt1 * price1
                
                results.append({
                    'chain_name': chain_name,
                    'pool_name': pool_name,
                    'pool_address': pool_address,
                    'dao_address': dao_address,
                    'dao_lp_balance': lp_balance,
                    'total_lp_supply': total_supply,
                    'ownership_percentage': share * 100,
                    'token0_amt': amt0,
                    'token1_amt': amt1,
                    'token0_price': price0,
                    'token1_price': price1,
                    'dao_usd_value': usd_value,
                    'timestamp': datetime.now().isoformat()
                })
                
            elif pool_type == 'uniswap_v3':
                nft = w3.eth.contract(address=UNIV3_NFT_MANAGER, abi=UNIV3_NFT_ABI)
                balance = nft.functions.balanceOf(dao_address).call()
                total_fox = 0
                total_weth = 0
                
                for i in range(balance):
                    try:
                        token_id = nft.functions.tokenOfOwnerByIndex(dao_address, i).call()
                        pos = nft.functions.positions(token_id).call()
                        
                        # For simplicity, treat liquidity as split 50/50
                        fox_amt = pos[7] / 2 / 1e18
                        weth_amt = pos[7] / 2 / 1e18
                        total_fox += fox_amt
                        total_weth += weth_amt
                    except Exception as e:
                        logger.debug(f"Error processing V3 position {i}: {e}")
                        continue
                
                price0 = get_token_price_coingecko('0xc770EEfAd204B5180dF6a14Ee197D99d808ee52d', chain_name)  # FOX
                price1 = get_token_price_coingecko('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', chain_name)  # WETH
                usd_value = total_fox * price0 + total_weth * price1
                
                results.append({
                    'chain_name': chain_name,
                    'pool_name': pool_name,
                    'pool_address': pool_address,
                    'dao_address': dao_address,
                    'dao_balance': balance,
                    'fox_amt': total_fox,
                    'weth_amt': total_weth,
                    'fox_price': price0,
                    'weth_price': price1,
                    'dao_usd_value': usd_value,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error analyzing {pool_name} on {chain_name}: {e}")
            continue
    
    return results

def fetch_lp_events(chain_id: int, start_block: int, end_block: int) -> Dict:
    """Fetch LP events for the specified period"""
    w3 = get_web3_connection(RPC_ENDPOINTS['ethereum'])  # Use Ethereum for now
    
    conn = sqlite3.connect(LP_DB_PATH)
    cursor = conn.cursor()
    
    total_add_events = 0
    total_remove_events = 0
    
    for pool_address, pool_name in LP_CONTRACTS[chain_id].get('uniswap_v3_pools', []):
        logger.info(f"Fetching LP events for {pool_name}")
        
        try:
            # Fetch IncreaseLiquidity events
            increase_logs = w3.eth.get_logs({
                'address': pool_address,
                'topics': [LP_EVENT_SIGNATURES['increase_liquidity']],
                'fromBlock': start_block,
                'toBlock': end_block
            })
            
            for log in increase_logs:
                cursor.execute('''
                    INSERT INTO increase_liquidity_events 
                    (chain_id, pool_address, pool_name, block_number, tx_hash, log_index,
                     owner, tick_lower, tick_upper, amount, amount0, amount1, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    chain_id, pool_address, pool_name, log['blockNumber'], log['transactionHash'].hex(),
                    log['logIndex'], '0x' + log['topics'][1][-40:].hex(), 0, 0, '0', '0', '0', int(time.time())
                ))
                total_add_events += 1
            
            # Fetch DecreaseLiquidity events
            decrease_logs = w3.eth.get_logs({
                'address': pool_address,
                'topics': [LP_EVENT_SIGNATURES['decrease_liquidity']],
                'fromBlock': start_block,
                'toBlock': end_block
            })
            
            for log in decrease_logs:
                cursor.execute('''
                    INSERT INTO decrease_liquidity_events 
                    (chain_id, pool_address, pool_name, block_number, tx_hash, log_index,
                     owner, tick_lower, tick_upper, amount, amount0, amount1, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    chain_id, pool_address, pool_name, log['blockNumber'], log['transactionHash'].hex(),
                    log['logIndex'], '0x' + log['topics'][1][-40:].hex(), 0, 0, '0', '0', '0', int(time.time())
                ))
                total_remove_events += 1
                
        except Exception as e:
            logger.error(f"Error fetching events for {pool_name}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    return {
        'total_add_events': total_add_events,
        'total_remove_events': total_remove_events,
        'total_events': total_add_events + total_remove_events
    }

def save_dao_positions_to_db(positions: List[Dict]) -> None:
    """Save DAO positions to database"""
    conn = sqlite3.connect(DAO_DB_PATH)
    cursor = conn.cursor()
    
    for pos in positions:
        cursor.execute('''
            INSERT INTO dao_position_history 
            (chain_name, pool_name, pool_address, dao_address, dao_balance, dao_lp_balance, 
             total_lp_supply, ownership_percentage, token0_amt, token1_amt, token0_price, 
             token1_price, fox_amt, weth_amt, fox_price, weth_price, dao_usd_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pos.get('chain_name'),
            pos.get('pool_name'),
            pos.get('pool_address'),
            pos.get('dao_address'),
            pos.get('dao_balance', 0),
            pos.get('dao_lp_balance', 0),
            pos.get('total_lp_supply', 0),
            pos.get('ownership_percentage', 0),
            pos.get('token0_amt', 0),
            pos.get('token1_amt', 0),
            pos.get('token0_price', 0),
            pos.get('token1_price', 0),
            pos.get('fox_amt', 0),
            pos.get('weth_amt', 0),
            pos.get('fox_price', 0),
            pos.get('weth_price', 0),
            pos.get('dao_usd_value', 0),
            pos.get('timestamp')
        ))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(positions)} DAO position records to database")

def save_combined_analysis(dao_positions: List[Dict], lp_events: Dict) -> None:
    """Save combined analysis to database"""
    conn = sqlite3.connect(LP_DB_PATH)
    cursor = conn.cursor()
    
    # Calculate totals
    dao_total_value = sum(pos['dao_usd_value'] for pos in dao_positions)
    dao_ethereum_value = sum(pos['dao_usd_value'] for pos in dao_positions if pos['chain_name'] == 'ethereum')
    dao_arbitrum_value = sum(pos['dao_usd_value'] for pos in dao_positions if pos['chain_name'] == 'arbitrum')
    
    # Get previous DAO value for change calculation
    cursor.execute('''
        SELECT dao_total_value FROM dao_lp_combined_analysis 
        ORDER BY created_at DESC LIMIT 1
    ''')
    result = cursor.fetchone()
    previous_dao_value = result[0] if result else dao_total_value
    dao_net_change = dao_total_value - previous_dao_value
    
    cursor.execute('''
        INSERT INTO dao_lp_combined_analysis 
        (analysis_date, dao_total_value, dao_ethereum_value, dao_arbitrum_value,
         lp_total_events, lp_add_events, lp_remove_events, dao_net_change)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        dao_total_value,
        dao_ethereum_value,
        dao_arbitrum_value,
        lp_events['total_events'],
        lp_events['total_add_events'],
        lp_events['total_remove_events'],
        dao_net_change
    ))
    
    conn.commit()
    conn.close()
    logger.info("Saved combined analysis to database")

def display_combined_analysis(dao_positions: List[Dict], lp_events: Dict):
    """Display combined analysis with color coding"""
    
    print("\n" + "="*120)
    print("COMBINED DAO & LP ANALYSIS")
    print("="*120)
    
    # DAO Positions Summary
    print("\n📊 DAO TREASURY POSITIONS:")
    print("="*60)
    
    total_dao_value = sum(pos['dao_usd_value'] for pos in dao_positions)
    print(f"Total DAO Value: ${total_dao_value:,.2f}")
    
    for pos in dao_positions:
        pool_name = f"{pos['chain_name']}/{pos['pool_name']}"
        usd_value = pos['dao_usd_value']
        lp_balance = pos.get('dao_lp_balance', 0)
        ownership = pos.get('ownership_percentage', 0)
        
        if lp_balance > 0:
            print(f"  {pool_name}: ${usd_value:,.2f} (LP: {lp_balance:,.4f}, Share: {ownership:.2f}%)")
        else:
            print(f"  {pool_name}: ${usd_value:,.2f}")
    
    # LP Activity Summary
    print(f"\n🔄 LP ACTIVITY (Last 24 hours):")
    print("="*60)
    
    add_color = Fore.GREEN if lp_events['total_add_events'] > 0 else Style.RESET_ALL
    remove_color = Fore.RED if lp_events['total_remove_events'] > 0 else Style.RESET_ALL
    
    print(f"Total LP Events: {lp_events['total_events']}")
    print(f"Add Events:      {add_color}{lp_events['total_add_events']}{Style.RESET_ALL}")
    print(f"Remove Events:   {remove_color}{lp_events['total_remove_events']}{Style.RESET_ALL}")
    
    # Combined Insights
    print(f"\n💡 COMBINED INSIGHTS:")
    print("="*60)
    
    if lp_events['total_add_events'] > lp_events['total_remove_events']:
        print(f"• LP activity shows net additions (more adds than removes)")
    elif lp_events['total_remove_events'] > lp_events['total_add_events']:
        print(f"• LP activity shows net removals (more removes than adds)")
    else:
        print(f"• LP activity is balanced (equal adds and removes)")
    
    if total_dao_value > 1000000:
        print(f"• DAO maintains significant liquidity positions (>$1M)")
    else:
        print(f"• DAO has moderate liquidity positions")
    
    print(f"• Monitoring {len(dao_positions)} FOX pools across multiple chains")

def main():
    """Main combined analysis function"""
    logger.info("Starting Combined DAO & LP Analysis")
    
    # Setup databases
    setup_databases()
    
    # Get current DAO positions
    dao_positions = get_current_dao_positions()
    
    if dao_positions:
        # Save DAO positions
        save_dao_positions_to_db(dao_positions)
        
        # Get LP events for last 24 hours
        w3 = get_web3_connection(RPC_ENDPOINTS['ethereum'])
        current_block = w3.eth.block_number
        blocks_per_day = 7200  # Ethereum blocks per day
        start_block = current_block - blocks_per_day
        
        lp_events = fetch_lp_events(1, start_block, current_block)
        
        # Save combined analysis
        save_combined_analysis(dao_positions, lp_events)
        
        # Display results
        display_combined_analysis(dao_positions, lp_events)
        
        logger.info("Combined analysis complete!")
    else:
        logger.warning("No DAO positions found")

if __name__ == "__main__":
    main() 