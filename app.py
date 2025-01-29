import streamlit as st
import pandas as pd
from trajectory_calculator import hit_trajectory_calculator
from trajectory_visualizer import create_stadium_trajectory_visualization

def main():
    st.title('Baseball Trajectory Calculator')
    
    try:
        stadium_df = pd.read_excel("fence_data.xlsx")
        available_stadiums = sorted(stadium_df['stadium'].unique())
    except Exception as e:
        st.error(f"Error loading stadium data: {str(e)}")
        return

    st.sidebar.header('Trajectory Parameters')

    selected_stadium = st.sidebar.selectbox(
        'Select Stadium',
        available_stadiums,
        index=0
    )

    # Input parameters
    exit_speed = st.sidebar.slider('Exit Speed (mph)', 60, 120, 95)
    launch_angle = st.sidebar.slider('Launch Angle (degrees)', 0, 50, 25)
    direction = st.sidebar.slider('Direction (degrees)', -45, 45, 0)
    batter_side = st.sidebar.radio('Batter Side', ['Left', 'Right'])

    # Initial position
    x0, y0, z0 = 0, 0, 0

    if st.sidebar.button('Calculate Trajectory'):
        try:
            sign = -1 if batter_side == 'Left' else 1
            df, distance = hit_trajectory_calculator(x0, y0, z0, exit_speed, launch_angle, direction, sign)
            plot_buffer = create_stadium_trajectory_visualization(df, selected_stadium, distance, launch_angle)

            if plot_buffer:
                st.image(plot_buffer)

                # Display key metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Proj Distance", f"{distance:.1f} ft")
                col2.metric("Exit Velocity", f"{exit_speed} mph")
                col3.metric("Launch Angle", f"{launch_angle}°")
            else:
                st.error("Failed to create visualization")

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    main()
