#!/bin/bash

# THORChain Data Consolidator Runner
# This script runs the Python consolidator to process viewblock data files

echo "🚀 THORChain Data Consolidator"
echo "================================"

# Check if we're in the right directory
if [ ! -f "thorchain_data_consolidator_fixed.py" ]; then
    echo "❌ Error: Please run this script from the scripts directory"
    echo "   cd scripts"
    echo "   ./consolidate_thorchain.sh"
    exit 1
fi

# Run the consolidator
echo "🔄 Running consolidation..."
python thorchain_data_consolidator_fixed.py

echo ""
echo "✅ Consolidation complete!"
echo ""
echo "To view database statistics only:"
echo "  python thorchain_data_consolidator_fixed.py --stats"
echo ""
echo "To force reprocessing of all files:"
echo "  python thorchain_data_consolidator_fixed.py --force"
