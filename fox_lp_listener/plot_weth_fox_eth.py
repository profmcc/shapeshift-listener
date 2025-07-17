import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fetch data from Flipside API
url = "https://flipsidecrypto.xyz/api/v1/queries/acfbdcb1-216d-4762-b924-5287567669de/data/latest"
response = requests.get(url)
data = response.json()["data"]

# Convert to DataFrame
if isinstance(data, list) and len(data) > 0 and 'DAY' in data[0]:
    df = pd.DataFrame(data)
    df['DAY'] = pd.to_datetime(df['DAY'])
    df = df.sort_values('DAY')
    df['FOX Liquidity'] = pd.to_numeric(df['FOX Liquidity'])
else:
    raise ValueError("Unexpected data format from Flipside API")

# Plot
plt.figure(figsize=(14, 5))
plt.style.use('dark_background')
plt.plot(df['DAY'], df['FOX Liquidity'], color='#ff1fae', linewidth=2, label='FOX_AMOUNT')
plt.title("Cumulative FOX LP'd in WETH/FOX Ethereum Pool", fontsize=14, fontweight='bold', loc='left')
plt.xlabel("DATE")
plt.ylabel("FOX_AMOUNT")
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig("weth_fox_eth_cumulative.png", dpi=200)
plt.show() 