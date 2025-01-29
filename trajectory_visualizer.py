import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
from matplotlib.patches import Polygon


# trajectory_visualizer.py
def create_stadium_trajectory_visualization(df, stadium_name, distance, launch_angle):
    try:
        # Read stadium data
        stadium_df = pd.read_excel("fence_data.xlsx")
        stadium_data = stadium_df[stadium_df['stadium'] == stadium_name]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))

        field_green = '#0B6623'  # Deep forest green
        infield_brown = '#654321'  # Rich brown

        # Create outfield vertices (between foul lines and fence)
        vertices_x = [0]
        vertices_y = [0]
        
        # Add fence points between foul lines
        mask = (np.abs(np.arctan2(stadium_data['x'], stadium_data['y'])) <= np.pi/4)
        vertices_x.extend(stadium_data[mask]['x'].values)
        vertices_y.extend(stadium_data[mask]['y'].values)
        
        # Create outfield polygon
        vertices = np.column_stack((vertices_x, vertices_y))
        outfield = plt.Polygon(vertices, facecolor=field_green, alpha=0.6)
        
        # Create infield circle for masking
        infield_radius = 90
        theta = np.linspace(45, 135, 100)
        infield_x = infield_radius * np.cos(np.radians(theta))
        infield_y = infield_radius * np.sin(np.radians(theta))
        infield_vertices = np.column_stack((infield_x, infield_y))
        infield = plt.Polygon(np.vstack(([0, 0], infield_vertices)), 
                            facecolor=infield_brown, alpha=0.3)
        
        # Add patches in correct order
        ax.add_patch(outfield)  # Add outfield first
        ax.add_patch(infield)   # Add infield on top

        # Plot foul lines
        max_distance = max(abs(df['x'].max()), abs(df['y'].max()), 400)
        ax.plot([0, max_distance * np.cos(np.radians(45))], 
                [0, max_distance * np.sin(np.radians(45))],
                color='black', linestyle='--', linewidth=1.5)
        ax.plot([0, max_distance * np.cos(np.radians(135))], 
                [0, max_distance * np.sin(np.radians(135))],
                color='black', linestyle='--', linewidth=1.5)


        # Plot stadium fence
        if not stadium_data.empty:
            # Bottom of fence
            ax.plot(stadium_data['x'], stadium_data['y'], 'k-', linewidth=2, label='Fence Bottom')
            
            # Top of fence
            fence_top_y = stadium_data['y'] + stadium_data['fence_height']
            ax.plot(stadium_data['x'], fence_top_y, 'r-', linewidth=2, label='Fence Top')
            
            # Fill fence area
            ax.fill_between(stadium_data['x'], stadium_data['y'], fence_top_y,
                          color='gray', alpha=0.3, 
                          where=(abs(np.arctan2(stadium_data['x'], stadium_data['y'])) <= np.pi/4))

            # Add height labels
            for i in range(0, len(stadium_data), max(1, len(stadium_data)//4)):
                if abs(np.arctan2(stadium_data['x'].iloc[i], stadium_data['y'].iloc[i])) <= np.pi/4:
                    ax.annotate(f"{int(stadium_data['fence_height'].iloc[i])}ft",
                              (stadium_data['x'].iloc[i], stadium_data['y'].iloc[i]),
                              xytext=(0, 10), textcoords='offset points',
                              ha='center', va='bottom')


        # Plot trajectory
        ax.plot(df['x'], df['y'], color='red', linewidth=4)
        ax.scatter(df['x'].iloc[-1], df['y'].iloc[-1], color='red', s=100)


        # Set limits and aspect
        ax.set_xlim(-250, 250)
        ax.set_ylim(-50, 500)
        ax.set_aspect('equal')

        # Remove all axes and white space
        ax.axis('off')
        
        # Set title without "- Ball Trajectory"
        ax.set_title(f'{stadium_name}', 
             pad=20,  # Increase padding to move title down
             fontsize=16,  # Increase font size
             y= -0.001)  # Move title below the plot

        
        # Save with tight layout and no extra white space
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', 
                   pad_inches=0, dpi=300)
        buf.seek(0)
        plt.close()

        return buf
    except Exception as e:
        print(f"Error in visualization: {str(e)}")
        return None
