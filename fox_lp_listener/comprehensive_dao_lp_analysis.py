#!/usr/bin/env python3
"""
Comprehensive DAO & LP Analysis System
Combines DAO treasury tracking with LP event monitoring for complete FOX pool analysis.
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
    """Setup databases for analysis"""
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
    
    # Combined analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comprehensive_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_date TEXT,
            dao_total_value REAL,
            dao_ethereum_value REAL,
            dao_arbitrum_value REAL,
            dao_position_count INTEGER,
            lp_activity_score INTEGER,
            market_health_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Databases setup complete")

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

def save_comprehensive_analysis(dao_positions: List[Dict]) -> None:
    """Save comprehensive analysis to database"""
    conn = sqlite3.connect(DAO_DB_PATH)
    cursor = conn.cursor()
    
    # Calculate metrics
    dao_total_value = sum(pos['dao_usd_value'] for pos in dao_positions)
    dao_ethereum_value = sum(pos['dao_usd_value'] for pos in dao_positions if pos['chain_name'] == 'ethereum')
    dao_arbitrum_value = sum(pos['dao_usd_value'] for pos in dao_positions if pos['chain_name'] == 'arbitrum')
    dao_position_count = len(dao_positions)
    
    # Calculate health scores
    lp_activity_score = min(100, dao_position_count * 20)  # Based on number of active positions
    market_health_score = min(100, (dao_total_value / 1000000) * 50)  # Based on total value
    
    cursor.execute('''
        INSERT INTO comprehensive_analysis 
        (analysis_date, dao_total_value, dao_ethereum_value, dao_arbitrum_value,
         dao_position_count, lp_activity_score, market_health_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        dao_total_value,
        dao_ethereum_value,
        dao_arbitrum_value,
        dao_position_count,
        lp_activity_score,
        market_health_score
    ))
    
    conn.commit()
    conn.close()
    logger.info("Saved comprehensive analysis to database")

def get_color_for_value(value: float, max_abs_value: float) -> str:
    """Get color based on value"""
    if value == 0:
        return Style.RESET_ALL
    
    intensity = min(abs(value) / max_abs_value, 1.0) if max_abs_value > 0 else 0
    
    if value > 0:
        if intensity < 0.3:
            return Fore.GREEN
        elif intensity < 0.7:
            return Fore.GREEN + Style.BRIGHT
        else:
            return Back.GREEN + Fore.WHITE + Style.BRIGHT
    else:
        if intensity < 0.3:
            return Fore.RED
        elif intensity < 0.7:
            return Fore.RED + Style.BRIGHT
        else:
            return Back.RED + Fore.WHITE + Style.BRIGHT

def display_comprehensive_analysis(dao_positions: List[Dict]):
    """Display comprehensive analysis with color coding"""
    
    print("\n" + "="*120)
    print("COMPREHENSIVE DAO & LP ANALYSIS")
    print("="*120)
    
    # DAO Positions Summary
    print("\n📊 DAO TREASURY POSITIONS:")
    print("="*60)
    
    total_dao_value = sum(pos['dao_usd_value'] for pos in dao_positions)
    print(f"Total DAO Value: ${total_dao_value:,.2f}")
    
    # Calculate max value for color intensity
    max_value = max(pos['dao_usd_value'] for pos in dao_positions) if dao_positions else 1
    
    for pos in dao_positions:
        pool_name = f"{pos['chain_name']}/{pos['pool_name']}"
        usd_value = pos['dao_usd_value']
        lp_balance = pos.get('dao_lp_balance', 0)
        ownership = pos.get('ownership_percentage', 0)
        
        color = get_color_for_value(usd_value, max_value)
        
        if lp_balance > 0:
            print(f"  {pool_name}: {color}${usd_value:,.2f}{Style.RESET_ALL} (LP: {lp_balance:,.4f}, Share: {ownership:.2f}%)")
        else:
            print(f"  {pool_name}: {color}${usd_value:,.2f}{Style.RESET_ALL}")
    
    # Chain Breakdown
    print(f"\n🌐 CHAIN BREAKDOWN:")
    print("="*60)
    
    chain_totals = {}
    for pos in dao_positions:
        chain = pos['chain_name']
        if chain not in chain_totals:
            chain_totals[chain] = 0
        chain_totals[chain] += pos['dao_usd_value']
    
    for chain, value in chain_totals.items():
        color = get_color_for_value(value, max_value)
        print(f"  {chain.capitalize()}: {color}${value:,.2f}{Style.RESET_ALL}")
    
    # Health Metrics
    print(f"\n💡 HEALTH METRICS:")
    print("="*60)
    
    dao_position_count = len(dao_positions)
    lp_activity_score = min(100, dao_position_count * 20)
    market_health_score = min(100, (total_dao_value / 1000000) * 50)
    
    # Color code health scores
    if lp_activity_score >= 80:
        activity_color = Fore.GREEN + Style.BRIGHT
    elif lp_activity_score >= 50:
        activity_color = Fore.YELLOW
    else:
        activity_color = Fore.RED
    
    if market_health_score >= 80:
        health_color = Fore.GREEN + Style.BRIGHT
    elif market_health_score >= 50:
        health_color = Fore.YELLOW
    else:
        health_color = Fore.RED
    
    print(f"  LP Activity Score:    {activity_color}{lp_activity_score:>3}/100{Style.RESET_ALL}")
    print(f"  Market Health Score:  {health_color}{market_health_score:>3}/100{Style.RESET_ALL}")
    print(f"  Active Positions:     {dao_position_count}")
    
    # Insights
    print(f"\n🔍 INSIGHTS:")
    print("="*60)
    
    if total_dao_value > 2000000:
        print("• DAO maintains very strong liquidity positions (>$2M)")
    elif total_dao_value > 1000000:
        print("• DAO maintains strong liquidity positions (>$1M)")
    else:
        print("• DAO has moderate liquidity positions")
    
    if dao_position_count >= 3:
        print("• DAO is well diversified across multiple pools")
    elif dao_position_count >= 2:
        print("• DAO has moderate diversification")
    else:
        print("• DAO has limited diversification")
    
    if lp_activity_score >= 80:
        print("• High LP activity indicates active treasury management")
    elif lp_activity_score >= 50:
        print("• Moderate LP activity shows steady treasury operations")
    else:
        print("• Low LP activity suggests conservative treasury approach")
    
    if market_health_score >= 80:
        print("• Excellent market health with strong liquidity depth")
    elif market_health_score >= 50:
        print("• Good market health with adequate liquidity")
    else:
        print("• Market health could be improved with more liquidity")

def main():
    """Main comprehensive analysis function"""
    logger.info("Starting Comprehensive DAO & LP Analysis")
    
    # Setup databases
    setup_databases()
    
    # Get current DAO positions
    dao_positions = get_current_dao_positions()
    
    if dao_positions:
        # Save DAO positions
        save_dao_positions_to_db(dao_positions)
        
        # Save comprehensive analysis
        save_comprehensive_analysis(dao_positions)
        
        # Display results
        display_comprehensive_analysis(dao_positions)
        
        logger.info("Comprehensive analysis complete!")
    else:
        logger.warning("No DAO positions found")

if __name__ == "__main__":
    main() 