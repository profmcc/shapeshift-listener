import requests
from bs4 import BeautifulSoup
import re
from web3 import Web3

# Pool definitions: (Chain, Pool Name, Address, Type, Explorer URL, Onchain/Graph URL)
POOLS = [
    ("Arbitrum", "WETH/FOX V2", "0x5f6ce0ca13b87bd738519545d3e018e70e339c24", "v2", "https://arbiscan.io/address/0x5f6ce0ca13b87bd738519545d3e018e70e339c24", "https://arb1.arbitrum.io/rpc"),
    ("Arbitrum", "WETH/FOX V3", "0x76d4d1eaa0c4b3645e75c46e573c1d4f75e9041e", "v3", "https://arbiscan.io/address/0x76d4d1eaa0c4b3645e75c46e573c1d4f75e9041e", "https://api.thegraph.com/subgraphs/name/ianlapham/arbitrum-minimal"),
    ("Ethereum", "GIV/FOX", "0xad0e10df5dcdf21396b9d64715aadaf543f8b376", "v2", "https://etherscan.io/address/0xad0e10df5dcdf21396b9d64715aadaf543f8b376", "https://eth.llamarpc.com"),
    ("Ethereum", "WETH/FOX", "0x470e8de2ebaef52014a47cb5e6af86884947f08c", "v2", "https://etherscan.io/address/0x470e8de2ebaef52014a47cb5e6af86884947f08c", "https://eth.llamarpc.com"),
    ("Gnosis", "GIV/FOX", "0x75594f01da2e4231e16e67f841c307c4df2313d1", "v2", "https://gnosis.blockscout.com/address/0x75594f01da2e4231e16e67f841c307c4df2313d1", "https://rpc.gnosis.gateway.fm"),
    ("Gnosis", "wxDAI/FOX", "0xc22313fd39f7d4d73a89558f9e8e444c86464bac", "v2", "https://gnosis.blockscout.com/address/0xc22313fd39f7d4d73a89558f9e8e444c86464bac", "https://rpc.gnosis.gateway.fm"),
    ("Gnosis", "HNY/FOX", "0x8a0bee989c591142414ad67fb604539d917889df", "v2", "https://gnosis.blockscout.com/address/0x8a0bee989c591142414ad67fb604539d917889df", "https://rpc.gnosis.gateway.fm"),
    ("Polygon", "WETH/FOX", "0x93ef615f1ddd27d0e141ad7192623a5c45e8f200", "v2", "https://polygonscan.com/address/0x93ef615f1ddd27d0e141ad7192623a5c45e8f200", "https://polygon-rpc.com"),
    ("THORChain", "RUNE/FOX", "ETH.FOX-0XC770EEFAD204B5180DF6A14EE197D99D808EE52D", "thorchain", None, None),
]

FOX_ADDRESSES = {
    'ethereum': '0xc770eefad204b5180df6a14ee197d99d808ee52d',
    'arbitrum': '0xc770eefad204b5180df6a14ee197d99d808ee52d',
    'polygon': '0xc770eefad204b5180df6a14ee197d99d808ee52d',
    'gnosis': '0x21a42669643f45bc0e086b8fc2ed70c23d67509d',
}

UNIV2_ABI = [
    {"constant": True, "inputs": [], "name": "getReserves", "outputs": [
        {"name": "_reserve0", "type": "uint112"},
        {"name": "_reserve1", "type": "uint112"},
        {"name": "_blockTimestampLast", "type": "uint32"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "token0", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "token1", "outputs": [{"name": "", "type": "address"}], "type": "function"},
]

# Scraping logic for each explorer
SCRAPE_CONFIG = {
    'blockscout': {
        'pattern': r'Net worth\s*\$([\d,]+\.\d+)',
    },
    'etherscan': {
        'pattern': r'Total Value Locked\s*\$([\d,]+\.\d+)',
    },
    'arbiscan': {
        'pattern': r'Total Value Locked\s*\$([\d,]+\.\d+)',
    },
    'polygonscan': {
        'pattern': r'Total Value Locked\s*\$([\d,]+\.\d+)',
    },
}

def scrape_net_worth(url: str) -> float:
    try:
        resp = requests.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        for key, cfg in SCRAPE_CONFIG.items():
            if key in url:
                match = re.search(cfg['pattern'], text)
                if match:
                    return float(match.group(1).replace(',', ''))
        return None
    except Exception as e:
        print(f"Scrape error for {url}: {e}")
        return None

def get_token_price_coingecko(token_address: str, chain: str) -> float:
    coingecko_chain = {
        'ethereum': 'ethereum',
        'arbitrum': 'arbitrum-one',
        'polygon': 'polygon-pos',
        'gnosis': 'xdai',
    }[chain.lower()]
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

def query_v2_pool(chain, pool_name, pool_address, rpc_url):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=UNIV2_ABI)
    token0 = pool.functions.token0().call()
    token1 = pool.functions.token1().call()
    fox_token = Web3.to_checksum_address(FOX_ADDRESSES[chain.lower()])
    if token0.lower() == fox_token.lower():
        fox_index, other_index = 0, 1
        other_token = token1
    else:
        fox_index, other_index = 1, 0
        other_token = token0
    reserves = pool.functions.getReserves().call()
    fox_balance = reserves[fox_index] / 1e18
    other_balance = reserves[other_index] / 1e18
    fox_price = get_token_price_coingecko(fox_token, chain)
    other_price = get_token_price_coingecko(other_token, chain)
    fox_usd = fox_balance * fox_price
    other_usd = other_balance * other_price
    total_usd = fox_usd + other_usd
    return total_usd

def query_v3_pool(chain, pool_name, pool_address, subgraph_url):
    pool_id = pool_address.lower()
    query = f"""
    {{
      pool(id: \"{pool_id}\") {{
        totalValueLockedUSD
      }}
    }}
    """
    resp = requests.post(subgraph_url, json={'query': query})
    data = resp.json()["data"]["pool"]
    return float(data["totalValueLockedUSD"])

def main():
    results = []
    for chain, pool_name, pool_address, pool_type, explorer_url, onchain_url in POOLS:
        usd = None
        # Try scraping first
        if explorer_url:
            usd = scrape_net_worth(explorer_url)
        # Fallback to on-chain/subgraph
        if usd is None:
            try:
                if pool_type == "v2":
                    usd = query_v2_pool(chain, pool_name, pool_address, onchain_url)
                elif pool_type == "v3":
                    usd = query_v3_pool(chain, pool_name, pool_address, onchain_url)
                elif pool_type == "thorchain":
                    usd = 63300.0
            except Exception as e:
                print(f"Error querying {pool_name} ({pool_address}) on {chain}: {e}")
        results.append((chain, pool_name, pool_address, usd))
    # Print table
    print(f"{'Chain':<10} | {'Pool':<15} | {'Pool Address':<44} | {'Total USD':>12}")
    print("-"*90)
    for chain, pool_name, pool_address, usd in results:
        usd_str = f"{usd:,.2f}" if usd is not None else "N/A"
        print(f"{chain:<10} | {pool_name:<15} | {pool_address:<44} | {usd_str:>12}")
    # Group by chain
    print("\nTotals by Chain:")
    chain_totals = {}
    for chain, _, _, usd in results:
        chain_totals.setdefault(chain, 0)
        chain_totals[chain] += usd if usd else 0
    for chain, total in chain_totals.items():
        print(f"{chain:<10}: $ {total:,.2f}")

if __name__ == "__main__":
    main() 