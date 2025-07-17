import requests

def get_thorchain_pool_stats(pool_id: str = 'ETH.FOX-0XC770EEFAD204B5180DF6A14EE197D99D808EE52D'):
    url = f'https://midgard.thorchain.info/v2/pool/{pool_id}'
    resp = requests.get(url, timeout=15)
    data = resp.json()
    if 'pool' not in data:
        raise Exception('No pool data found')
    pool = data['pool']
    asset_depth = float(pool['assetDepth']) / 1e8  # FOX (8 decimals)
    rune_depth = float(pool['runeDepth']) / 1e8    # RUNE (8 decimals)
    asset_price_usd = float(pool['assetPriceUSD'])
    asset_usd = asset_depth * asset_price_usd
    rune_usd = rune_depth * float(pool['runePriceUSD'])
    total_usd = asset_usd + rune_usd
    print(f"THORChain Pool: {pool_id}")
    print(f"FOX Balance: {asset_depth:,.2f} ($ {asset_usd:,.2f})")
    print(f"RUNE Balance: {rune_depth:,.2f} ($ {rune_usd:,.2f})")
    print(f"Total USD Value: $ {total_usd:,.2f}")
    print(f"FOX Price: $ {asset_price_usd:.4f}")
    print(f"RUNE Price: $ {pool['runePriceUSD']}")

if __name__ == "__main__":
    get_thorchain_pool_stats() 