#!/usr/bin/env python3
"""
Weekly DAO FOX Pool Analysis Display
Shows weekly analysis format with real current data and demonstrates change tracking.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init(autoreset=True)

def get_current_positions_from_db():
    """Get current positions from database"""
    conn = sqlite3.connect('fox_pools_analysis.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT chain_name, pool_name, dao_usd_value, dao_lp_balance, ownership_percentage, timestamp
        FROM dao_position_history
        ORDER BY timestamp DESC
        LIMIT 10
    ''')
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return []
    
    # Get the most recent entry for each pool
    latest_positions = {}
    for row in data:
        chain_name, pool_name, usd_value, lp_balance, ownership, timestamp = row
        pool_key = f"{chain_name}/{pool_name}"
        
        if pool_key not in latest_positions:
            latest_positions[pool_key] = {
                'chain_name': chain_name,
                'pool_name': pool_name,
                'usd_value': usd_value,
                'lp_balance': lp_balance or 0,
                'ownership': ownership or 0,
                'timestamp': timestamp
            }
    
    return list(latest_positions.values())

def generate_weekly_weeks():
    """Generate list of weeks for the last 3 months"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    weeks = []
    current_week_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    while current_week_start <= end_date:
        week_end = current_week_start + timedelta(days=7)
        if week_end > end_date:
            week_end = end_date
            
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

def create_weekly_analysis_table():
    """Create a weekly analysis table with real data"""
    
    # Get current positions
    positions = get_current_positions_from_db()
    
    if not positions:
        print("No position data found. Run weekly_dao_tracking.py first.")
        return
    
    # Generate weeks
    weeks = generate_weekly_weeks()
    
    # Create weekly data based on current positions
    # This simulates what the analysis would look like if we had historical data
    weekly_data = []
    
    for position in positions:
        pool_key = f"{position['chain_name']}/{position['pool_name']}"
        current_value = position['usd_value']
        
        # Simulate weekly changes based on current value
        # This is for demonstration - in reality, we'd have actual historical data
        for i, week in enumerate(weeks):
            # Simulate realistic patterns based on current value
            if i < len(weeks) // 3:  # First third - some additions
                adds = 1 if i % 3 == 0 else 0
                removes = 0
            elif i < 2 * len(weeks) // 3:  # Middle third - mixed activity
                adds = 1 if i % 4 == 0 else 0
                removes = 1 if i % 5 == 0 else 0
            else:  # Last third - some removals
                adds = 0
                removes = 1 if i % 3 == 0 else 0
            
            # Scale based on current position value
            if current_value > 1000000:  # Large position
                adds *= 2
                removes *= 2
            elif current_value > 100000:  # Medium position
                adds *= 1
                removes *= 1
            else:  # Small position
                adds = max(0, adds - 1)
                removes = max(0, removes - 1)
            
            weekly_data.append({
                'chain_name': position['chain_name'],
                'pool_name': position['pool_name'],
                'week_start': week['start'],
                'week_end': week['end'],
                'adds': adds,
                'removes': removes,
                'net_change': adds - removes,
                'current_value': current_value
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(weekly_data)
    
    # Get unique weeks and pools
    weeks_list = sorted(df['week_start'].unique())
    pools = df[['chain_name', 'pool_name']].drop_duplicates()
    
    # Create pivot table
    pivot_data = []
    for _, pool in pools.iterrows():
        pool_data = df[(df['chain_name'] == pool['chain_name']) & 
                      (df['pool_name'] == pool['pool_name'])]
        
        row = [f"{pool['chain_name']}/{pool['pool_name']}"]
        for week in weeks_list:
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
    print("WEEKLY DAO NET LIQUIDITY CHANGES - LAST 3 MONTHS")
    print("(Green = Additions, Red = Removals)")
    print("Based on real current DAO positions")
    print("="*120)
    
    # Header
    print(f"{'Pool':<30}", end="")
    for i, week in enumerate(weeks_list):
        week_num = i + 1
        week_date = week[:10]  # Just the date part
        print(f"{'W' + str(week_num):<8}", end="")
    print()
    
    print(f"{'='*30}", end="")
    for _ in weeks_list:
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
    
    # Current position summary
    print(f"\nCURRENT DAO POSITIONS:")
    total_current_value = sum(pos['usd_value'] for pos in positions)
    print(f"Total USD Value: ${total_current_value:,.2f}")
    
    for pos in positions:
        pool_name = f"{pos['chain_name']}/{pos['pool_name']}"
        usd_value = pos['usd_value']
        lp_balance = pos['lp_balance']
        ownership = pos['ownership']
        
        if lp_balance > 0:
            print(f"  {pool_name}: ${usd_value:,.2f} (LP: {lp_balance:,.4f}, Share: {ownership:.2f}%)")
        else:
            print(f"  {pool_name}: ${usd_value:,.2f}")
    
    # Weekly totals
    print(f"\nWeekly Net Changes:")
    for i, week in enumerate(weeks_list):
        week_total = sum(row[i+1] for row in pivot_data if isinstance(row[i+1], (int, float)))
        color = get_color_for_value(week_total, max_abs_value)
        week_num = i + 1
        week_date = week[:10]
        print(f"  Week {week_num} ({week_date}): {color}{week_total:>3}{Style.RESET_ALL}")

def main():
    """Main function"""
    print("Weekly DAO FOX Pool Analysis Display")
    print("Based on real current DAO positions")
    
    create_weekly_analysis_table()
    
    print("\n" + "="*60)
    print("ANALYSIS NOTES:")
    print("="*60)
    print("• This analysis shows what weekly tracking would look like")
    print("• Current positions are real data from blockchain")
    print("• Weekly changes are simulated based on current position sizes")
    print("• Green values indicate liquidity additions")
    print("• Red values indicate liquidity removals")
    print("• Intensity of color indicates magnitude of change")
    print("• Run weekly_dao_tracking.py regularly to build historical data")

if __name__ == "__main__":
    main() 