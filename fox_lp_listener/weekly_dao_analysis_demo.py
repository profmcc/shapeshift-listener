#!/usr/bin/env python3
"""
Weekly DAO FOX Pool Activity Analysis Demo for Q2 2025
Demonstrates the weekly net add/remove analysis with color-coded visualization.
"""

import pandas as pd
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style
import sqlite3

# Initialize colorama for colored output
init(autoreset=True)

# Q2 2025 date range (April 1 - June 30, 2025)
Q2_START = datetime(2025, 4, 1)
Q2_END = datetime(2025, 6, 30, 23, 59, 59)

def generate_weekly_weeks():
    """Generate list of weeks in Q2 2025"""
    weeks = []
    current_week_start = Q2_START
    
    while current_week_start <= Q2_END:
        week_end = current_week_start + timedelta(days=7)
        if week_end > Q2_END:
            week_end = Q2_END
            
        weeks.append({
            'start': current_week_start.strftime('%Y-%m-%d'),
            'end': (week_end - timedelta(seconds=1)).strftime('%Y-%m-%d')
        })
        
        current_week_start = week_end
        
    return weeks

def get_color_for_value(value: float, max_abs_value: float) -> str:
    """Get color based on value (green for positive, red for negative)"""
    if value == 0:
        return Style.RESET_ALL
    
    intensity = min(abs(value) / max_abs_value, 1.0) if max_abs_value > 0 else 0
    
    if value > 0:
        # Green gradient for additions
        if intensity < 0.3:
            return Fore.GREEN
        elif intensity < 0.7:
            return Fore.GREEN + Style.BRIGHT
        else:
            return Back.GREEN + Fore.WHITE + Style.BRIGHT
    else:
        # Red gradient for removals
        if intensity < 0.3:
            return Fore.RED
        elif intensity < 0.7:
            return Fore.RED + Style.BRIGHT
        else:
            return Back.RED + Fore.WHITE + Style.BRIGHT

def create_demo_data():
    """Create demo data for Q2 2025 analysis"""
    weeks = generate_weekly_weeks()
    
    # Simulate realistic DAO activity patterns
    demo_data = []
    
    pools = [
        {'chain': 'ethereum', 'name': 'WETH/FOX V2'},
        {'chain': 'arbitrum', 'name': 'WETH/FOX V2'},
        {'chain': 'arbitrum', 'name': 'WETH/FOX V3'},
    ]
    
    for pool in pools:
        for i, week in enumerate(weeks):
            # Simulate realistic patterns:
            # - More activity in early weeks (April)
            # - Some removals in May
            # - Mixed activity in June
            if i < 4:  # April weeks
                adds = 2 if i == 0 else (1 if i % 2 == 0 else 0)
                removes = 0 if i < 2 else (1 if i == 3 else 0)
            elif i < 8:  # May weeks
                adds = 1 if i == 4 else (0 if i % 2 == 0 else 1)
                removes = 1 if i == 5 else (0 if i % 2 == 0 else 1)
            else:  # June weeks
                adds = 1 if i % 2 == 0 else 0
                removes = 0 if i % 2 == 0 else 1
            
            demo_data.append({
                'chain_name': pool['chain'],
                'pool_name': pool['name'],
                'week_start': week['start'],
                'week_end': week['end'],
                'adds': adds,
                'removes': removes,
                'net_change': adds - removes
            })
    
    return demo_data

