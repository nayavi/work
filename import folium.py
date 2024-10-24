
import folium
import pandas as pd
import numpy as np

# Step 1: List of CSV files (replace with your actual file paths)
file_list = ['hospitals_ll.csv', 'otherconsumers_ll.csv', 'otherindustries_ll.csv','powerproducers_ll.csv','waste_ll.csv','watertreatment_ll.csv']  # Add all n CSV file names here

# Initialize an empty dataframe to store all lat/lon data for calculating the average location
all_data = pd.DataFrame(columns=['Latitude', 'Longitude'])

# Step 2: Create a base map object (this will be centered later based on average lat/lon)
m = None

# Step 3: Create dictionaries to hold feature groups for each category
operator_layers = {}
sector_layers = {}
region_layers = {}

# Step 4: Define bins for Emissions
bins = [0, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 5000, 6000, 10000, np.inf]
emission_labels = ['0-200', '201-400', '401-600', '601-800', '801-1000',
                   '1001-2000', '2001-3000', '3001-4000', '4001-5000',
                   '5001-6000', '6001-10000', '10000+']

# Create a feature group for each emissions bin
emissions_layers = {label: folium.FeatureGroup(name=f'Emissions: {label}') for label in emission_labels}



# Step 5: Loop over each file to process it
for i, file_name in enumerate(file_list):
    # Read the data from the current CSV file
    data = pd.read_csv(file_name)
    
    # Step 6: Append latitude and longitude to the combined dataframe
    all_data = pd.concat([all_data, data[['Latitude', 'Longitude']]], ignore_index=True)

    # Step 7: Bin the "Emissions" column based on the defined bins
    data['Emissions_Bin'] = pd.cut(data[' Emission '], bins=bins, labels=emission_labels, include_lowest=True)

    # Step 8: Add markers for each row in the current file
    for idx, row in data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        
        # Get the category values for this row
        operator = row['Operator']
        sector = row['Sector']
        region = row['Region']
        emissions_bin = row['Emissions_Bin']
        
        # Ensure the operator layer exists
        if operator not in operator_layers:
            operator_layers[operator] = folium.FeatureGroup(name=f'Operator: {operator}')
        
        # Ensure the sector layer exists
        if sector not in sector_layers:
            sector_layers[sector] = folium.FeatureGroup(name=f'Sector: {sector}')
        
        # Ensure the region layer exists
        if region not in region_layers:
            region_layers[region] = folium.FeatureGroup(name=f'Region: {region}')
        
        # Add marker to the appropriate operator layer
        folium.Marker(
            location=[lat, lon],
            popup=f"Operator: {operator}<br>Sector: {sector}<br>Region: {region}<br>Emissions: {row[' Emission ']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(operator_layers[operator])

        # Add marker to the appropriate sector layer
        folium.Marker(
            location=[lat, lon],
            popup=f"Operator: {operator}<br>Sector: {sector}<br>Region: {region}<br>Emissions: {row[' Emission ']}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(sector_layers[sector])

        # Add marker to the appropriate region layer
        folium.Marker(
            location=[lat, lon],
            popup=f"Operator: {operator}<br>Sector: {sector}<br>Region: {region}<br>Emissions: {row[' Emission ']}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(region_layers[region])

        # Add marker to the appropriate emissions bin layer
        folium.Marker(
            location=[lat, lon],
            popup=f"Operator: {operator}<br>Sector: {sector}<br>Region: {region}<br>Emissions: {row[' Emission ']}",
            icon=folium.Icon(color='orange', icon='info-sign')
        ).add_to(emissions_layers[emissions_bin])

# Step 9: Create the base map and center it later based on average lat/lon
if m is None:
    m = folium.Map(location=[0, 0], zoom_start=3)  # Placeholder, we'll update this later

# Step 10: Add all the operator, sector, region, and emissions layers to the map
for operator, layer in operator_layers.items():
    layer.add_to(m)

for sector, layer in sector_layers.items():
    layer.add_to(m)

for region, layer in region_layers.items():
    layer.add_to(m)

for emissions_bin, layer in emissions_layers.items():
    layer.add_to(m)

# Step 11: Calculate the average latitude and longitude across all files
avg_lat = all_data['Latitude'].mean()
avg_lon = all_data['Longitude'].mean()

# Step 12: Recenter the map at the average latitude and longitude
m.location = [avg_lat, avg_lon]

# Step 13: Add LayerControl to allow toggling of categories
folium.LayerControl().add_to(m)

# Step 14: Save the map to an HTML file and display it
m.save('map_with_multiple_categories.html')

print(f"Map created with average location at: Latitude {avg_lat}, Longitude {avg_lon}")
