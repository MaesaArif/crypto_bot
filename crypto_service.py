import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge
import os

# https://alternative.me/crypto/fear-and-greed-index/
def fear_and_greed():
    """Fetches the latest Fear and Greed Index data."""
    url = "https://api.alternative.me/fng/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and "data" in data and len(data["data"]) > 0:
            return data["data"][0], None
        return None, "No data found in API response."
        
    except Exception as e:
        return None, str(e)

def get_fng_emoji_bar(value):
    """Creates a text-based emoji bar for the Fear and Greed value."""
    # Scale: 0 (Green) -> 100 (Orange) as requested
    # We'll use 10 segments
    try:
        val = int(value)
    except:
        val = 50
    
    segments = 10
    filled = round((val / 100) * segments)
    
    # Gradient: Green (at 0) -> Orange (at 100)
    # 0-3: Green, 4-6: Yellow, 7-10: Orange
    bar = ""
    for i in range(segments):
        if i < filled:
            if i < 4:
                bar += "🟩"
            elif i < 7:
                bar += "🟨"
            else:
                bar += "🟧"
        else:
            bar += "⬛"
    
    return bar

def create_fng_gauge(value, title="Fear & Greed Index", output_path="output/fng_gauge.png"):
    """Creates a speedometer-style gauge image."""
    try:
        val = int(value)
    except:
        val = 50

    # Create figure
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={'aspect': 'equal'})
    
    # Gauge parameters
    # Matplotlib angles: 0 is East, 90 is North, 180 is West.
    # Speedometer: 180 (Left) to 0 (Right)
    start_angle = 180
    end_angle = 0
    
    # Create the background arc (gradient)
    # User requested: Green at 0, Orange at 100
    colors = ['#2ecc71', '#f1c40f', '#e67e22'] # Green, Yellow, Orange
    
    # Draw segments
    ax.add_patch(Wedge((0, 0), 1, 120, 180, color=colors[0], alpha=0.3)) # Green
    ax.add_patch(Wedge((0, 0), 1, 60, 120, color=colors[1], alpha=0.3))  # Yellow
    ax.add_patch(Wedge((0, 0), 1, 0, 60, color=colors[2], alpha=0.3))   # Orange
    
    # Draw the needle
    # Value 0 -> 180 degrees, Value 100 -> 0 degrees
    needle_angle = 180 - (val * 1.8)
    needle_rad = np.deg2rad(needle_angle)
    
    ax.annotate("", xy=(0.8 * np.cos(needle_rad), 0.8 * np.sin(needle_rad)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="wedge,tail_width=0.5", color="black", lw=2))
    
    # Center circle
    ax.add_patch(plt.Circle((0, 0), 0.05, color="black"))
    
    # Labels
    ax.text(0, -0.2, f"{val}", horizontalalignment='center', verticalalignment='center', 
            fontsize=24, fontweight='bold')
    ax.text(0, -0.4, title, horizontalalignment='center', verticalalignment='center', 
            fontsize=14)
    
    # Min/Max labels
    ax.text(-1.1, 0, "0", horizontalalignment='center', verticalalignment='center')
    ax.text(1.1, 0, "100", horizontalalignment='center', verticalalignment='center')
    
    # Cleanup
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.6, 1.2)
    ax.axis('off')
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, transparent=True, bbox_inches='tight')
    plt.close()
    
    return output_path
