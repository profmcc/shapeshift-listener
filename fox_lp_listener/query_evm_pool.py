import os
import requests
from web3 import Web3
from typing import Tuple

# -------- CONFIGURATION --------
# Set these for the pool you want to query
POOL_ADDRESS = os.environ.get('POOL_ADDRESS') or '0x470e8de2ebaef52014a47cb5e6af86884947f08c'  # Example: WETH/FOX Ethereum
CHAIN = os.environ.get('CHAIN') or 'ethereum'  # ethereum, arbitrum, polygon, gnosis
RPC_URLS = {
    'ethereum': 'https://eth.llamarpc.com',
    'arbitrum': 'https://arb1.arbitrum.io/rpc',
    'polygon': 'https://polygon-rpc.com',
    'gnosis': 'https://rpc.gnosis.gateway.fm',
}

# ERC20 token addresses for FOX and WETH on each chain
FOX_ADDRESSES = {
    'ethereum': '0xc770eefad204b5180df6a14ee197d99d808ee52d',
    'arbitrum': '0xc770eefad204b5180df6a14ee197d99d808ee52d',
    'polygon': '0xc770eefad204b5180df6a14ee197d99d808ee52d',
    'gnosis': '0x21a42669643f45bc0e086b8fc2ed70c23d67509d',
}
WETH_ADDRESSES = {
    'ethereum': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'arbitrum': '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',
    'polygon': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
    'gnosis': '0x6a023ccd1ff6f2045c3309768ead9e68f978f6e1',
}

# Uniswap V2 ABI (minimal)
UNIV2_ABI = [
    {"constant": True, "inputs": [], "name": "getReserves", "outputs": [
        {"name": "_reserve0", "type": "uint112"},
        {"name": "_reserve1", "type": "uint112"},
        {"name": "_blockTimestampLast", "type": "uint32"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "token0", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "token1", "outputs": [{"name": "", "type": "address"}], "type": "function"},
]

# --------- HELPERS ---------
def get_token_price_coingecko(token_address: str, chain: str) -> float:
    coingecko_chain = {
        'ethereum': 'ethereum',
        'arbitrum': 'arbitrum-one',
        'polygon': 'polygon-pos',
        'gnosis': 'xdai',
    }[chain]
    url = f"https://api.coingecko.com/api/v3/simple/token_price/{coingecko_chain}?contract_addresses={token_address}&vs_currencies=usd"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not data:
            return 0.0
        price_info = list(data.values())[0]
        return price_info.get('usd', 0.0)
    except Exception as e:
        print(f"Error fetching price for {token_address}: {e}")
        return 0.0

def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URLS[CHAIN]))
    pool = w3.eth.contract(address=Web3.to_checksum_address(POOL_ADDRESS), abi=UNIV2_ABI)
    
    # Get tokens
    token0 = pool.functions.token0().call()
    token1 = pool.functions.token1().call()
    fox_token = Web3.to_checksum_address(FOX_ADDRESSES[CHAIN])
    # Identify which is FOX and which is the other asset
    if token0.lower() == fox_token.lower():
        fox_index, other_index = 0, 1
        other_token = token1
    else:
        fox_index, other_index = 1, 0
        other_token = token0
    
    reserves = pool.functions.getReserves().call()
    total_supply = pool.functions.totalSupply().call() / 1e18
    fox_balance = reserves[fox_index] / 1e18
    other_balance = reserves[other_index] / 1e18
    
    # Get prices
    fox_price = get_token_price_coingecko(fox_token, CHAIN)
    other_price = get_token_price_coingecko(other_token, CHAIN)
    
    # USD value
    fox_usd = fox_balance * fox_price
    other_usd = other_balance * other_price
    total_usd = fox_usd + other_usd
    
    print(f"\nPool: {POOL_ADDRESS} on {CHAIN.capitalize()}")
    print(f"FOX Balance: {fox_balance:,.2f} ($ {fox_usd:,.2f})")
    print(f"Other Asset Balance: {other_balance:,.4f} ($ {other_usd:,.2f})")
    print(f"Total USD Value: $ {total_usd:,.2f}")
    print(f"FOX Price: $ {fox_price:.4f}")
    print(f"Other Asset Price: $ {other_price:.4f}")
    print(f"Total LP Supply: {total_supply:,.2f}")

if __name__ == "__main__":
    main() 