#!/usr/bin/env python3
"""
Master Analysis Runner
Runs all DAO and LP analysis components and displays comprehensive results.
"""

import subprocess
import sys
import os
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

def run_script(script_name: str, description: str) -> bool:
    """Run a script and return success status"""
    print(f"\n{Fore.CYAN}🔄 Running {description}...{Style.RESET_ALL}")
    print(f"Script: {script_name}")
    print("-" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ {description} completed successfully{Style.RESET_ALL}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"{Fore.RED}❌ {description} failed{Style.RESET_ALL}")
            if result.stderr:
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}❌ {description} timed out{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ {description} error: {e}{Style.RESET_ALL}")
        return False

def display_system_summary():
    """Display system summary"""
    print(f"\n{Fore.YELLOW}{'='*80}")
    print("🎯 SHAPESHIFT DAO & LP ANALYSIS SYSTEM")
    print("="*80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System Status: {Fore.GREEN}OPERATIONAL{Style.RESET_ALL}")
    print(f"{'='*80}{Style.RESET_ALL}")

def display_available_scripts():
    """Display available analysis scripts"""
    print(f"\n{Fore.CYAN}📋 AVAILABLE ANALYSIS SCRIPTS:{Style.RESET_ALL}")
    print("-" * 60)
    
    scripts = [
        ("weekly_dao_tracking.py", "DAO Position Tracking", "Real-time DAO treasury position monitoring"),
        ("simple_weekly_display.py", "Weekly Analysis Display", "Color-coded weekly liquidity changes"),
        ("track_changes.py", "Change Tracker", "Historical position change analysis"),
        ("comprehensive_dao_lp_analysis.py", "Comprehensive Analysis", "Complete DAO & LP health metrics"),
        ("dao_lp_combined_analysis.py", "Combined Analysis", "DAO + LP event monitoring"),
        ("analyze_dao_ownership.py", "DAO Ownership", "Current DAO pool ownership analysis")
    ]
    
    for script, name, description in scripts:
        if os.path.exists(script):
            print(f"✅ {name:<25} - {description}")
        else:
            print(f"❌ {name:<25} - {description} (Missing)")

def run_comprehensive_analysis():
    """Run the comprehensive analysis suite"""
    print(f"\n{Fore.YELLOW}🚀 STARTING COMPREHENSIVE ANALYSIS SUITE{Style.RESET_ALL}")
    print("="*80)
    
    # Run core analysis
    success_count = 0
    total_scripts = 3
    
    # 1. DAO Position Tracking
    if run_script("weekly_dao_tracking.py", "DAO Position Tracking"):
        success_count += 1
    
    # 2. Comprehensive Analysis
    if run_script("comprehensive_dao_lp_analysis.py", "Comprehensive Analysis"):
        success_count += 1
    
    # 3. Weekly Display
    if run_script("simple_weekly_display.py", "Weekly Analysis Display"):
        success_count += 1
    
    # Summary
    print(f"\n{Fore.YELLOW}📊 ANALYSIS SUMMARY:{Style.RESET_ALL}")
    print("="*60)
    print(f"Scripts Run: {success_count}/{total_scripts}")
    
    if success_count == total_scripts:
        print(f"{Fore.GREEN}🎉 All analyses completed successfully!{Style.RESET_ALL}")
    elif success_count > 0:
        print(f"{Fore.YELLOW}⚠️  Partial success - {success_count}/{total_scripts} scripts completed{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Analysis failed - no scripts completed successfully{Style.RESET_ALL}")

def display_usage_instructions():
    """Display usage instructions"""
    print(f"\n{Fore.CYAN}📖 USAGE INSTRUCTIONS:{Style.RESET_ALL}")
    print("="*60)
    print("• Run this script to execute all analysis components")
    print("• Individual scripts can be run separately:")
    print("  - python weekly_dao_tracking.py (Real-time DAO positions)")
    print("  - python comprehensive_dao_lp_analysis.py (Health metrics)")
    print("  - python simple_weekly_display.py (Weekly analysis)")
    print("  - python track_changes.py (Historical changes)")
    print("• Databases are automatically created and maintained")
    print("• All data is real-time from blockchain sources")

def main():
    """Main function"""
    display_system_summary()
    display_available_scripts()
    
    print(f"\n{Fore.GREEN}🎯 Ready to run comprehensive analysis...{Style.RESET_ALL}")
    
    # Run the analysis suite
    run_comprehensive_analysis()
    
    # Display usage instructions
    display_usage_instructions()
    
    print(f"\n{Fore.YELLOW}🏁 Analysis complete! Check the results above.{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 