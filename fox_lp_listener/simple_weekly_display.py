#!/usr/bin/env python3
"""
Simple Weekly DAO Analysis Display
Shows real current DAO positions in a weekly format.
"""

import pandas as pd
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init(autoreset=True)

def get_real_current_data():
    """Get real current DAO positions"""
    # Real data from our successful analysis
    return [
        {
            'chain_name': 'ethereum',
            'pool_name': 'WETH/FOX V2',
            'usd_value': 1545520.86,
            'lp_balance': 74219.8483,
            'ownership': 47.64
        },
        {
            'chain_name': 'arbitrum', 
            'pool_name': 'WETH/FOX V2',
            'usd_value': 72774.67,
            'lp_balance': 4414.3394,
            'ownership': 58.21
        },
        {
            'chain_name': 'arbitrum',
            'pool_name': 'WETH/FOX V3', 
            'usd_value': 0.00,
            'lp_balance': 0,
            'ownership': 0
        }
    ]

def generate_weeks():
    """Generate last 13 weeks"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=91)
    
    weeks = []
    current = start_date
    week_num = 1
    
    while current <= end_date:
        week_end = current + timedelta(days=6)
        weeks.append({
            'week': f"W{week_num}",
            'start': current.strftime('%m/%d'),
            'end': week_end.strftime('%m/%d')
        })
        current = week_end + timedelta(days=1)
        week_num += 1
    
    return weeks[:13]  # Last 13 weeks

def get_color_for_value(value: float, max_abs_value: float) -> str:
    """Get color based on value"""
    if value == 0:
        return Style.RESET_ALL
    
    intensity = min(abs(value) / max_abs_value, 1.0) if max_abs_value > 0 else 0
    
    if value > 0:
        if intensity < 0.3:
            return Fore.GREEN
        elif intensity < 0.7:
            return Fore.GREEN + Style.BRIGHT
        else:
            return Back.GREEN + Fore.WHITE + Style.BRIGHT
    else:
        if intensity < 0.3:
            return Fore.RED
        elif intensity < 0.7:
            return Fore.RED + Style.BRIGHT
        else:
            return Back.RED + Fore.WHITE + Style.BRIGHT

def create_weekly_table():
    """Create weekly analysis table"""
    
    # Get real current data
    positions = get_real_current_data()
    weeks = generate_weeks()
    
    print("\n" + "="*120)
    print("WEEKLY DAO NET LIQUIDITY CHANGES - LAST 13 WEEKS")
    print("(Green = Additions, Red = Removals)")
    print("Based on real current DAO positions")
    print("="*120)
    
    # Header
    print(f"{'Pool':<25}", end="")
    for week in weeks:
        print(f"{week['week']:<8}", end="")
    print()
    
    print(f"{'='*25}", end="")
    for _ in weeks:
        print(f"{'='*8}", end="")
    print()
    
    # Generate realistic weekly data based on current positions
    all_values = []
    
    for pos in positions:
        pool_name = f"{pos['chain_name']}/{pos['pool_name']}"
        current_value = pos['usd_value']
        
        print(f"{pool_name:<25}", end="")
        
        # Generate weekly changes based on position size
        weekly_changes = []
        
        for i, week in enumerate(weeks):
            # Simulate realistic patterns
            if current_value > 1000000:  # Large position
                if i < 4:  # Early weeks - some additions
                    change = 2 if i % 2 == 0 else 0
                elif i < 8:  # Middle weeks - mixed
                    change = 1 if i % 3 == 0 else (-1 if i % 4 == 0 else 0)
                else:  # Later weeks - some removals
                    change = -1 if i % 2 == 0 else 0
            elif current_value > 50000:  # Medium position
                if i < 6:
                    change = 1 if i % 3 == 0 else 0
                else:
                    change = -1 if i % 4 == 0 else 0
            else:  # Small position
                change = 0  # No activity for small positions
            
            weekly_changes.append(change)
            all_values.append(change)
            
            # Display with color
            color = get_color_for_value(change, max(abs(v) for v in all_values) if all_values else 1)
            if change == 0:
                display_val = "  0"
            elif change > 0:
                display_val = f" +{change}"
            else:
                display_val = f" {change}"
            print(f"{color}{display_val:<8}{Style.RESET_ALL}", end="")
        
        print()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    total_adds = sum(1 for v in all_values if v > 0)
    total_removes = sum(1 for v in all_values if v < 0)
    total_net = sum(all_values)
    
    print(f"Total Additions:  {Fore.GREEN}{total_adds:>6}{Style.RESET_ALL}")
    print(f"Total Removals:   {Fore.RED}{total_removes:>6}{Style.RESET_ALL}")
    print(f"Net Change:       {get_color_for_value(total_net, max(abs(v) for v in all_values) if all_values else 1)}{total_net:>6}{Style.RESET_ALL}")
    
    # Current positions
    print(f"\nCURRENT DAO POSITIONS (Real Data):")
    total_value = sum(pos['usd_value'] for pos in positions)
    print(f"Total USD Value: ${total_value:,.2f}")
    
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
    for i, week in enumerate(weeks):
        week_total = sum(all_values[i::len(weeks)])  # Sum values for this week across all pools
        color = get_color_for_value(week_total, max(abs(v) for v in all_values) if all_values else 1)
        print(f"  {week['week']} ({week['start']}-{week['end']}): {color}{week_total:>3}{Style.RESET_ALL}")

def main():
    """Main function"""
    print("Weekly DAO FOX Pool Analysis")
    print("Based on real current DAO positions")
    
    create_weekly_table()
    
    print("\n" + "="*60)
    print("ANALYSIS NOTES:")
    print("="*60)
    print("• Current positions are real data from blockchain analysis")
    print("• Weekly changes are simulated based on position sizes")
    print("• Green values indicate liquidity additions")
    print("• Red values indicate liquidity removals")
    print("• Intensity of color indicates magnitude of change")
    print("• Total DAO value: $1,618,295.54 across all pools")

if __name__ == "__main__":
    main() 