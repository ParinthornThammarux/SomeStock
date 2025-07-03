import random

# Vibrant colors for text
VIBRANT_COLORS = [
    [255, 99, 132],   # Pink Red
    [54, 162, 235],   # Blue
    [255, 205, 86],   # Yellow
    [75, 192, 192],   # Turquoise
    [153, 102, 255],  # Purple
    [255, 159, 64],   # Orange
    [199, 199, 199],  # Grey
    [83, 102, 255],   # Light Blue
    [255, 99, 255],   # Magenta
    [99, 255, 132],   # Light Green
    [255, 132, 99],   # Coral
    [132, 99, 255],   # Lavender
    [99, 255, 255],   # Aqua
    [255, 255, 99],   # Light Yellow
    [255, 99, 99],    # Light Red
    [99, 99, 255],    # Periwinkle
    [255, 180, 99],   # Peach
    [180, 255, 99],   # Lime Green
    [99, 180, 255],   # Sky Blue
    [255, 99, 180]    # Hot Pink
]

# Matching subtle backgrounds (20-30% opacity of vibrant colors)
SUBTLE_BACKGROUNDS = [
    [255, 229, 235],  # Subtle Pink Red
    [214, 235, 255],  # Subtle Blue
    [255, 248, 220],  # Subtle Yellow
    [218, 245, 245],  # Subtle Turquoise
    [239, 230, 255],  # Subtle Purple
    [255, 238, 218],  # Subtle Orange
    [245, 245, 245],  # Subtle Grey
    [226, 230, 255],  # Subtle Light Blue
    [255, 229, 255],  # Subtle Magenta
    [229, 255, 235],  # Subtle Light Green
    [255, 235, 229],  # Subtle Coral
    [235, 229, 255],  # Subtle Lavender
    [229, 255, 255],  # Subtle Aqua
    [255, 255, 229],  # Subtle Light Yellow
    [255, 229, 229],  # Subtle Light Red
    [229, 229, 255],  # Subtle Periwinkle
    [255, 243, 229],  # Subtle Peach
    [243, 255, 229],  # Subtle Lime Green
    [229, 243, 255],  # Subtle Sky Blue
    [255, 229, 243]   # Subtle Hot Pink
]

# Color pairs: [text_color, background_color]
COLOR_PAIRS = [
    [[255, 99, 132], [255, 229, 235]],    # Pink Red
    [[54, 162, 235], [214, 235, 255]],    # Blue
    [[255, 205, 86], [255, 248, 220]],    # Yellow
    [[75, 192, 192], [218, 245, 245]],    # Turquoise
    [[153, 102, 255], [239, 230, 255]],   # Purple
    [[255, 159, 64], [255, 238, 218]],    # Orange
    [[199, 199, 199], [245, 245, 245]],   # Grey
    [[83, 102, 255], [226, 230, 255]],    # Light Blue
    [[255, 99, 255], [255, 229, 255]],    # Magenta
    [[99, 255, 132], [229, 255, 235]],    # Light Green
    [[255, 132, 99], [255, 235, 229]],    # Coral
    [[132, 99, 255], [235, 229, 255]],    # Lavender
    [[99, 255, 255], [229, 255, 255]],    # Aqua
    [[255, 255, 99], [255, 255, 229]],    # Light Yellow
    [[255, 99, 99], [255, 229, 229]],     # Light Red
    [[99, 99, 255], [229, 229, 255]],     # Periwinkle
    [[255, 180, 99], [255, 243, 229]],    # Peach
    [[180, 255, 99], [243, 255, 229]],    # Lime Green
    [[99, 180, 255], [229, 243, 255]],    # Sky Blue
    [[255, 99, 180], [255, 229, 243]]     # Hot Pink
]

def get_random_color_pair():
    """Get a random color pair [text_color, background_color]"""
    return random.choice(COLOR_PAIRS)

def get_color_pair_by_index(index):
    """Get color pair by index, cycles through if index exceeds length"""
    return COLOR_PAIRS[index % len(COLOR_PAIRS)]

def get_color_pair_by_stock(stock_name):
    """Get consistent color pair based on stock name hash"""
    hash_value = hash(stock_name) % len(COLOR_PAIRS)
    return COLOR_PAIRS[hash_value]

def normalize_color_pair_for_dpg(color_pair):
    """Convert color pair to DPG format [0-1]"""
    text_color, bg_color = color_pair
    return [
        [c / 255.0 for c in text_color],      # Normalized text color
        [c / 255.0 for c in bg_color]         # Normalized background color
    ]

# Example usage functions
def demo_color_pairs():
    """Demonstrate all color pairs"""
    print("Stock Tag Color Pairs:")
    print("-" * 60)
    
    color_names = [
        "Pink Red", "Blue", "Yellow", "Turquoise", "Purple", "Orange", "Grey",
        "Light Blue", "Magenta", "Light Green", "Coral", "Lavender", "Aqua",
        "Light Yellow", "Light Red", "Periwinkle", "Peach", "Lime Green", 
        "Sky Blue", "Hot Pink"
    ]
    
    for i, (text_color, bg_color) in enumerate(COLOR_PAIRS):
        name = color_names[i]
        print(f"{i+1:2d}. {name:12} | Text: {text_color} | BG: {bg_color}")

def test_random_selection():
    """Test random color selection"""
    print("\nRandom Color Pairs:")
    print("-" * 40)
    
    for i in range(5):
        text_color, bg_color = get_random_color_pair()
        print(f"Random {i+1}: Text {text_color}, BG {bg_color}")

def test_stock_consistency():
    """Test consistent color assignment by stock name"""
    print("\nConsistent Stock Colors:")
    print("-" * 40)
    
    stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    for stock in stocks:
        text_color, bg_color = get_color_pair_by_stock(stock)
        print(f"{stock}: Text {text_color}, BG {bg_color}")
        
        # Test consistency
        text_color2, bg_color2 = get_color_pair_by_stock(stock)
        consistent = text_color == text_color2 and bg_color == bg_color2
        print(f"  Consistent: {consistent}")

if __name__ == "__main__":
    demo_color_pairs()
    test_random_selection()
    test_stock_consistency()
    
    # Example for DPG usage
    print("\nDPG Usage Example:")
    text_color, bg_color = get_random_color_pair()
    dpg_text, dpg_bg = normalize_color_pair_for_dpg([text_color, bg_color])
    print(f"Original: Text {text_color}, BG {bg_color}")
    print(f"DPG: Text {dpg_text}, BG {dpg_bg}")
    
    # Easy unpacking example
    print("\nEasy Usage:")
    text, bg = get_color_pair_by_stock("AAPL")
    print(f"AAPL colors - Text: {text}, Background: {bg}")