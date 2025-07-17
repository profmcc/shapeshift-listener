#!/usr/bin/env python3
"""
DAO Liquidity Health Presentation Data Generator
Creates charts and data for PowerPoint presentation on DAO liquidity health.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import numpy as np
from web3 import Web3
import requests

# Configure matplotlib for better charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Configuration
DAO_DB_PATH = 'fox_pools_analysis.db'

# DAO Treasury Addresses
DAO_TREASURY_ADDRESSES = {
    'ethereum': Web3.to_checksum_address('0x90a48d5cf7343b08da12e067680b4c6dbfe551be'),
    'arbitrum': Web3.to_checksum_address('0x38276553f8fbf2a027d901f8be45f00373d8dd48'),
    'optimism': Web3.to_checksum_address('0x6268d07327f4fb7380732dc6d63d95f88c0e083b'),
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

def get_current_dao_data() -> List[Dict]:
    """Get current DAO position data"""
    conn = sqlite3.connect(DAO_DB_PATH)
    cursor = conn.cursor()
    
    # Get latest DAO positions - get the most recent record for each pool
    cursor.execute('''
        SELECT chain_name, pool_name, dao_usd_value, dao_lp_balance, 
               total_lp_supply, ownership_percentage, token0_amt, token1_amt,
               fox_amt, weth_amt, fox_price, weth_price
        FROM dao_position_history 
        WHERE id IN (
            SELECT MAX(id) 
            FROM dao_position_history 
            GROUP BY chain_name, pool_name
        )
        ORDER BY dao_usd_value DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    data = []
    for row in results:
        data.append({
            'chain': row[0],
            'pool': row[1],
            'dao_usd_value': row[2] or 0,
            'dao_lp_balance': row[3] or 0,
            'total_lp_supply': row[4] or 0,
            'ownership_percentage': row[5] or 0,
            'token0_amt': row[6] or 0,
            'token1_amt': row[7] or 0,
            'fox_amt': row[8] or 0,
            'weth_amt': row[9] or 0,
            'fox_price': row[10] or 0,
            'weth_price': row[11] or 0
        })
    
    return data

def get_historical_dao_data() -> pd.DataFrame:
    """Get historical DAO data for trends"""
    conn = sqlite3.connect(DAO_DB_PATH)
    
    query = '''
        SELECT timestamp, chain_name, pool_name, dao_usd_value, 
               ownership_percentage, fox_amt, weth_amt
        FROM dao_position_history 
        ORDER BY timestamp DESC
        LIMIT 100
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def create_liquidity_distribution_chart(data: List[Dict]) -> None:
    """Create pie chart showing DAO liquidity distribution"""
    plt.figure(figsize=(12, 8))
    
    # Prepare data
    labels = []
    sizes = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for item in data:
        if item['dao_usd_value'] > 0:
            labels.append(f"{item['chain'].capitalize()}\n{item['pool']}")
            sizes.append(item['dao_usd_value'])
    
    if not sizes:
        plt.text(0.5, 0.5, 'No DAO liquidity data available', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=16)
        plt.title('DAO Liquidity Distribution by Pool', fontsize=16, fontweight='bold', pad=20)
    else:
        # Create pie chart
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title('DAO Liquidity Distribution by Pool', fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        
        # Add total value annotation
        total_value = sum(sizes)
        plt.figtext(0.5, 0.02, f'Total DAO Liquidity: ${total_value:,.0f}', 
                    ha='center', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('dao_liquidity_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_ownership_chart(data: List[Dict]) -> None:
    """Create bar chart showing DAO ownership percentages"""
    plt.figure(figsize=(12, 8))
    
    pools = []
    ownership = []
    colors = []
    
    for item in data:
        if item['dao_usd_value'] > 0:
            pools.append(f"{item['chain'].capitalize()}\n{item['pool']}")
            ownership.append(item['ownership_percentage'])
            
            # Color coding based on ownership percentage
            if item['ownership_percentage'] > 50:
                colors.append('#FF6B6B')  # Red for high ownership
            elif item['ownership_percentage'] > 25:
                colors.append('#FFA500')  # Orange for medium ownership
            else:
                colors.append('#4ECDC4')  # Green for low ownership
    
    if not pools:
        plt.text(0.5, 0.5, 'No DAO ownership data available', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=16)
        plt.title('DAO Ownership Percentage by Pool', fontsize=16, fontweight='bold', pad=20)
    else:
        bars = plt.bar(pools, ownership, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar, value in zip(bars, ownership):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.title('DAO Ownership Percentage by Pool', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Ownership Percentage (%)', fontsize=12)
        plt.ylim(0, max(ownership) * 1.2 if ownership else 100)
        
        # Add horizontal line at 50%
        plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50% Threshold')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('dao_ownership_percentages.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_liquidity_health_chart(data: List[Dict]) -> None:
    """Create stacked bar chart showing liquidity health metrics"""
    plt.figure(figsize=(14, 8))
    
    pools = []
    dao_liquidity = []
    total_liquidity = []
    other_liquidity = []
    
    for item in data:
        if item['dao_usd_value'] > 0:
            pool_name = f"{item['chain'].capitalize()}\n{item['pool']}"
            pools.append(pool_name)
            
            dao_value = item['dao_usd_value']
            total_value = dao_value / (item['ownership_percentage'] / 100) if item['ownership_percentage'] > 0 else dao_value
            other_value = total_value - dao_value
            
            dao_liquidity.append(dao_value)
            total_liquidity.append(total_value)
            other_liquidity.append(other_value)
    
    # Create stacked bar chart
    x = np.arange(len(pools))
    width = 0.6
    
    plt.bar(x, dao_liquidity, width, label='DAO Liquidity', color='#FF6B6B', alpha=0.8)
    plt.bar(x, other_liquidity, width, bottom=dao_liquidity, label='Other Liquidity', color='#4ECDC4', alpha=0.8)
    
    plt.xlabel('Pools', fontsize=12)
    plt.ylabel('Liquidity Value (USD)', fontsize=12)
    plt.title('DAO vs Total Pool Liquidity', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x, pools, rotation=45, ha='right')
    plt.legend()
    
    # Add value annotations
    for i, (dao_val, total_val) in enumerate(zip(dao_liquidity, total_liquidity)):
        plt.text(i, dao_val/2, f'${dao_val:,.0f}', ha='center', va='center', fontweight='bold', color='white')
        plt.text(i, dao_val + total_val/2, f'${total_val:,.0f}', ha='center', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('liquidity_health_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_historical_trend_chart(df: pd.DataFrame) -> None:
    """Create line chart showing historical DAO value trends"""
    plt.figure(figsize=(14, 8))
    
    # Group by timestamp and sum DAO values
    daily_data = df.groupby(df['timestamp'].dt.date)['dao_usd_value'].sum().reset_index()
    daily_data['timestamp'] = pd.to_datetime(daily_data['timestamp'])
    
    if len(daily_data) == 0:
        plt.text(0.5, 0.5, 'No historical data available', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=16)
        plt.title('DAO Liquidity Value Over Time', fontsize=16, fontweight='bold', pad=20)
    else:
        plt.plot(daily_data['timestamp'], daily_data['dao_usd_value'], 
                 marker='o', linewidth=3, markersize=8, color='#FF6B6B')
        
        plt.title('DAO Liquidity Value Over Time', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Total DAO Liquidity Value (USD)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add trend line only if we have enough data points
        if len(daily_data) > 1:
            try:
                z = np.polyfit(range(len(daily_data)), daily_data['dao_usd_value'], 1)
                p = np.poly1d(z)
                plt.plot(daily_data['timestamp'], p(range(len(daily_data))), 
                         '--', alpha=0.7, color='#4ECDC4', linewidth=2, label='Trend')
                plt.legend()
            except:
                pass  # Skip trend line if calculation fails
    
    plt.tight_layout()
    plt.savefig('dao_liquidity_trend.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_health_metrics_dashboard(data: List[Dict]) -> None:
    """Create a dashboard with key health metrics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Calculate metrics
    total_dao_value = sum(item['dao_usd_value'] for item in data)
    active_pools_data = [item for item in data if item['dao_usd_value'] > 0]
    total_ownership = sum(item['ownership_percentage'] for item in active_pools_data)
    avg_ownership = total_ownership / len(active_pools_data) if active_pools_data else 0
    active_pools = len(active_pools_data)
    
    # Metric 1: Total DAO Value
    ax1.pie([total_dao_value, 2000000 - total_dao_value], 
             labels=['DAO Value', 'Target'], autopct='%1.1f%%', 
             colors=['#FF6B6B', '#E0E0E0'], startangle=90)
    ax1.set_title('DAO Liquidity vs Target ($2M)', fontweight='bold')
    
    # Metric 2: Average Ownership
    ax2.bar(['Average Ownership'], [avg_ownership], color='#4ECDC4', alpha=0.8)
    ax2.set_ylabel('Percentage (%)')
    ax2.set_title('Average DAO Ownership', fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.text(0, avg_ownership + 2, f'{avg_ownership:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Metric 3: Active Pools
    ax3.bar(['Active Pools'], [active_pools], color='#45B7D1', alpha=0.8)
    ax3.set_ylabel('Number of Pools')
    ax3.set_title('Active DAO Pools', fontweight='bold')
    ax3.set_ylim(0, 5)
    ax3.text(0, active_pools + 0.1, str(active_pools), ha='center', va='bottom', fontweight='bold')
    
    # Metric 4: Health Score
    health_score = min(100, (total_dao_value / 1000000) * 50 + (avg_ownership / 100) * 30 + (active_pools / 3) * 20)
    ax4.pie([health_score, 100 - health_score], 
             labels=['Health Score', ''], autopct='%1.0f%%', 
             colors=['#96CEB4', '#E0E0E0'], startangle=90)
    ax4.set_title('Overall Liquidity Health Score', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('liquidity_health_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_presentation_data() -> Dict:
    """Generate all presentation data and charts"""
    print("Generating DAO Liquidity Health Presentation Data...")
    
    # Get current data
    current_data = get_current_dao_data()
    historical_data = get_historical_dao_data()
    
    # Create charts
    create_liquidity_distribution_chart(current_data)
    create_ownership_chart(current_data)
    create_liquidity_health_chart(current_data)
    create_historical_trend_chart(historical_data)
    create_health_metrics_dashboard(current_data)
    
    # Calculate summary statistics
    total_dao_value = sum(item['dao_usd_value'] for item in current_data)
    active_pools_data = [item for item in current_data if item['dao_usd_value'] > 0]
    total_ownership = sum(item['ownership_percentage'] for item in active_pools_data)
    avg_ownership = total_ownership / len(active_pools_data) if active_pools_data else 0
    active_pools = len(active_pools_data)
    
    # Health score calculation
    health_score = min(100, (total_dao_value / 1000000) * 50 + (avg_ownership / 100) * 30 + (active_pools / 3) * 20)
    
    summary_data = {
        'total_dao_value': total_dao_value,
        'avg_ownership': avg_ownership,
        'active_pools': active_pools,
        'health_score': health_score,
        'charts_generated': [
            'dao_liquidity_distribution.png',
            'dao_ownership_percentages.png',
            'liquidity_health_comparison.png',
            'dao_liquidity_trend.png',
            'liquidity_health_dashboard.png'
        ],
        'pool_details': current_data
    }
    
    # Save summary data
    with open('presentation_summary.json', 'w') as f:
        json.dump(summary_data, f, indent=2, default=str)
    
    print("✅ Presentation data generated successfully!")
    print(f"📊 Total DAO Value: ${total_dao_value:,.2f}")
    print(f"📈 Average Ownership: {avg_ownership:.1f}%")
    print(f"🏊 Active Pools: {active_pools}")
    print(f"💚 Health Score: {health_score:.1f}/100")
    print(f"📁 Charts saved: {len(summary_data['charts_generated'])} files")
    
    return summary_data

def main():
    """Main function"""
    try:
        summary = generate_presentation_data()
        
        print("\n" + "="*60)
        print("📊 PRESENTATION DATA READY")
        print("="*60)
        print("Charts generated for PowerPoint:")
        for chart in summary['charts_generated']:
            print(f"  ✅ {chart}")
        print("\nSummary data saved to: presentation_summary.json")
        
    except Exception as e:
        print(f"❌ Error generating presentation data: {e}")

if __name__ == "__main__":
    main() 