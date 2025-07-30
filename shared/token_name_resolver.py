#!/usr/bin/env python3
"""
Token Name Resolver
Resolves token addresses to human-readable names and symbols.
"""

import os
import sqlite3
import requests
import time
from typing import Dict, List, Optional
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class TokenNameResolver:
    def __init__(self):
        self.alchemy_api_key = os.getenv('ALCHEMY_API_KEY')
        self.infura_api_key = os.getenv('INFURA_API_KEY')
        
        # Initialize Web3
        if self.alchemy_api_key:
            self.w3 = Web3(Web3.HTTPProvider(f'https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}'))
        elif self.infura_api_key:
            self.w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{self.infura_api_key}'))
        else:
            self.w3 = None
        
        # Common token addresses and their names
        self.common_tokens = {
            # Native tokens
            '0x0000000000000000000000000000000000000000': 'ETH',
            '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee': 'ETH',
            
            # Major tokens
            '0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8': 'USDC',
            '0xdAC17F958D2ee523a2206206994597C13D831ec7': 'USDT',
            '0x6B175474E89094C44Da98b954EedeAC495271d0F': 'DAI',
            '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 'WBTC',
            '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 'WETH',
            '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1': 'WETH',  # Arbitrum
            '0x4200000000000000000000000000000000000006': 'WETH',  # Base
            '0x98f7A83361F7Ac8765CcEBAB1425da6d3414a40': 'WETH',  # Polygon
            
            # FOX token
            '0xc770EEfAd204B5180dF6a14Ee197D99d808ee52d': 'FOX',
            '0xc770eefad204b5180df6a14ee197d99d808ee52d': 'FOX',
            
            # Common stablecoins
            '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913': 'USDC',  # Base
            '0xaf88d065e77c8cC2239327C5EDb3A432268e5831': 'USDC',  # Arbitrum
            '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174': 'USDC',  # Polygon
            '0x176211869cA2b568f2A7D4EE941E073a821EE1ff': 'USDC',  # Base
            
            # Other common tokens
            '0x6985884C4392D348587B19cb9eAAf157F13271cd': 'USDT',  # Base
            '0x912CE59144191C1204E64559FE8253a0e49E6548': 'ARB',   # Arbitrum
            '0x3D01Fe5A38ddBD307fDd635b4Cb0e29681226D6f': 'USDT',  # Base
            '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb': 'USDC',  # Base
            '0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b': 'USDT',  # Base
            '0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34': 'USDC',  # Base
            '0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2': 'USDT',  # Base
            '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf': 'USDC',  # Base
            '0x940181a94A35A4569E4529A3CDfB74e38FD98631': 'USDC',  # Base
            '0x1111111111166b7FE7bd91427724B487980aFc69': '1INCH', # Base
        }
        
        # Cache for token lookups
        self.token_cache = {}
    
    def get_token_name(self, address: str, chain: str = 'ethereum') -> str:
        """Get token name/symbol for a given address"""
        if not address or address == '0x0000000000000000000000000000000000000000':
            return 'ETH' if chain != 'ethereum' else 'ETH'
        
        # Check cache first
        cache_key = f"{address.lower()}_{chain}"
        if cache_key in self.token_cache:
            return self.token_cache[cache_key]
        
        # Check common tokens
        if address in self.common_tokens:
            self.token_cache[cache_key] = self.common_tokens[address]
            return self.common_tokens[address]
        
        # Try to get from blockchain
        token_name = self._get_token_from_blockchain(address, chain)
        if token_name:
            self.token_cache[cache_key] = token_name
            return token_name
        
        # Fallback to address
        return address[:10] + '...'
    
    def _get_token_from_blockchain(self, address: str, chain: str) -> Optional[str]:
        """Get token info from blockchain"""
        if not self.w3:
            return None
        
        try:
            # ERC-20 token interface
            token_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "name",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                }
            ]
            
            contract = self.w3.eth.contract(address=address, abi=token_abi)
            
            # Try to get symbol first
            try:
                symbol = contract.functions.symbol().call()
                if symbol:
                    return symbol
            except:
                pass
            
            # Try to get name
            try:
                name = contract.functions.name().call()
                if name:
                    return name
            except:
                pass
            
        except Exception as e:
            print(f"Error getting token info for {address}: {e}")
        
        return None
    
    def add_token_name_columns(self, db_path: str, table_name: str, token_columns: List[str]):
        """Add token name columns to a database table"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add token name columns for each token column
            for token_col in token_columns:
                name_col = f"{token_col}_name"
                if name_col not in columns:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {name_col} TEXT")
                    print(f"Added column {name_col} to {table_name}")
            
            conn.commit()
            conn.close()
            print(f"✅ Added token name columns to {db_path}")
            
        except Exception as e:
            print(f"Error adding token name columns to {db_path}: {e}")
    
    def populate_token_names(self, db_path: str, table_name: str, token_columns: List[str], chain_column: str = 'chain'):
        """Populate token name columns with resolved names"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if chain column exists
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            if chain_column not in columns:
                # For tables without chain column (like THORChain), use a default chain
                print(f"No {chain_column} column found in {table_name}, using default chain")
                chain_column = None
            
            # Get all unique token addresses
            for token_col in token_columns:
                name_col = f"{token_col}_name"
                
                if chain_column:
                    # Get unique token addresses with chain
                    cursor.execute(f"SELECT DISTINCT {token_col}, {chain_column} FROM {table_name} WHERE {token_col} IS NOT NULL AND {token_col} != ''")
                    unique_tokens = cursor.fetchall()
                else:
                    # Get unique token addresses without chain
                    cursor.execute(f"SELECT DISTINCT {token_col} FROM {table_name} WHERE {token_col} IS NOT NULL AND {token_col} != ''")
                    unique_tokens = [(row[0], 'ethereum') for row in cursor.fetchall()]
                
                print(f"Found {len(unique_tokens)} unique {token_col} addresses to resolve")
                
                # Resolve each token
                for token_data in unique_tokens:
                    if chain_column:
                        token_addr, chain = token_data
                    else:
                        token_addr = token_data[0]
                        chain = 'ethereum'  # Default for THORChain
                    
                    if token_addr:
                        token_name = self.get_token_name(token_addr, chain)
                        
                        # Update all rows with this token address
                        if chain_column:
                            cursor.execute(f"""
                                UPDATE {table_name} 
                                SET {name_col} = ? 
                                WHERE {token_col} = ? AND {chain_column} = ?
                            """, (token_name, token_addr, chain))
                        else:
                            cursor.execute(f"""
                                UPDATE {table_name} 
                                SET {name_col} = ? 
                                WHERE {token_col} = ?
                            """, (token_name, token_addr))
                        
                        print(f"Resolved {token_addr} -> {token_name} on {chain}")
                
                conn.commit()
            
            conn.close()
            print(f"✅ Populated token names in {db_path}")
            
        except Exception as e:
            print(f"Error populating token names in {db_path}: {e}")

