# utils/matplotlib_integration.py

import dearpygui.dearpygui as dpg
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import io
from PIL import Image
import base64
import tempfile
import os

class DPGMatplotlibIntegration:
    """Helper class to integrate matplotlib plots into DearPyGUI"""
    
    def __init__(self):
        self.temp_files = []
    
    def create_pandas_timeframe_chart(self, df, parent_tag, width=800, height=400):
        """
        Create a pandas timeframe chart and display it in DPG
        """
        # Set matplotlib to use a non-interactive backend
        plt.switch_backend('Agg')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Example pandas timeframe plot
        if 'date' in df.columns and 'price' in df.columns:
            df.set_index('date')['price'].plot(ax=ax, kind='line')
        else:
            # Fallback demo data
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            prices = np.cumsum(np.random.randn(100)) + 100
            demo_df = pd.DataFrame({'price': prices}, index=dates)
            demo_df['price'].plot(ax=ax, kind='line')
        
        ax.set_title('Stock Price Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.grid(True, alpha=0.3)
        
        # Save to temporary file
        temp_path = self._save_plot_to_temp(fig)
        plt.close(fig)
        
        # Load and display in DPG
        self._display_image_in_dpg(temp_path, parent_tag, f"timeframe_chart_{len(self.temp_files)}")
        
        return temp_path
    
    def create_sankey_chart(self, parent_tag, width=800, height=600):
        """
        Create a Sankey chart using plotly and display it in DPG
        Note: This creates a static image of the Sankey chart
        """
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = ["Revenue", "Operating Expenses", "COGS", "Net Income", "Taxes", "Other"],
                color = ["blue", "red", "orange", "green", "purple", "brown"]
            ),
            link = dict(
                source = [0, 0, 1, 1, 1], # indices correspond to labels
                target = [1, 2, 3, 4, 5],
                value = [100, 200, 50, 30, 20]
            )
        )])
        
        fig.update_layout(
            title_text="Cash Flow Sankey Diagram", 
            font_size=10,
            width=width,
            height=height
        )
        
        # Save as static image
        temp_path = self._save_plotly_to_temp(fig, width, height)
        
        # Display in DPG
        self._display_image_in_dpg(temp_path, parent_tag, f"sankey_chart_{len(self.temp_files)}")
        
        return temp_path
    
    def create_advanced_pandas_chart(self, parent_tag, width=800, height=600):
        """
        Create advanced pandas visualizations
        """
        plt.switch_backend('Agg')
        
        # Create sample financial data
        dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
        np.random.seed(42)
        
        # Generate realistic stock data
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        volume = np.random.lognormal(10, 1, len(dates))
        
        df = pd.DataFrame({
            'price': prices,
            'volume': volume,
            'returns': returns
        }, index=dates)
        
        # Create subplot with multiple charts
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(width/100, height/100), dpi=100)
        
        # Price chart with moving averages
        df['price'].plot(ax=ax1, label='Price', alpha=0.7)
        df['price'].rolling(20).mean().plot(ax=ax1, label='20-day MA', alpha=0.8)
        df['price'].rolling(50).mean().plot(ax=ax1, label='50-day MA', alpha=0.8)
        ax1.set_title('Price with Moving Averages')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume chart
        ax2.bar(df.index, df['volume'], alpha=0.6, width=1)
        ax2.set_title('Trading Volume')
        ax2.set_ylabel('Volume')
        
        # Returns histogram
        ax3.hist(df['returns'], bins=50, alpha=0.7, edgecolor='black')
        ax3.set_title('Daily Returns Distribution')
        ax3.set_xlabel('Returns')
        ax3.set_ylabel('Frequency')
        
        # Rolling volatility
        rolling_vol = df['returns'].rolling(30).std() * np.sqrt(252)
        rolling_vol.plot(ax=ax4)
        ax4.set_title('30-day Rolling Volatility (Annualized)')
        ax4.set_ylabel('Volatility')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save and display
        temp_path = self._save_plot_to_temp(fig)
        plt.close(fig)
        
        self._display_image_in_dpg(temp_path, parent_tag, f"advanced_pandas_{len(self.temp_files)}")
        
        return temp_path
    
    def _save_plot_to_temp(self, fig):
        """Save matplotlib figure to temporary file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fig.savefig(temp_file.name, dpi=100, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def _save_plotly_to_temp(self, fig, width, height):
        """Save plotly figure to temporary file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        
        # Save plotly figure as static image
        fig.write_image(temp_file.name, width=width, height=height, engine="kaleido")
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def _display_image_in_dpg(self, image_path, parent_tag, image_tag):
        """Load and display image in DearPyGUI"""
        try:
            # Load image
            width, height, channels, data = dpg.load_image(image_path)
            
            # Create texture
            texture_tag = f"texture_{image_tag}"
            if dpg.does_item_exist(texture_tag):
                dpg.delete_item(texture_tag)
            
            with dpg.texture_registry():
                dpg.add_static_texture(width=width, height=height, 
                                     default_value=data, tag=texture_tag)
            
            # Display image
            if dpg.does_item_exist(image_tag):
                dpg.delete_item(image_tag)
            
            dpg.add_image(texture_tag, parent=parent_tag, tag=image_tag)
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            dpg.add_text(f"Error loading chart: {e}", parent=parent_tag, color=[255, 0, 0])
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Error cleaning up {temp_file}: {e}")
        self.temp_files = []

# Example usage functions
def create_stock_analysis_page(parent_tag):
    """Create a comprehensive stock analysis page with multiple chart types"""
    
    matplotlib_helper = DPGMatplotlibIntegration()
    
    dpg.add_text("Advanced Stock Analysis Dashboard", parent=parent_tag, color=[255, 255, 255])
    dpg.add_separator(parent=parent_tag)
    dpg.add_spacer(height=10, parent=parent_tag)
    
    # Pandas timeframe chart
    dpg.add_text("Price Analysis with Moving Averages", parent=parent_tag, color=[200, 200, 255])
    matplotlib_helper.create_advanced_pandas_chart(parent_tag, width=1000, height=600)
    
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Sankey chart
    dpg.add_text("Cash Flow Analysis", parent=parent_tag, color=[200, 255, 200])
    matplotlib_helper.create_sankey_chart(parent_tag, width=800, height=400)
    
    # Store helper for cleanup
    if not hasattr(dpg, '_matplotlib_helpers'):
        dpg._matplotlib_helpers = []
    dpg._matplotlib_helpers.append(matplotlib_helper)
    
    # Cleanup button
    dpg.add_spacer(height=20, parent=parent_tag)
    dpg.add_button(label="Refresh Charts", 
                  callback=lambda: refresh_charts(parent_tag),
                  parent=parent_tag)

def refresh_charts(parent_tag):
    """Refresh all charts on the page"""
    # Clear existing content
    dpg.delete_item(parent_tag, children_only=True)
    
    # Recreate charts
    create_stock_analysis_page(parent_tag)