def create_color_table(weekly_results: list) -> None:
    """Create a color-coded table showing weekly net changes"""
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(weekly_results)
    
    if df.empty:
        print("\n" + "="*100)
        print("WEEKLY DAO NET LIQUIDITY CHANGES - Q2 2025")
        print("(Green = Additions, Red = Removals)")
        print("="*100)
        print("\nNo data available for Q2 2025")
        return
    
    # Get unique weeks across all pools
    weeks = sorted(df['week_start'].unique())
    pools = df[['chain_name', 'pool_name']].drop_duplicates()
    
    # Create pivot table
    pivot_data = []
    for _, pool in pools.iterrows():
        pool_data = df[(df['chain_name'] == pool['chain_name']) & 
                      (df['pool_name'] == pool['pool_name'])]
        
        row = [f"{pool['chain_name']}/{pool['pool_name']}"]
        for week in weeks:
            week_data = pool_data[pool_data['week_start'] == week]
            if not week_data.empty:
                net_change = week_data.iloc[0]['net_change']
                row.append(net_change)
            else:
                row.append(0)
        pivot_data.append(row)
    
    # Calculate max absolute value for color intensity
    all_values = [val for row in pivot_data for val in row[1:] if isinstance(val, (int, float))]
    max_abs_value = max(abs(val) for val in all_values) if all_values else 1
    
    print("\n" + "="*120)
    print("WEEKLY DAO NET LIQUIDITY CHANGES - Q2 2025")
    print("(Green = Additions, Red = Removals)")
    print("="*120)
    
    # Header
    print(f"{'Pool':<30}", end="")
    for i, week in enumerate(weeks):
        week_num = i + 1
        week_date = week[:10]  # Just the date part
        print(f"{'W' + str(week_num):<8}", end="")
    print()
    
    print(f"{'='*30}", end="")
    for _ in weeks:
        print(f"{'='*8}", end="")
    print()
    
    # Data rows
    for row in pivot_data:
        pool_name = row[0][:29]  # Truncate long names
        print(f"{pool_name:<30}", end="")
        
        for val in row[1:]:
            color = get_color_for_value(val, max_abs_value)
            if val == 0:
                display_val = "  0"
            elif val > 0:
                display_val = f" +{val}"
            else:
                display_val = f" {val}"
            print(f"{color}{display_val:<8}{Style.RESET_ALL}", end="")
        print()
    
    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    total_adds = df['adds'].sum()
    total_removes = df['removes'].sum()
    total_net = df['net_change'].sum()
    
    print(f"Total Additions:  {Fore.GREEN}{total_adds:>6}{Style.RESET_ALL}")
    print(f"Total Removals:   {Fore.RED}{total_removes:>6}{Style.RESET_ALL}")
    print(f"Net Change:       {get_color_for_value(total_net, max_abs_value)}{total_net:>6}{Style.RESET_ALL}")
    
    # Weekly totals
    print(f"\nWeekly Net Changes:")
    for i, week in enumerate(weeks):
        week_total = sum(row[i+1] for row in pivot_data if isinstance(row[i+1], (int, float)))
        color = get_color_for_value(week_total, max_abs_value)
        week_num = i + 1
        week_date = week[:10]
        print(f"  Week {week_num} ({week_date}): {color}{week_total:>3}{Style.RESET_ALL}")
    
    # Monthly breakdown
    print(f"\nMonthly Breakdown:")
    monthly_data = {
        'April': df[df['week_start'].str.startswith('2025-04')],
        'May': df[df['week_start'].str.startswith('2025-05')],
        'June': df[df['week_start'].str.startswith('2025-06')]
    }
    
    for month, month_df in monthly_data.items():
        if not month_df.empty:
            month_adds = month_df['adds'].sum()
            month_removes = month_df['removes'].sum()
            month_net = month_df['net_change'].sum()
            print(f"  {month}: {Fore.GREEN}+{month_adds}{Style.RESET_ALL} / {Fore.RED}-{month_removes}{Style.RESET_ALL} = {get_color_for_value(month_net, max_abs_value)}{month_net:>3}{Style.RESET_ALL}")

def save_demo_results_to_db(weekly_results: list) -> None:
    """Save demo results to database"""
    conn = sqlite3.connect('fox_pools_analysis.db')
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_dao_activity_demo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_name TEXT,
            pool_name TEXT,
            week_start TEXT,
            week_end TEXT,
            adds INTEGER,
            removes INTEGER,
            net_change INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Clear existing demo data
    cursor.execute('DELETE FROM weekly_dao_activity_demo')
    
    # Insert demo data
    for result in weekly_results:
        cursor.execute('''
            INSERT INTO weekly_dao_activity_demo 
            (chain_name, pool_name, week_start, week_end, adds, removes, net_change)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result['chain_name'],
            result['pool_name'],
            result['week_start'],
            result['week_end'],
            result['adds'],
            result['removes'],
            result['net_change']
        ))
    
    conn.commit()
    conn.close()
    print(f"\nSaved {len(weekly_results)} demo weekly activity records to database")

def main():
    """Main demo function"""
    print("Starting Weekly DAO FOX Pool Activity Analysis Demo for Q2 2025")
    print("Note: This is a demonstration with simulated data")
    
    # Generate demo data
    demo_data = create_demo_data()
    
    # Display color-coded table
    create_color_table(demo_data)
    
    # Save to database
    save_demo_results_to_db(demo_data)
    
    print("\n" + "="*60)
    print("ANALYSIS NOTES:")
    print("="*60)
    print("• This analysis covers Q2 2025 (April-June 2025)")
    print("• Green values indicate liquidity additions")
    print("• Red values indicate liquidity removals")
    print("• Intensity of color indicates magnitude of change")
    print("• Data is simulated for demonstration purposes")
    print("• Real analysis would require historical blockchain data")

if __name__ == "__main__":
    main() 