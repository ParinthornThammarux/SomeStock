# components/stock_data_manager.py
# Simplified manager that imports from the combined stock_component
import dearpygui as dpg

from components.stock.stock_component import (
    # Data classes
    StockData,
    StockTag,
    
    # Cache functions
    get_cached_stock_data,
    update_stock_data_cache,
    get_stock_data_for_table,
    save_cache_to_file,
    load_cache_from_file,
    cleanup_cache,
    
    # Tag management functions
    create_stock_tag,
    get_all_active_tags,
    get_focused_tag,
    find_tag_by_symbol,
    get_favorited_stocks,
    clear_all_tags,
    refresh_all_tags,
    
    # Constants
    CACHE_DURATION,
    MAX_CACHE_SIZE,
    
    _stock_data_cache
)
from utils import constants

# Add this alias for backward compatibility
stock_data_cache = _stock_data_cache

# Legacy compatibility - these functions maintain the old interface
def add_stock_tag(symbol, company_name, parent="tags_container"):
    """Legacy function - creates stock tag using new API"""
    return create_stock_tag(symbol, company_name, parent)

def get_all_stock_tags():
    """Legacy function - returns all active tags"""
    return get_all_active_tags()

def find_tag_by_name(symbol):
    """Legacy function - finds tag by symbol"""
    return find_tag_by_symbol(symbol)

def remove_from_list(symbol):
    """Legacy function - removes tag from tracking"""
    tag = find_tag_by_symbol(symbol)
    if tag:
        tag.remove()

def get_focused_stock():
    """Legacy function - returns focused stock symbol"""
    focused_tag = get_focused_tag()
    return focused_tag.symbol if focused_tag else None

def restore_tags_to_container(container_tag="tags_container"):
    """Restore all active tags to the specified container by recreating them"""
    try:
        # Get current active tags data
        active_tags = get_all_active_tags().copy()  # Make a copy
        tag_data = []
        
        # Store the data from existing tags
        for tag in active_tags:
            tag_data.append({
                'symbol': tag.symbol,
                'company_name': tag.company_name,
                'is_favorited': tag.is_favorited,
                'stock_data': tag.stock_data
            })
        
        # Clear all existing tags
        clear_all_tags()
        
        # Recreate tags in the new container
        for data in tag_data:
            try:
                # Create new tag
                new_tag = create_stock_tag(
                    symbol=data['symbol'],
                    company_name=data['company_name'],
                    parent=container_tag
                )
                
                if new_tag:
                    # Restore state
                    new_tag.is_favorited = data['is_favorited']
                    new_tag.stock_data = data['stock_data']
                    
                    # Update heart icon if favorited
                    if new_tag.is_favorited:
                        if dpg.does_item_exist(f"{new_tag.tag_id}_heart"):
                            dpg.set_item_label(f"{new_tag.tag_id}_heart", constants.ICON_HEART)
                    
                    new_tag.set_focus(False)  # Don't auto-focus
                    
            except Exception as e:
                print(f"❌ Error recreating tag {data['symbol']}: {e}")
        if constants.DEBUG:
            print(f"✅ Restored {len(tag_data)} tags to {container_tag}")
        
    except Exception as e:
        print(f"❌ Error in restore_tags_to_container: {e}")
    
# Re-export for convenience
__all__ = [
    'StockData',
    'StockTag',
    'create_stock_tag',
    'add_stock_tag',  # Legacy
    'get_all_active_tags',
    'get_all_stock_tags',  # Legacy
    'get_focused_tag',
    'get_focused_stock',  # Legacy
    'find_tag_by_symbol',
    'find_tag_by_name',  # Legacy
    'get_favorited_stocks',
    'clear_all_tags',
    'refresh_all_tags',
    'get_cached_stock_data',
    'update_stock_data_cache',
    'get_stock_data_for_table',
    'save_cache_to_file',
    'load_cache_from_file',
    'stock_data_cache',
    'cleanup_cache',
    'CACHE_DURATION',
    'MAX_CACHE_SIZE'
]