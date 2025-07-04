# utils/stockdex_layer.py

import dearpygui.dearpygui as dpg

from utils import constants

def fetch_data_from_stockdx(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    
    print("=" * 80)
    print(f"🔍 STARTING FIXED DATA FETCH FOR SYMBOL: {symbol}")
    print("=" * 80)
    
    try:
        from stockdex import Ticker
        ticker = Ticker(ticker=symbol)
        df = ticker.yahoo_api_price(range='1d', dataGranularity='5m')
        
        if df is None or df.empty:
            print("❌ No data received")
            return
            
        print(f"✅ Retrieved {len(df)} data points for {symbol}")
        
        # Convert to DPG format
        x_data = list(range(len(df)))
        y_data = df['close'].tolist()
        
        print(f"📋 Converted data - X: {len(x_data)} points, Y: {len(y_data)} points")
        print(f"📋 Y data range: ${min(y_data):.2f} to ${max(y_data):.2f}")
        
        # FIXED: Update DPG chart using stored tags
        print("🎨 FIXED: Updating DPG chart with stored tags...")
        print(f"📋 Line tag: {line_tag}")
        print(f"📋 X-axis tag: {x_axis_tag}")
        print(f"📋 Y-axis tag: {y_axis_tag}")
        print(f"📋 Plot tag: {plot_tag}")
        
        # Check if all required tags exist
        tags_exist = True
        for tag_name, tag_value in [
            ("Line", line_tag),
            ("X-axis", x_axis_tag), 
            ("Y-axis", y_axis_tag),
            ("Plot", plot_tag)
        ]:
            if tag_value is None:
                print(f"❌ {tag_name} tag is None")
                tags_exist = False
            elif not dpg.does_item_exist(tag_value):
                print(f"❌ {tag_name} tag '{tag_value}' does not exist")
                tags_exist = False
            else:
                print(f"✅ {tag_name} tag exists")
        
        if not tags_exist:
            print("❌ Cannot update chart - missing tags")
            return
        
        # Update the line series data
        try:
            print("🔄 Updating line series data...")
            dpg.set_value(line_tag, [x_data, y_data])
            print("✅ Line series data updated successfully")
        except Exception as e:
            print(f"❌ Failed to update line series: {e}")
            return
        
        # Update axis limits using stored tags
        if len(y_data) > 0:
            min_price = min(y_data) * 0.995  # Tighter margins
            max_price = max(y_data) * 1.005
            
            print(f"📋 Setting axis limits:")
            print(f"   X-axis: 0 to {len(x_data)}")
            print(f"   Y-axis: ${min_price:.2f} to ${max_price:.2f}")
            
            try:
                # Update X-axis
                dpg.set_axis_limits(x_axis_tag, 0, len(x_data))
                print("✅ X-axis limits updated")
                
                # Update Y-axis  
                dpg.set_axis_limits(y_axis_tag, min_price, max_price)
                print("✅ Y-axis limits updated")
                
            except Exception as e:
                print(f"❌ Failed to update axis limits: {e}")
        
        # Force plot refresh
        try:
            print("🔄 Forcing plot refresh...")
            # These calls can help force DPG to redraw
            dpg.set_item_width(plot_tag, dpg.get_item_width(plot_tag))
            print("✅ Plot refresh triggered")
        except Exception as e:
            print(f"⚠️ Plot refresh failed (non-critical): {e}")
        
        print(f"✅ Chart update completed for {symbol}")
        print(f"💰 Latest price: ${y_data[-1]:.2f}")
        
    except Exception as e:
        print(f"❌ Error in FIXED fetch function: {e}")
        import traceback
        traceback.print_exc()