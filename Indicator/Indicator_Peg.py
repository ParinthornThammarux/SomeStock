import dearpygui.dearpygui as dpg
import threading
import requests
from bs4 import BeautifulSoup
import time

from utils import constants

# ==================== PEG Ratio Scraper ====================
def fetch_peg_ratio(symbol):
    """
    Fetches the PEG Ratio (5yr expected) for a given stock symbol from Yahoo Finance.
    Includes comprehensive headers and error handling to mimic a browser request.
    """
    url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
    
    headers = {
        'Host': 'finance.yahoo.com',
        'Sec-Ch-Ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Priority': 'u=0, i',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        peg_ratio_value = "N/A" # Default to N/A if not found
        
        # Look for the table row containing "PEG Ratio (5yr expected)"
        # Note: Yahoo Finance HTML structure can change, this might need adjustment
        for tr in soup.find_all('tr'):
            if 'PEG Ratio' in tr.text:
                # Find all <td> tags in the row and get the second one (index 1)
                tds = tr.find_all('td')
                if len(tds) > 1:
                    peg_ratio_value = tds[1].text.strip()
                break
        if constants.DEBUG:
            print(f"🔢 {symbol} - PEG Ratio (fetched): {peg_ratio_value}")
        return peg_ratio_value

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error for {symbol} (Status: {e.response.status_code}): {e}")
        return "Error"
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error for {symbol}: {e}")
        return "Error"
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout error for {symbol}: {e}")
        return "Error"
    except requests.exceptions.RequestException as e:
        print(f"❌ General request error for {symbol}: {e}")
        return "Error"
    except Exception as e:
        print(f"❌ An unexpected error occurred while fetching PEG ratio for {symbol}: {e}")
        return "Error"


# ==================== DPG PEG Ratio Component ====================

def create_peg_table_for_stock(parent_tag, symbol, container_height=100):
    """
    Creates a simple DPG table to display the PEG ratio for a specific stock.
    """
    try:
        print(f"📋 Creating PEG Ratio table for {symbol}")
        
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"peg_table_container_{symbol}_{timestamp}"
        status_tag = f"peg_status_{symbol}_{timestamp}"
        peg_symbol_text_tag = f"peg_symbol_text_{symbol}_{timestamp}"
        peg_ratio_value_tag = f"peg_ratio_value_{symbol}_{timestamp}"

        with dpg.child_window(
            width=-1, 
            height=container_height, 
            border=True, 
            parent=parent_tag,
            tag=chart_container_tag
        ):
            with dpg.group(horizontal=True):
                dpg.add_text(f"PEG Ratio: {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=status_tag, color=[255, 255, 0])
            
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Create a simple table for the PEG ratio
            with dpg.table(
                header_row=True,
                resizable=True,
                borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True,
                tag=f"peg_ratio_table_{symbol}_{timestamp}"
            ):
                dpg.add_table_column(label="Symbol")
                dpg.add_table_column(label="PEG Ratio (5yr expected)")

                with dpg.table_row():
                    dpg.add_text(symbol, tag=peg_symbol_text_tag)
                    dpg.add_text("Fetching...", tag=peg_ratio_value_tag)
        
        # Start fetching and displaying PEG ratio in a separate thread
        thread = threading.Thread(
            target=_fetch_and_display_peg_ratio, 
            args=(symbol, peg_ratio_value_tag, status_tag)
        )
        thread.daemon = True
        thread.start()
        
        return chart_container_tag
        
    except Exception as e:
        print(f"❌ Error creating PEG Ratio table for {symbol}: {e}")
        return None

def _fetch_and_display_peg_ratio(symbol, peg_ratio_value_tag, status_tag):
    """
    Fetches the PEG ratio and updates the DPG table and status.
    """
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Fetching PEG Ratio...")
            dpg.configure_item(status_tag, color=[255, 255, 0]) # Yellow for loading

        peg_ratio = fetch_peg_ratio(symbol)

        if dpg.does_item_exist(peg_ratio_value_tag):
            dpg.set_value(peg_ratio_value_tag, peg_ratio)

        if dpg.does_item_exist(status_tag):
            if peg_ratio and peg_ratio != "N/A" and peg_ratio != "Error":
                dpg.set_value(status_tag, f"PEG Ratio fetched: {peg_ratio}")
                dpg.configure_item(status_tag, color=[0, 255, 0]) # Green for success
            elif peg_ratio == "N/A":
                dpg.set_value(status_tag, "PEG Ratio: N/A")
                dpg.configure_item(status_tag, color=[255, 100, 100]) # Red for not available
            else: # Error case
                dpg.set_value(status_tag, "PEG Ratio: Error fetching")
                dpg.configure_item(status_tag, color=[255, 0, 0]) # Red for error

    except Exception as e:
        print(f"❌ Error in _fetch_and_display_peg_ratio for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 0, 0]) # Red for error