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

# Create a dictionary to hold feature groups for each combination of sector and emissions
layer_groups = {}

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
            sector_colors[sector] = predefined_colors[len(sector_colors) % len(predefined_colors)]

    # Add markers to respective combination layers
    for idx, row in data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        emission_bin = row['Emission_Bin']
        sector = row['Sector']
        
        # Create a unique layer name based on sector and emission bin
        layer_name = f"{sector} - {emission_bin}"

        # Create the layer if it doesn't exist
        if layer_name not in layer_groups:
            layer_groups[layer_name] = folium.FeatureGroup(name=layer_name)

        # Get the color for the sector
        marker_color = sector_colors.get(sector, 'gray')  # Default to gray if sector not found
        
        # Add marker to the appropriate layer
        folium.Marker(
            location=[lat, lon],
            popup=f"Operator: {row['Operator']}<br>Sector: {sector}<br>Region: {row['Region']}<br>Emission: {row[' Emission ']}",
            icon=folium.Icon(color=marker_color, icon='info-sign')
        ).add_to(layer_groups[layer_name])

# Create the base map
m = folium.Map(location=[52.9375, -1.7201], zoom_start=6)  # Initial location and zoom level


# Sort layer groups alphabetically
sorted_layer_names = sorted(layer_groups.keys(), key=lambda x: (x.split(' - ')[0], x.split(' - ')[1]))

# Add all sector-emission combination layers to the map in sorted order
for layer_name in sorted_layer_names:
    layer_groups[layer_name].add_to(m)

# Add a layer control to the map
layer_control = folium.LayerControl(position='topright', collapsed=False)
layer_control.add_to(m)

# Create a legend for sectors
legend_html = '''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 160px; height: auto; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white;
                opacity: 0.8;
                padding: 10px;">
        <h4 style="text-align: center;">Sector Legend</h4>
        <div style="display: flex; flex-direction: column;">
'''

# Add sector colors to the legend
for sector, color in sector_colors.items():
    legend_html += f'<div style="margin: 5px;"><span style="background-color: {color}; width: 15px; height: 15px; display: inline-block; border-radius: 3px;"></span> {sector}</div>'

legend_html += '''
        </div>
    </div>
'''

# Add the legend to the map
m.get_root().html.add_child(folium.Element(legend_html))

# Function to add "Select All" checkbox to the map
def add_select_all_option(map_object):
    # Create JavaScript for the select all option
    select_all_js = '''
    <script>
    function selectAll() {
        var layers = document.querySelectorAll('.leaflet-control-layers-selector');
        var selectAllCheckbox = document.getElementById('select-all');

        // If selectAllCheckbox is checked, check all layer checkboxes
        if (selectAllCheckbox.checked) {
            layers.forEach(function(layer) {
                layer.checked = true;
                layer.dispatchEvent(new Event('change'));
            });
        } else {
            // Uncheck all layer checkboxes
            layers.forEach(function(layer) {
                layer.checked = false;
                layer.dispatchEvent(new Event('change'));
            });
        }
    }
    </script>
    '''

    # Create HTML for the "Select All" checkbox
    select_all_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 175px; 
                z-index: 9999; 
                font-size: 14px; 
                background-color: white; 
                padding: 10px; 
                border: 2px solid black; 
                border-radius: 5px;">
        <input type="checkbox" id="select-all" onclick="selectAll()"> Select All
    </div>
    '''

    # Add JavaScript and checkbox to the map
    map_object.get_root().html.add_child(folium.Element(select_all_js))
    map_object.get_root().html.add_child(folium.Element(select_all_html))

# Add the select all option to the map
add_select_all_option(m)

# Save the map to an HTML file
m.save("map_with_select_all.html")
