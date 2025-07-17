import requests
import pandas as pd
from datetime import datetime

# Pool name and Flipside API endpoint pairs
POOLS = [
    ("WETH/FOX Ethereum", "https://flipsidecrypto.xyz/api/v1/queries/acfbdcb1-216d-4762-b924-5287567669de/data/latest"),
    ("GIV/FOX Ethereum", "https://flipsidecrypto.xyz/api/v1/queries/074a15b1-f372-4e07-bb9a-0c0f95ae7a5e/data/latest"),
    ("WETH/FOX Polygon", "https://flipsidecrypto.xyz/api/v1/queries/904f5308-6ad1-49d7-ad65-c367fbb55284/data/latest"),
    ("WETH/FOX Arbitrum V2", "https://flipsidecrypto.xyz/api/v1/queries/db96afc6-6b47-49a9-a2f1-02b85e867c08/data/latest"),
    ("wxDAI/FOX Gnosis", "https://flipsidecrypto.xyz/api/v1/queries/1a92af1a-29d2-4cef-bc73-b0d6d2024b1a/data/latest"),
    ("GIV/FOX Gnosis", "https://flipsidecrypto.xyz/api/v1/queries/b3e7e396-8dae-405a-8261-fee3ce49717d/data/latest"),
    ("HNY/FOX Gnosis", "https://flipsidecrypto.xyz/api/v1/queries/28f6e904-29e0-40f4-916a-8e496b15cf97/data/latest"),
    ("RUNE/FOX THORChain", "https://flipsidecrypto.xyz/api/v1/queries/1085eb75-7bc6-47c6-b8a7-500b2236ccb3/data/latest"),
    ("WETH/FOX Arbitrum V3", "https://flipsidecrypto.xyz/api/v1/queries/00baa258-5e2e-4c6d-8a28-5379839c1809/data/latest"),
]

def fetch_latest_fox_lp(api_url: str) -> float:
    try:
        resp = requests.get(api_url, timeout=30)
        data = resp.json()["data"]
        if not data:
            return 0.0
        df = pd.DataFrame(data)
        df['DAY'] = pd.to_datetime(df['DAY'], errors='coerce')
        df = df.dropna(subset=['DAY'])
        df = df.sort_values('DAY')
        # Get the latest non-null FOX Liquidity value
        latest = df.dropna(subset=['FOX Liquidity']).iloc[-1]
        return float(latest['FOX Liquidity'])
    except Exception as e:
        print(f"Error fetching {api_url}: {e}")
        return 0.0

def main():
    print(f"{'Pool':<25} | {'Latest FOX LP':>20}")
    print("-"*50)
    for pool_name, api_url in POOLS:
        fox_lp = fetch_latest_fox_lp(api_url)
        print(f"{pool_name:<25} | {fox_lp:>20,.0f}")

if __name__ == "__main__":
    main() 