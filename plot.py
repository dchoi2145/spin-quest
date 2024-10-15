import pandas as pd
import numpy as np
import plotly.express as px

# Simulate data
np.random.seed(0)
hits = np.random.randint(0, 2, size=(200, 6))  # 200 hodoscope slices, 6 detectors

# Create a DataFrame
detector_ids = [1, 2, 3, 4, 5, 6]
hodoscope_data = pd.DataFrame(hits, columns=[f'Detector_{id}' for id in detector_ids], index=range(1, 201))

# Create heatmap
fig = px.imshow(hodoscope_data.T,
                labels=dict(x="Hodoscope Slice", y="Detector", color="Hit"),
                x=hodoscope_data.index,
                y=hodoscope_data.columns,
                color_continuous_scale="magenta")

fig.update_layout(title='Hodoscope Hits by Detector',
                  xaxis_title='Hodoscope Slice',
                  yaxis_title='Detector')

# Show the figure
fig.write_image("fig1.png")