def main():
    """Main function to add token names to all databases"""
    resolver = TokenNameResolver()
    
    # Define database configurations
    db_configs = [
        {
            'path': 'databases/affiliate.db',
            'tables': [
                {
                    'name': 'relay_affiliate_fees',
                    'token_columns': ['token_address']
                },
                {
                    'name': 'relay_claiming_transactions',
                    'token_columns': ['token_address']
                }
            ]
        },
        {
            'path': 'databases/portals_transactions.db',
            'tables': [
                {
                    'name': 'portals_transactions',
                    'token_columns': ['input_token', 'output_token', 'affiliate_token']
                }
            ]
        },
        {
            'path': 'databases/cowswap_transactions.db',
            'tables': [
                {
                    'name': 'cowswap_transactions',
                    'token_columns': ['sell_token', 'buy_token']
                }
            ]
        },
        {
            'path': 'databases/thorchain_transactions.db',
            'tables': [
                {
                    'name': 'thorchain_transactions',
                    'token_columns': ['from_asset', 'to_asset']
                }
            ]
        }
    ]
    
    # Process each database
    for db_config in db_configs:
        if os.path.exists(db_config['path']):
            print(f"\nProcessing {db_config['path']}...")
            
            for table_config in db_config['tables']:
                # Add token name columns
                resolver.add_token_name_columns(
                    db_config['path'],
                    table_config['name'],
                    table_config['token_columns']
                )
                
                # Populate token names
                resolver.populate_token_names(
                    db_config['path'],
                    table_config['name'],
                    table_config['token_columns']
                )

if __name__ == "__main__":
    main() 