import pandas as pd
import numpy as np
import plotly.express as px

# Function for creating heatmap
def create_heatmap(detectors, hits):
    # Create a DataFrame
    hodoscope_data = pd.DataFrame(hits, columns=[detector for detector in detectors], index=range(1, len(hits) + 1))

    # Create heatmap
    fig = px.imshow(hodoscope_data.T,
                    labels=dict(x="Hodoscope Slice", y="Detector", color="Hit"),
                    x=hodoscope_data.index,
                    y=hodoscope_data.columns,
                    color_continuous_scale="magenta")

    fig.update_layout(title='Hodoscope Hits by Detector',
                    xaxis_title='Hodoscope Slice',
                    yaxis_title='Detector')
    
    return fig

if __name__ == "__main__":
    # Simulate data
    np.random.seed(0)
    num_detectors = 6
    num_slices = 200
    hits = np.random.randint(0, 2, size=(num_slices, num_detectors))  # 200 hodoscope slices, 6 detectors
    print(hits.shape)

    # Generate figure
    fig = create_heatmap(["Detector {}".format(i+1) for i in range(num_detectors)], hits)

    # Show the figure
    fig.write_image("fig1.png")