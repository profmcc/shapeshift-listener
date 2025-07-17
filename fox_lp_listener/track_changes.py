#!/usr/bin/env python3
"""
DAO Position Change Tracker
Tracks actual changes in DAO positions over time.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init(autoreset=True)

def get_position_history():
    """Get position history from database"""
    conn = sqlite3.connect('fox_pools_analysis.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT chain_name, pool_name, dao_usd_value, timestamp
        FROM dao_position_history
        ORDER BY timestamp DESC
    ''')
    
    data = cursor.fetchall()
    conn.close()
    
    return data

def analyze_changes():
    """Analyze position changes over time"""
    data = get_position_history()
    
    if len(data) < 2:
        print("Need at least 2 data points to analyze changes.")
        print("Run weekly_dao_tracking.py multiple times to build history.")
        return
    
    # Group by pool
    pools = {}
    for row in data:
        chain_name, pool_name, usd_value, timestamp = row
        pool_key = f"{chain_name}/{pool_name}"
        
        if pool_key not in pools:
            pools[pool_key] = []
        
        pools[pool_key].append({
            'usd_value': usd_value,
            'timestamp': timestamp
        })
    
    # Calculate changes for each pool
    changes = []
    for pool_key, history in pools.items():
        if len(history) >= 2:
            # Sort by timestamp
            history.sort(key=lambda x: x['timestamp'])
            
            # Calculate change
            old_value = history[0]['usd_value']
            new_value = history[-1]['usd_value']
            change = new_value - old_value
            change_pct = (change / old_value * 100) if old_value > 0 else 0
            
            changes.append({
                'pool': pool_key,
                'old_value': old_value,
                'new_value': new_value,
                'change': change,
                'change_pct': change_pct,
                'old_timestamp': history[0]['timestamp'],
                'new_timestamp': history[-1]['timestamp']
            })
    
    return changes

def get_color_for_change(change: float, max_abs_change: float) -> str:
    """Get color based on change value"""
    if change == 0:
        return Style.RESET_ALL
    
    intensity = min(abs(change) / max_abs_change, 1.0) if max_abs_change > 0 else 0
    
    if change > 0:
        # Green gradient for increases
        if intensity < 0.3:
            return Fore.GREEN
        elif intensity < 0.7:
            return Fore.GREEN + Style.BRIGHT
        else:
            return Back.GREEN + Fore.WHITE + Style.BRIGHT
    else:
        # Red gradient for decreases
        if intensity < 0.3:
            return Fore.RED
        elif intensity < 0.7:
            return Fore.RED + Style.BRIGHT
        else:
            return Back.RED + Fore.WHITE + Style.BRIGHT

def display_changes(changes):
    """Display position changes with color coding"""
    if not changes:
        print("No position changes detected.")
        return
    
    # Calculate max change for color intensity
    max_abs_change = max(abs(c['change']) for c in changes) if changes else 1
    
    print("\n" + "="*100)
    print("DAO POSITION CHANGES (Real Data)")
    print("(Green = Increases, Red = Decreases)")
    print("="*100)
    
    print(f"{'Pool':<30} {'Old Value':<15} {'New Value':<15} {'Change':<12} {'% Change':<10}")
    print("="*100)
    
    for change in changes:
        color = get_color_for_change(change['change'], max_abs_change)
        
        old_val = f"${change['old_value']:,.2f}"
        new_val = f"${change['new_value']:,.2f}"
        change_val = f"${change['change']:+,.2f}"
        pct_val = f"{change['change_pct']:+.2f}%"
        
        print(f"{change['pool']:<30} {old_val:<15} {new_val:<15} {color}{change_val:<12}{Style.RESET_ALL} {color}{pct_val:<10}{Style.RESET_ALL}")

def show_current_positions():
    """Show current positions"""
    data = get_position_history()
    
    if not data:
        print("No position data found.")
        return
    
    # Get latest positions
    latest = {}
    for row in data:
        chain_name, pool_name, usd_value, timestamp = row
        pool_key = f"{chain_name}/{pool_name}"
        
        if pool_key not in latest:
            latest[pool_key] = {
                'chain_name': chain_name,
                'pool_name': pool_name,
                'usd_value': usd_value,
                'timestamp': timestamp
            }
    
    print("\n" + "="*60)
    print("CURRENT DAO POSITIONS")
    print("="*60)
    
    total_value = sum(pos['usd_value'] for pos in latest.values())
    print(f"Total USD Value: ${total_value:,.2f}")
    
    for pool_key, pos in latest.items():
        print(f"  {pool_key}: ${pos['usd_value']:,.2f}")

def main():
    """Main function"""
    print("DAO Position Change Tracker")
    print("Analyzing real position changes over time")
    
    # Show current positions
    show_current_positions()
    
    # Analyze and display changes
    changes = analyze_changes()
    display_changes(changes)
    
    print("\n" + "="*60)
    print("TRACKING NOTES:")
    print("="*60)
    print("• Run 'python weekly_dao_tracking.py' regularly to build history")
    print("• This will track actual changes in DAO positions over time")
    print("• Changes are based on real blockchain data")
    print("• Green indicates position increases")
    print("• Red indicates position decreases")

if __name__ == "__main__":
    main() 