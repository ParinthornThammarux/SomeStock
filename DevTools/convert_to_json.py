import pandas as pd
import json

def excel_to_json(excel_file_path, output_json_path):
    """
    Convert Excel file with stock data to JSON format
    """
    try:
        # Read Excel file
        print(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Display basic info
        print(f"Loaded {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Convert to list of dictionaries
        stock_data = []
        for _, row in df.iterrows():
            stock_info = {
                "symbol": str(row['Symbol']).strip(),
                "company_name": str(row['Company Name']).strip(),
                "industry": str(row['Industry']).strip(),
                "market_cap": str(row['Market Cap']).strip()
            }
            stock_data.append(stock_info)
        
        # Create search-optimized structure
        search_data = {}
        
        # Group by symbol prefixes for fast search
        for stock in stock_data:
            symbol = stock['symbol'].upper()
            
            # Create entries for each prefix (A, AA, AAA, etc.)
            for i in range(1, len(symbol) + 1):
                prefix = symbol[:i]
                
                if prefix not in search_data:
                    search_data[prefix] = []
                
                # Add stock to this prefix (avoid duplicates)
                if stock not in search_data[prefix]:
                    search_data[prefix].append(stock)
        
        # Create final JSON structure
        output_data = {
            "metadata": {
                "total_stocks": len(stock_data),
                "prefixes": len(search_data),
                "source": excel_file_path
            },
            "stocks": stock_data,
            "search_index": search_data
        }
        
        # Save to JSON file
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Successfully converted to JSON!")
        print(f"📁 Output file: {output_json_path}")
        print(f"📊 Total stocks: {len(stock_data)}")
        print(f"🔍 Search prefixes: {len(search_data)}")
        
        # Show some example prefixes
        print(f"\nExample prefixes:")
        for prefix in list(search_data.keys())[:10]:
            count = len(search_data[prefix])
            print(f"  '{prefix}': {count} stocks")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_search_json(json_file_path, search_term):
    """
    Test the search functionality
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        search_index = data['search_index']
        search_term = search_term.upper()
        
        if search_term in search_index:
            results = search_index[search_term]
            print(f"\n🔍 Search results for '{search_term}' ({len(results)} found):")
            for stock in results[:10]:  # Show first 10
                print(f"  {stock['symbol']} - {stock['company_name']}")
        else:
            print(f"\n❌ No results found for '{search_term}'")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

if __name__ == "__main__":
    # Configuration
    EXCEL_FILE = "Stock_Symbols.xlsx"  # Change this to your Excel file path
    JSON_FILE = "stock_data.json"
    
    # Convert Excel to JSON
    excel_to_json(EXCEL_FILE, JSON_FILE)
    
    # Test searches
    print("\n" + "="*50)
    print("TESTING SEARCH FUNCTIONALITY")
    print("="*50)
    
    test_searches = ["A", "AA", "APP", "GOOG", "MICRO"]
    for search_term in test_searches:
        test_search_json(JSON_FILE, search_term)