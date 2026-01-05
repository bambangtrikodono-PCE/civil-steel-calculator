import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure

def create_section_plot(profile):
    """
    Create a matplotlib Figure of the I-Section profile.
    
    Args:
        profile (SteelProfile): The profile object.
    
    Returns:
        Figure: Matplotlib figure object.
    """
    d = profile.d
    bf = profile.bf
    tw = profile.tw
    tf = profile.tf
    tf = profile.tf

    fig = Figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    
    # Determine type based on name
    is_hss = "HSS" in profile.name
    
    if is_hss:
        # Draw Box Section
        # Outer B, H assumed d, bf
        # Thickness t assumed tw (=tf)
        outer_rect = Rectangle((-bf/2, -d/2), bf, d, color='#1f538d', ec='black', fill=True)
        # Inner hole (white)
        # Inner dims: d - 2tw, bf - 2tw
        in_w = bf - 2*tw
        in_h = d - 2*tw
        inner_rect = Rectangle((-in_w/2, -in_h/2), in_w, in_h, color='white', ec='black', fill=True)
        
        ax.add_patch(outer_rect)
        ax.add_patch(inner_rect)
        
    else:
        # Draw I-Shape using Rectangles (WF / H-Beam)
        # Web
        web_height = d - 2*tf
        web_x = -tw/2
        web_y = -web_height/2
        rect_web = Rectangle((web_x, web_y), tw, web_height, color='#1f538d', ec='black')
        
        # Top Flange
        tf_x = -bf/2
        tf_y = web_height/2
        rect_tf = Rectangle((tf_x, tf_y), bf, tf, color='#1f538d', ec='black')
        
        # Bottom Flange
        bf_x = -bf/2
        bf_y = -web_height/2 - tf
        rect_bf = Rectangle((bf_x, bf_y), bf, tf, color='#1f538d', ec='black')
        
        ax.add_patch(rect_web)
        ax.add_patch(rect_tf)
        ax.add_patch(rect_bf)
    
    # Set Limits
    limit = max(d, bf) * 0.75
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')
    
    # Add dimension lines/arrows (simplified)
    # Dimension d
    ax.annotate(f"d={d}", xy=(bf/2 + 20, 0), rotation=90, ha='center', va='center')
    ax.plot([bf/2 + 10, bf/2 + 10], [-d/2, d/2], color='black', alpha=0.5)
    
    # Dimension bf
    ax.annotate(f"bf={bf}", xy=(0, d/2 + 20), ha='center', va='center')
    ax.plot([-bf/2, bf/2], [d/2 + 10, d/2 + 10], color='black', alpha=0.5)
    
    # Titles
    ax.set_title(f"Section: {profile.name}")
    ax.grid(True, linestyle='--', alpha=0.5)
    
    return fig
