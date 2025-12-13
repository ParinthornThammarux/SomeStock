"""
Test script to verify fetch_stock_data signature
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.data_fetch import fetch_stock_data

# Test 1: positional symbol, keyword args
print("Test 1: Positional symbol, keyword period and interval")
try:
    result = fetch_stock_data("AAPL", period="1mo", interval="1d")
    print(f"✅ Success: {type(result)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: all positional
print("\nTest 2: All positional")
try:
    result = fetch_stock_data("AAPL", "1mo", "1d")
    print(f"✅ Success: {type(result)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: all keyword
print("\nTest 3: All keyword")
try:
    result = fetch_stock_data(symbol="AAPL", period="1mo", interval="1d")
    print(f"✅ Success: {type(result)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: defaults
print("\nTest 4: Symbol only with defaults")
try:
    result = fetch_stock_data("AAPL")
    print(f"✅ Success: {type(result)}")
except Exception as e:
    print(f"❌ Error: {e}")
