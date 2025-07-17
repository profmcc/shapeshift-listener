import requests
from web3 import Web3

# Pool definitions: (Chain, Pool Name, Address, Type, RPC/Subgraph URL)
POOLS = [
    ("Arbitrum", "WETH/FOX V2", "0x5f6ce0ca13b87bd738519545d3e018e70e339c24", "v2", "https://arb1.arbitrum.io/rpc"),
    ("Arbitrum", "WETH/FOX V3", "0x76d4d1eaa0c4b3645e75c46e573c1d4f75e9041e", "v3", "https://api.thegraph.com/subgraphs/name/ianlapham/arbitrum-minimal"),
    ("Ethereum", "GIV/FOX", "0xad0e10df5dcdf21396b9d64715aadaf543f8b376", "v2", "https://eth.llamarpc.com"),
    ("Ethereum", "WETH/FOX", "0x470e8de2ebaef52014a47cb5e6af86884947f08c", "v2", "https://eth.llamarpc.com"),
    ("Gnosis", "GIV/FOX", "0x75594f01da2e4231e16e67f841c307c4df2313d1", "v2", "https://rpc.gnosis.gateway.fm"),
    ("Gnosis", "wxDAI/FOX", "0xc22313fd39f7d4d73a89558f9e8e444c86464bac", "v2", "https://rpc.gnosis.gateway.fm"),
    ("Gnosis", "HNY/FOX", "0x8a0bee989c591142414ad67fb604539d917889df", "v2", "https://rpc.gnosis.gateway.fm"),
    ("Polygon", "WETH/FOX", "0x93ef615f1ddd27d0e141ad7192623a5c45e8f200", "v2", "https://polygon-rpc.com"),
    ("THORChain", "RUNE/FOX", "ETH.FOX-0XC770EEFAD204B5180DF6A14EE197D99D808EE52D", "thorchain", None),
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
    return {
        'chain': chain,
        'pool_name': pool_name,
        'pool_address': pool_address,
        'fox_balance': fox_balance,
        'fox_usd': fox_usd,
        'other_balance': other_balance,
        'other_usd': other_usd,
        'total_usd': total_usd,
    }

def query_v3_pool(chain, pool_name, pool_address, subgraph_url):
    pool_id = pool_address.lower()
    query = f"""
    {{
      pool(id: \"{pool_id}\") {{
        id
        token0 {{ symbol decimals }}
        token1 {{ symbol decimals }}
        totalValueLockedToken0
        totalValueLockedToken1
        totalValueLockedUSD
      }}
    }}
    """
    resp = requests.post(subgraph_url, json={'query': query})
    data = resp.json()["data"]["pool"]
    fox_balance = float(data["totalValueLockedToken0"])
    other_balance = float(data["totalValueLockedToken1"])
    total_usd = float(data["totalValueLockedUSD"])
    return {
        'chain': chain,
        'pool_name': pool_name,
        'pool_address': pool_address,
        'fox_balance': fox_balance,
        'fox_usd': None,
        'other_balance': other_balance,
        'other_usd': None,
        'total_usd': total_usd,
    }

def main():
    results = []
    for chain, pool_name, pool_address, pool_type, url in POOLS:
        try:
            if pool_type == "v2":
                res = query_v2_pool(chain, pool_name, pool_address, url)
            elif pool_type == "v3":
                res = query_v3_pool(chain, pool_name, pool_address, url)
            elif pool_type == "thorchain":
                res = {
                    'chain': chain,
                    'pool_name': pool_name,
                    'pool_address': pool_address,
                    'fox_balance': None,
                    'fox_usd': None,
                    'other_balance': None,
                    'other_usd': None,
                    'total_usd': 63300.0,
                }
            else:
                continue
            results.append(res)
        except Exception as e:
            print(f"Error querying {pool_name} ({pool_address}) on {chain}: {e}")
    # Print table
    print(f"{'Chain':<10} | {'Pool':<15} | {'FOX Balance':>15} | {'Other Bal':>15} | {'Total USD':>12}")
    print("-"*80)
    for r in results:
        print(f"{r['chain']:<10} | {r['pool_name']:<15} | {str(r['fox_balance']):>15} | {str(r['other_balance']):>15} | {r['total_usd']:>12,.2f}")
    # Group by chain
    print("\nTotals by Chain:")
    chain_totals = {}
    for r in results:
        chain_totals.setdefault(r['chain'], 0)
        chain_totals[r['chain']] += r['total_usd']
    for chain, total in chain_totals.items():
        print(f"{chain:<10}: $ {total:,.2f}")

if __name__ == "__main__":
    main() 