import pandas as pd
import folium
import numpy as np

# Step 4: Define bins for Emissions
bins = [0, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 5000, 6000, 10000, np.inf]
emission_labels = ['0-200', '201-400', '401-600', '601-800', '801-1000',
                   '1001-2000', '2001-3000', '3001-4000', '4001-5000',
                   '5001-6000', '6001-10000', '10000+']

# Predefined colors for sectors (you can adjust these colors)
predefined_colors = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
    'beige', 'darkblue', 'darkgreen', 'lightgreen', 'cadetblue', 
    'violet', 'black', 'lightgray', 'pink', 'lightblue'
]

# New file list
file_list = [
    'hospitals_ll.csv', 
    'otherconsumers_ll.csv', 
    'otherindustries_ll.csv',
    'powerproducers_ll.csv',
    'waste_ll.csv',
    'watertreatment_ll.csv'
]

# Create dictionaries to hold feature groups for emissions and sectors
emissions_layers = {label: folium.FeatureGroup(name=f'Emissions: {label}') for label in emission_labels}
sector_layers = {}  # Initialize empty dict to hold sector layers

# Loop through each file to create layers and determine sector colors
sector_colors = {}
for file_name in file_list:
    data = pd.read_csv(file_name)

    # Update sector for hospitals
    if 'hospitals_ll' in file_name:
        data['Sector'] = 'Hospital'

    # Check and create emissions bins
    data['Emission_Bin'] = pd.cut(data[' Emission '], bins=bins, labels=emission_labels, include_lowest=True)

    # Extract unique sectors from the data and assign a color from predefined_colors
    for sector in data['Sector'].unique():
        if sector not in sector_colors:
            # Assign color in a round-robin manner, ensuring each sector has a unique color
            sector_colors[sector] = predefined_colors[len(sector_colors) % len(predefined_colors)]
            sector_layers[sector] = folium.FeatureGroup(name=sector)  # Create a layer for the sector

    # Add markers to respective emissions and sector groups
    for idx, row in data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        emission_bin = row['Emission_Bin']
        sector = row['Sector']
        
        # Get the color for the sector
        marker_color = sector_colors.get(sector, 'gray')  # Default to gray if sector not found
        
        # Add marker to the appropriate emissions bin layer
        if emission_bin in emissions_layers:
            folium.Marker(
                location=[lat, lon],
                popup=f"Operator: {row['Operator']}<br>Sector: {sector}<br>Region: {row['Region']}<br>Emission: {row[' Emission ']}",
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(emissions_layers[emission_bin])

        # Also add the marker to the sector layer
        if sector in sector_layers:
            folium.Marker(
                location=[lat, lon],
                popup=f"Operator: {row['Operator']}<br>Sector: {sector}<br>Region: {row['Region']}<br>Emission: {row[' Emission ']}",
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(sector_layers[sector])

# Create the base map
m = folium.Map(location=[52.9375, -1.7201], zoom_start=6)  # Initial location and zoom level

# Add all emissions and sector layers to the map
for emissions_bin, layer in emissions_layers.items():
    layer.add_to(m)

for sector_name, layer in sector_layers.items():
    layer.add_to(m)

# Add a layer control for emissions
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Add a second layer control specifically for sectors
sector_control = folium.LayerControl(position='bottomright', collapsed=False)
sector_control.add_to(m)

# Save the map to an HTML file
m.save("map.html")
