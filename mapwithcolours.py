import pandas as pd
import folium
import numpy as np
import random

# Function to generate a random color
def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# Step 4: Define bins for Emissions
bins = [0, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 5000, 6000, 10000, np.inf]
emission_labels = ['0-200', '201-400', '401-600', '601-800', '801-1000',
                   '1001-2000', '2001-3000', '3001-4000', '4001-5000',
                   '5001-6000', '6001-10000', '10000+']

# Create a feature group for each emissions bin
emissions_layers = {label: folium.FeatureGroup(name=f'Emissions: {label}') for label in emission_labels}

# Example Data Loading
file_list = ['hospitals_ll.csv', 'otherconsumers_ll.csv', 'otherindustries_ll.csv','powerproducers_ll.csv','waste_ll.csv','watertreatment_ll.csv']  # Add all n CSV file names here

# Dictionary to hold sector colors
sector_colors = {}

# Loop through each file to create layers and determine sector colors
for i, file_name in enumerate(file_list):
    data = pd.read_csv(file_name)

    # Update sector for hospitals
    if 'hospitals_ll' in file_name:
        data['Sector'] = 'Hospital'

    # Check and create emissions bins
    data['Emissions_Bin'] = pd.cut(data[' Emission '], bins=bins, labels=emission_labels, include_lowest=True)

    # Extract unique sectors from the data and assign a random color if not already assigned
    for sector in data['Sector'].unique():
        if sector not in sector_colors:
            sector_colors[sector] = random_color()  # Assign a random color

    # Adding markers to respective feature groups
    for idx, row in data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        emissions_bin = row['Emissions_Bin']
        sector = row['Sector']
        
        # Get the color for the sector
        marker_color = sector_colors.get(sector, 'gray')  # Default to gray if sector not found
        
        # Add marker to the appropriate emissions bin layer
        if emissions_bin in emissions_layers:
            folium.Marker(
                location=[lat, lon],
                popup=f"Operator: {row['Operator']}<br>Sector: {sector}<br>Region: {row['Region']}<br>Emissions: {row[' Emission ']}",
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(emissions_layers[emissions_bin])

# Example: Add all emissions layers to the map
m = folium.Map(location=[52.9375, -1.7201], zoom_start=6)  # Initial location and zoom level
for emissions_bin, layer in emissions_layers.items():
    layer.add_to(m)

# Save the map to an HTML file
m.save("map.html")
