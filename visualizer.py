import os
from xmlrpc.client import boolean

import folium
import pandas as pd
import networkx as nx
import branca.colormap as cm
from folium.plugins import HeatMap



# Ensure "outputs" folder exists
output_folder = "outputs"
os.makedirs(output_folder, exist_ok=True)

# Load MBTA Data
data_folder = "MBTA_graph_data"
nodes_path = os.path.join(data_folder, "Node_CSV.csv")
edges_path = os.path.join(data_folder, "Edge_CSV.csv")

nodes_df = pd.read_csv(nodes_path)
edges_df = pd.read_csv(edges_path)

# Create Graph
G = nx.Graph()

# Add Nodes
for _, row in nodes_df.iterrows():
    G.add_node(row['ID'], stop_name=row['stop_name'], pos=(row['Lat'], row['Lon']))

# Add Edges
for _, row in edges_df.iterrows():
    G.add_edge(row['Source'], row['Target'])

# Define MBTA Line Colors
color_mapping = {
    'Orange Line': 'orange',
    'Blue Line': 'blue',
    'Red Line': 'red',
    'Green Line': 'green',
}

# Compute centralities
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality_numpy(G)
closeness_centrality = nx.closeness_centrality(G)


def get_global_min_max(threat_folder, feature_columns):
    categorical_features = ["Defense_Posture", "Threat_Level"]  # Define categorical features
    continuous_features = [f for f in feature_columns if f not in categorical_features]  # Exclude categorical features

    global_min = {}
    global_max = {}

    for feature in continuous_features:
        all_values = []
        for filename in os.listdir(threat_folder):
            if filename.endswith(".csv"):
                df = pd.read_csv(os.path.join(threat_folder, filename))
                all_values.extend(df[feature].dropna().tolist())
        global_min[feature] = min(all_values)
        global_max[feature] = max(all_values)

    return global_min,global_max




def generate_mbta_map_without_features():
    """ Generates a simple MBTA network map without centrality features. """
    center_lat = nodes_df['Lat'].mean()
    center_lon = nodes_df['Lon'].mean()
    mbta_map = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')

    # Add Nodes (Stations)
    for _, row in nodes_df.iterrows():
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=3.5,
            color="black",
            fill=True,
            fill_color="black",
            fill_opacity=1.0,
            tooltip=row["stop_name"],
            popup=folium.Popup(f'Station: {row["stop_name"]}', max_width=250)
        ).add_to(mbta_map)

    # Add Edges (Connections)
    for _, row in edges_df.iterrows():
        source_id, target_id = row['Source'], row['Target']
        line = row['Line']

        source_pos = [G.nodes[source_id]['pos'][0], G.nodes[source_id]['pos'][1]]
        target_pos = [G.nodes[target_id]['pos'][0], G.nodes[target_id]['pos'][1]]

        line_color = color_mapping.get(line, 'gray')

        folium.PolyLine(
            [source_pos, target_pos],
            color=line_color,
            weight=3.5,
            opacity=0.8
        ).add_to(mbta_map)

    # Save Map
    map_path = os.path.join(output_folder, "outputs/mbta_map.html")
    mbta_map.save(map_path)
    return map_path


# Read Centralities from CSV
centrality_columns = {
    "No Centrality": None,
    "Degree": "Degree_Centrality",
    "Betweenness": "Betweenness_Centrality",
    "Eigen": "Eigen_Centrality",
    "Closeness": "Closeness_Centrality",
    "Domirank": "Domirank_Centrality"  # Added Domirank centrality
}


def generate_mbta_map_with_centrality(selected_centrality="No Centrality", top_k=len(nodes_df)):
    """
    Generates an MBTA map with selectable centrality measures from precomputed values.
    Highlights the top K nodes when a centrality is selected; otherwise, all nodes remain black.
    """
    center_lat = nodes_df['Lat'].mean()
    center_lon = nodes_df['Lon'].mean()
    mbta_map = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')

    centrality_column = centrality_columns[selected_centrality]

    # If no centrality, all nodes are black
    if selected_centrality == "No Centrality":
        colormap = None
        top_k_nodes = []
    else:
        # Get min/max for proper color scaling
        min_val, max_val = nodes_df[centrality_column].min(), nodes_df[centrality_column].max()
        colormap = cm.LinearColormap(["green", "yellow", "red"], vmin=min_val, vmax=max_val)

        # Identify top K nodes based on selected centrality
        top_k_nodes = nodes_df.nlargest(top_k, centrality_column)["ID"].tolist()

    # Add Nodes (Stations)
    for _, row in nodes_df.iterrows():
        station_id = row['ID']
        station_name = row["stop_name"]
        lat, lon = row["Lat"], row["Lon"]

        if selected_centrality == "No Centrality":
            node_color = "black"
            tooltip_text = f"{station_name}"  # Only show station name
        else:
            original_color = colormap(row[centrality_column])
            centrality_text = f"{row[centrality_column]:.3f}"
            node_color = original_color if station_id in top_k_nodes else "#B0B0B0"
            tooltip_text = f"{station_name} - {selected_centrality}: {centrality_text}"

        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=node_color,
            fill=True,
            fill_color=node_color,
            fill_opacity=1.0,
            tooltip=tooltip_text,
            popup=folium.Popup(f'Station: {station_name}<br>{selected_centrality}: {centrality_text}' if selected_centrality != "No Centrality" else f'Station: {station_name}', max_width=250)
        ).add_to(mbta_map)

    # Adjust Edge Width Based on Centrality Selection
    edge_width = 3.5 if selected_centrality == "No Centrality" else 2

    # Add Edges (Connections)
    for _, row in edges_df.iterrows():
        source_id, target_id = row['Source'], row['Target']
        line = row['Line']

        source_pos = [G.nodes[source_id]['pos'][0], G.nodes[source_id]['pos'][1]]
        target_pos = [G.nodes[target_id]['pos'][0], G.nodes[target_id]['pos'][1]]

        line_color = color_mapping.get(line, 'gray')

        folium.PolyLine(
            [source_pos, target_pos],
            color=line_color,
            weight=edge_width,
            opacity=0.8
        ).add_to(mbta_map)

    # Add color scale if centrality is selected
    if colormap:
        mbta_map.add_child(colormap)

    # Save Map
    map_path = os.path.join(output_folder, f"mbta_map_with_{selected_centrality.lower()}_top{top_k}.html")
    mbta_map.save(map_path)
    return map_path


# Define folder paths
threat_folder = "page_3_threat_features/Feature_Label"
layer_folder = "page_3_threat_features/Layer_Information"

# Layer CSVs
layer_files = {
    "Police Stations": "Boston_police.csv",
    "Fire Stations": "Boston_fire.csv",
    "Hospitals": "Boston_hospital.csv"
}

# Emoji markers for layers
layer_icons = {
    "Police Stations": "access_measures_logos/police.png",
    "Fire Stations": "access_measures_logos/fire.png",
    "Hospitals": "access_measures_logos/hospital.png"
}

# Updated feature dropdown options based on new dataset
# feature_columns = [
#     "D_nearest_police", "D_nearest_fire", "D_nearest_hospital",
#     "Protection_Level", "Total_Population", "average_ridership",
#     "All_Crime_Index", "Threat_level"
# ]


feature_columns = [
    "Attractiveness",
    "Defense_Posture", "Population_Density", "Average_Ridership",
    "Crime_Index", "Threat_Level","D_nearest_police", "D_nearest_fire", "D_nearest_hospital","D_police_fire"
]

# Define categorical colors
category_colors = {
    "High": "red",
    "Medium": "yellow",
    "Low": "green"
}

category_colors_defense_posture = {
    "High": "green",
    "Medium": "yellow",
    "Low": "red"
}

additional_fields = {
    "D_nearest_police_name": "Nearest police station",
    "D_nearest_fire_name": "Nearest fire station",
    "D_nearest_hospital_name": "Nearest hospital"
}

# feature_descriptions = {
#     "D_nearest_police": "Distance to the nearest police station in meters. Highlights the top K stations closest to police.",
#     "D_nearest_fire": "Distance to the nearest fire station in meters. Highlights the top K stations closest to fire services.",
#     "D_nearest_hospital": "Distance to the nearest hospital in meters. Highlights the top K stations closest to medical facilities.",
#     "Protection_Level": "Level of protection based on nearby emergency services categorized as High, Medium, or Low. Displays all stations categorized under the selected level.",
#     "Total_Population": "Total population in the area surrounding the station. Highlights the top K stations with the highest surrounding populations.",
#     "average_ridership": "Average daily ridership at this station. Highlights the top K stations with the highest ridership.",
#     "All_Crime_Index": "Composite index representing the total crime rate in the vicinity of the station. Highlights the top K stations with the highest crime indices.",
#     "Threat_level": "Threat level based on crime and vulnerability data, categorized as High, Medium, or Low. Displays all stations categorized under the selected threat level.",
#     "D_nearest_police_name": "Name of the nearest police station. Provided for informational purposes, not selectable for top K.",
#     "D_nearest_fire_name": "Name of the nearest fire station. Provided for informational purposes, not selectable for top K.",
#     "D_nearest_hospital_name": "Name of the nearest hospital. Provided for informational purposes, not selectable for top K."
# }

feature_descriptions = {
    "D_nearest_police": "Distance to the nearest police station in meters. Highlights the top K stations closest to police.",
    "D_nearest_fire": "Distance to the nearest fire station in meters. Highlights the top K stations closest to fire services.",
    "D_nearest_hospital": "Distance to the nearest hospital in meters. Highlights the top K stations closest to medical facilities.",
    "Defense_Posture": "Level of protection based on nearby emergency services categorized as High, Medium, or Low. Displays all stations categorized under the selected level.",
    "Population_Density": "Total population in the area surrounding the station. Highlights the top K stations with the highest surrounding populations.",
    "Average_Ridership": "Average daily ridership at this station. Highlights the top K stations with the highest ridership.",
    "Crime_Index": "Composite index representing the total crime rate in the vicinity of the station. Highlights the top K stations with the highest crime indices.",
    "Threat_Level": "Threat level is based on crime data, categorized as High, Medium, or Low. Displays all stations categorized under the selected threat level.",
    "D_nearest_police_name": "Name of the nearest police station. Provided for informational purposes, not selectable for top K.",
    "D_nearest_fire_name": "Name of the nearest fire station. Provided for informational purposes, not selectable for top K.",
    "D_nearest_hospital_name": "Name of the nearest hospital. Provided for informational purposes, not selectable for top K.",
    "Attractiveness": "Composite score based on multiple threat, defense, and network features to represent assumed adversarial preferences. (These scores may be updated based on subject matter expert inputs)",
    "D_police_fire": "Weighted sum of distances to nearest police and fire departments to indicate the level of potential protective resources for the target rail station of interest."
}



crime_folder = "page_3_threat_features/Crime_Data"

global_feature_min, global_feature_max = get_global_min_max(threat_folder, feature_columns)

def generate_threat_feature_map(time_of_day, selected_feature, top_k=None, active_layers=None, show_heatmap=False):
    """
    Generates a network map where nodes are colored based on a selected threat feature.
    Highlights the top K nodes based on the selected feature.
    Optionally adds external layers like police, fire, hospital locations and a HeatMap for crime data.
    """
    csv_file = f"Feature_Label_{time_of_day}.csv"
    file_path = os.path.join(threat_folder, csv_file)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    # Load the selected CSV file
    feature_df = pd.read_csv(file_path)


    # Merge with nodes_df based on Station_ID
    merged_df = feature_df.rename(columns={"Station_Name": "Station_Name", "ID": "ID"})


    center_lat = merged_df['Lat'].mean()
    center_lon = merged_df['Lon'].mean()
    mbta_map = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')

    # Check if the selected feature is categorical (Protection_Level, Threat_Level)
    # is_categorical = selected_feature in ["Protection_Level", "Threat_level"]

    is_categorical = selected_feature in ["Defense_Posture", "Threat_Level"]

    if not is_categorical:
        min_val, max_val = merged_df[selected_feature].min(), merged_df[selected_feature].max()
        # min_val = global_feature_min[selected_feature]
        # max_val = global_feature_max[selected_feature]


        median_val = merged_df[selected_feature].median()
        colormap = cm.LinearColormap(["green", "yellow", "red"], vmin=min_val, vmax=max_val)

        # Vertical color bar with labels for min, median, max values
        legend_html = f"""
        <div style="position: fixed; bottom: 50px; left: 50px; width: 40px; height: 180px; background-color: rgba(255, 255, 255, 0.8); z-index:9999; font-size:12px; border: none; padding: 10px;">
            <div style="height: 170px; width: 20px; background: linear-gradient(to top, green, yellow, red);"></div>
            <div style="position: absolute; bottom: 0; left: 35px;">{min_val:.2f}</div>
            <div style="position: absolute; top: 50%; left: 35px;">{median_val:.2f}</div>
            <div style="position: absolute; top: 0; left: 35px;">{max_val:.2f}</div>
        </div>
        """
        mbta_map.get_root().html.add_child(folium.Element(legend_html))
    else:

        colormap = None  # No colormap for categorical features


    top_k_data = []

    # Merge standard and additional feature columns
    display_features = feature_columns + list(additional_fields.keys())

    # Calculate padding based on the longest label
    longest_label = max([additional_fields.get(feat, feat) for feat in display_features], key=len)

    ascending_features = {"D_nearest_police", "D_nearest_fire", "D_nearest_hospital","D_police_fire"}

    # Determine if the feature is ascending or descending
    is_ascending = selected_feature in ascending_features

    if top_k and top_k < len(merged_df):
        if is_ascending:
            top_k_nodes = merged_df.nsmallest(top_k, selected_feature)["ID"].tolist()  # Use nsmallest for ascending
        else:
            top_k_nodes = merged_df.nlargest(top_k, selected_feature)["ID"].tolist()
    else:
        top_k_nodes = merged_df["ID"].tolist()

    # Add Nodes (Stations)
    for _, row in merged_df.iterrows():
        station_id = row['ID']
        station_name = row["Station_Name"]
        lat, lon = row["Lat"], row["Lon"]
        feature_value = row[selected_feature]

        if station_id in top_k_nodes:
            top_k_data.append((station_name, feature_value))


        # Apply categorical colors for Protection_Level and Threat_Level
        if is_categorical:
            node_color = category_colors.get(feature_value, "grey")if not selected_feature =="Defense_Posture" else category_colors_defense_posture.get(feature_value, "grey")
            node_radius=5
        else:
            if station_id in top_k_nodes:
                node_radius = 5  # Larger size for top K nodes
                node_color = colormap(feature_value) if not pd.isna(feature_value) else "grey"
            else:
                node_radius = 3  # Smaller size for non-top K nodes
                node_color = "#B0B0B0"  # Grey for non-top K nodes

        # Define a dictionary to specify custom labels for specific fields
        custom_labels = {
            "D_nearest_police": "Distance from nearest police station",
            "D_nearest_fire": "Distance from nearest fire station ",
            "D_nearest_hospital": "Distance from nearest hospital ",
            "D_nearest_police_name": "Nearest Police Station Name",
            "D_nearest_fire_name": "Nearest Fire Station Name",
            "D_nearest_hospital_name": "Nearest Hospital Name",
            "D_police_fire": "Weighted distance of police & fire station"
        }

        tooltip_content = f"Station Name: {row['Station_Name']}<br>" + "<br>".join([
            f"{custom_labels.get(feat, feat.replace('_', ' ').capitalize())}: {round(row[feat], 2) if isinstance(row[feat], float) else row[feat]}"
            for feat in display_features if feat != "Attractiveness"  # Exclude Attractiveness
        ])

        popup_content = f"Station Name: {row['Station_Name']}<br>" + "<br>".join([
            f"{custom_labels.get(feat, feat.replace('_', ' ').capitalize())}: {round(row[feat], 2) if isinstance(row[feat], float) else row[feat]}"
            for feat in display_features if feat != "Attractiveness"  # Exclude Attractiveness
        ])

        folium.CircleMarker(
            location=[lat, lon],
            radius=node_radius,
            color=node_color,
            fill=True,
            fill_color=node_color,
            fill_opacity=1.0,
            tooltip=f"Station Features:<br>{tooltip_content}",
            popup=folium.Popup(f"Station: {station_name}<br>{popup_content}", max_width=250)
        ).add_to(mbta_map)



    top_k_data.sort(key=lambda x: x[1], reverse=not is_ascending)


    # ✅ **Retained Edge Structure**
    edge_width = 1.5 if selected_feature == "No Centrality" else 1.5

    for _, row in edges_df.iterrows():
        source_id, target_id = row['Source'], row['Target']
        line = row['Line']

        source_pos = [G.nodes[source_id]['pos'][0], G.nodes[source_id]['pos'][1]]
        target_pos = [G.nodes[target_id]['pos'][0], G.nodes[target_id]['pos'][1]]

        line_color = color_mapping.get(line, 'gray')

        folium.PolyLine(
            [source_pos, target_pos],
            color=line_color,
            weight=edge_width,
            opacity=0.8
        ).add_to(mbta_map)

    # ✅ **Add External Layers (Police, Fire, Hospital)**
    if active_layers:
        for layer_name, file_name in layer_files.items():
            if layer_name in active_layers:
                layer_path = os.path.join(layer_folder, file_name)
                if os.path.exists(layer_path):
                    layer_df = pd.read_csv(layer_path)

                    for _, loc in layer_df.iterrows():
                        lat, lon = loc["Latitude"], loc["Longitude"]
                        icon_path = layer_icons[layer_name]

                        # Create a custom icon
                        custom_icon = folium.CustomIcon(
                            icon_image=icon_path,
                            icon_size=(20, 20),  # Set the size of the icon
                            icon_anchor=(10, 10)  # Anchor the middle-bottom point of the icon
                        )

                        folium.Marker(
                            location=[lat, lon],
                            icon=custom_icon,
                            tooltip=layer_name
                        ).add_to(mbta_map)

    # ✅ **Add Crime HeatMap if enabled**
    if show_heatmap:
        crime_file = f"Boston_Cambridge_Brookline_crime_filtered_{time_of_day}.csv"
        crime_path = os.path.join(crime_folder, crime_file)

        if os.path.exists(crime_path):
            crime_df = pd.read_csv(crime_path)

            # ✅ Filter out rows with missing latitude/longitude values
            crime_df = crime_df.dropna(subset=["Lat", "Long"])

            # ✅ Extract valid coordinates for the HeatMap
            heat_data = crime_df[["Lat", "Long"]].values.tolist()
            gradient = {0.2: 'red', 0.4: 'darkred', 0.6: 'firebrick', 0.8: 'crimson', 1.0: 'maroon'}
            # ✅ Ensure there's crime data before applying HeatMap
            if heat_data:
                HeatMap(
                    heat_data,
                    radius=15,
                    blur=15,
                    min_opacity=0.4,
                ).add_to(mbta_map)

    # ✅ **Add Legend for Categorical Features**

    if is_categorical and selected_feature != "Attractiveness":
        if selected_feature=="Defense_Posture":
            legend_html = """
                    <div style="
                        position: fixed; 
                        bottom: 50px; left: 50px; width: 150px; height: 100px; 
                        background-color: white; z-index:9999; font-size:14px;
                        border-radius: 5px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                        <b>Legend</b><br>
                        <div style='background-color:Green; width: 15px; height: 15px; display: inline-block;'></div> High <br>
                        <div style='background-color:yellow; width: 15px; height: 15px; display: inline-block;'></div> Medium <br>
                        <div style='background-color:Red; width: 15px; height: 15px; display: inline-block;'></div> Low <br>
                    </div>
                    """
        else:
            legend_html = """
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 100px; 
                background-color: white; z-index:9999; font-size:14px;
                border-radius: 5px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                <b>Legend</b><br>
                <div style='background-color:red; width: 15px; height: 15px; display: inline-block;'></div> High <br>
                <div style='background-color:yellow; width: 15px; height: 15px; display: inline-block;'></div> Medium <br>
                <div style='background-color:green; width: 15px; height: 15px; display: inline-block;'></div> Low <br>
            </div>
            """


        mbta_map.get_root().html.add_child(folium.Element(legend_html))


    elif colormap and selected_feature != "Attractiveness":
        # mbta_map.add_child(colormap)

        # HTML for top K nodes overlay
        remaining_stations = len(top_k_data) - 10

        # HTML for top K nodes overlay
        top_k_html = f"""
        <div style="position: fixed; top: 50px; right: 50px; width: 200px; height: 250px; 
                    background-color: white; z-index:9999; font-size:14px;
                    border: 2px solid grey; overflow-y: auto;">
            <h4 style="text-align:center;">Top {min(len(top_k_data), 10)}: {selected_feature}</h4>
            <ul>
        """
        for name, value in top_k_data[:10]:  # limit to top 10 for display
            top_k_html += f"<li>{name}: {value:.2f}</li>"

        if remaining_stations > 0:
            top_k_html += f"<li>... and {remaining_stations} more stations</li>"

        top_k_html += "</ul></div>"

        # Add the overlay to the map
        mbta_map.get_root().html.add_child(folium.Element(top_k_html))

    description_html = f"""
    <div style="position: fixed; 
                top: 10px; 
                left: 10px; 
                width: 300px; 
                background-color: white; 
                z-index:9999; 
                font-size:14px; 
                padding: 10px; 
                border-radius: 5px; 
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <strong>{selected_feature.replace('_', ' ').capitalize()}:</strong> {feature_descriptions[selected_feature]}
    </div>
    """

    mbta_map.get_root().html.add_child(folium.Element(description_html))

    # ✅ **Save the Final Map**
    map_path = os.path.join(output_folder, f"mbta_threat_{time_of_day}_{selected_feature}_top{top_k}.html")
    mbta_map.save(map_path)
    return map_path


temp_folder="page_3_threat_features/temp_playground"

def generate_attractiveness_map(time_of_day):
    csv_file = f"Feature_Label_{time_of_day}.csv"
    file_path = os.path.join(temp_folder, csv_file)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    # Load the selected CSV file
    feature_df = pd.read_csv(file_path)

    center_lat = feature_df['Lat'].mean()
    center_lon = feature_df['Lon'].mean()
    mbta_map = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')

    # Define the colormap for Attractiveness
    min_val = feature_df["Attractiveness"].min()
    max_val = feature_df["Attractiveness"].max()
    median_val = feature_df["Attractiveness"].median()
    colormap = cm.LinearColormap(["green", "yellow", "red"], vmin=min_val, vmax=max_val)

    # ✅ **Retained Edge Structure**
    edge_width = 1.5  # Keep edges thinner but visible
    for _, row in edges_df.iterrows():
        source_id, target_id = row['Source'], row['Target']
        line = row['Line']

        source_pos = [G.nodes[source_id]['pos'][0], G.nodes[source_id]['pos'][1]]
        target_pos = [G.nodes[target_id]['pos'][0], G.nodes[target_id]['pos'][1]]

        line_color = color_mapping.get(line, 'gray')  # Same color scheme as before

        folium.PolyLine(
            [source_pos, target_pos],
            color=line_color,
            weight=edge_width,
            opacity=0.8
        ).add_to(mbta_map)

    # ✅ **Add Nodes (Stations) for Attractiveness**
    for _, row in feature_df.iterrows():
        station_id = row['ID']
        station_name = row["Station_Name"]
        lat, lon = row["Lat"], row["Lon"]
        attractiveness_score = row["Attractiveness"]
        threat_level = row["Threat_Level"]
        defense_posture = row["Defense_Posture"]

        folium.CircleMarker(
            location=[lat, lon],
            radius=5,  # Fixed size for all nodes
            color=colormap(attractiveness_score),
            fill=True,
            fill_color=colormap(attractiveness_score),
            fill_opacity=1.0,
            tooltip=f"Station: {station_name}<br>"
                    f"Attractiveness: {attractiveness_score:.2f}<br>"
                    "<br> Additional info: <br>"
                    f"Threat Level: {threat_level}<br>"
                    f"Defense Posture: {defense_posture}",
            popup=f"Station: {station_name}<br>"
                    f"Attractiveness: {attractiveness_score:.2f}<br>"
                    "<br> Additional info: <br>"
                    f"Threat Level: {threat_level}<br>"
                    f"Defense Posture: {defense_posture}"
        ).add_to(mbta_map)

    # ✅ **Add Color Bar**
    legend_html = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; width: 40px; height: 180px; background-color: rgba(255, 255, 255, 0.8); z-index:9999; font-size:12px; border: none; padding: 10px;">
        <div style="height: 170px; width: 20px; background: linear-gradient(to top, green, yellow, red);"></div>
        <div style="position: absolute; bottom: 0; left: 35px;">{min_val:.2f}</div>
        <div style="position: absolute; top: 50%; left: 35px;">{median_val:.2f}</div>
        <div style="position: absolute; top: 0; left: 35px;">{max_val:.2f}</div>
    </div>
    """
    mbta_map.get_root().html.add_child(folium.Element(legend_html))
    description_html = f"""
        <div style="position: fixed; 
                    top: 10px; 
                    left: 10px; 
                    width: 300px; 
                    background-color: white; 
                    z-index:9999; 
                    font-size:14px; 
                    padding: 10px; 
                    border-radius: 5px; 
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
             The stations are color-coded representing <strong> Attractiveness </strong>, which is a Composite score based on multiple threat, defense, and network features to represent assumed adversarial preferences. (These scores may be updated based on subject matter expert inputs)
        </div>
        """

    mbta_map.get_root().html.add_child(folium.Element(description_html))

    # ✅ **Save the Final Map**
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    map_path = os.path.join(output_folder, f"mbta_attractiveness_{time_of_day}.html")
    mbta_map.save(map_path)

    return map_path


def generate_overlay_singular_map(time_of_day, feature, top_k, common=False):
    """
    Generates a map overlaying the top K nodes based on a selected feature.
    - If `common` is True: Highlights common top-K nodes in red.
    - If `common` is False: Highlights top-K nodes based on the selected feature's colormap.
    """

    temp_folder = "page_3_threat_features/temp_playground"
    output_folder = "page_3_threat_features/output_maps"

    csv_file = f"Feature_Label_{time_of_day}.csv"
    file_path = os.path.join(temp_folder, csv_file)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    # Load the CSV file
    feature_df = pd.read_csv(file_path)

    # Compute center for map view
    center_lat = feature_df['Lat'].mean()
    center_lon = feature_df['Lon'].mean()
    mbta_map = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')

    # Define colormap for numerical features (if not in common mode)
    if not common:
        min_val = feature_df[feature].min()
        max_val = feature_df[feature].max()
        median_val = feature_df[feature].median()
        colormap = cm.LinearColormap(["green", "yellow", "red"], vmin=min_val, vmax=max_val)
    else:
        colormap = None  # No color scheme for common map

    ascending_features = {"D_nearest_police", "D_nearest_fire", "D_nearest_hospital","D_police_fire"}

    # Determine if the feature is ascending or descending



    # Determine the top K stations based on the feature
    if not common:
        top_k_nodes = feature_df.nlargest(top_k, feature)["ID"].tolist()
    else:
        # Collect top_k nodes for each selected feature
        top_k_sets = [
            set(feature_df.nlargest(top_k, feat)["ID"].tolist()) for feat in feature
        ]

        # Count occurrences of each node in multiple features
        node_counts = {}
        for feature_set in top_k_sets:
            for node in feature_set:
                node_counts[node] = node_counts.get(node, 0) + 1

        # Assign colors based on occurrences
        node_color_map = {
            1: "yellow",  # Present in 1 feature
            2: "orange",  # Present in 2 features
            3: "red"      # Present in 3 features
        }

    # ✅ **Retained Edge Structure**
    edge_width = 1.5
    for _, row in edges_df.iterrows():
        source_id, target_id = row['Source'], row['Target']
        line = row['Line']

        source_pos = [G.nodes[source_id]['pos'][0], G.nodes[source_id]['pos'][1]]
        target_pos = [G.nodes[target_id]['pos'][0], G.nodes[target_id]['pos'][1]]

        line_color = color_mapping.get(line, 'gray')

        folium.PolyLine(
            [source_pos, target_pos],
            color=line_color,
            weight=edge_width,
            opacity=0.8
        ).add_to(mbta_map)

    # ✅ **Add Nodes (Stations)**
    for _, row in feature_df.iterrows():
        station_id = row['ID']
        station_name = row["Station_Name"]
        lat, lon = row["Lat"], row["Lon"]
        feature_value = row[feature]

        # Coloring logic:
        if common:
            node_count = node_counts.get(station_id, 0)
            node_color = node_color_map.get(node_count, "grey")  # Assign color based on occurrences
            node_radius = 5 if node_count > 0 else 3  # Highlight top nodes3
        else:
            # Top K nodes get color from colormap, others are grey
            node_color = colormap(feature_value) if station_id in top_k_nodes else "grey"
            node_radius = 5 if station_id in top_k_nodes else 3


        if not common:
            content= f"Station: {station_name}<br>{feature}: {feature_value:.2f}"
        else:
            content = f"Station: {station_name}"

        folium.CircleMarker(
            location=[lat, lon],
            radius=node_radius,
            color=node_color,
            fill=True,
            fill_color=node_color,
            fill_opacity=1.0,
                tooltip=content,
                popup=content,
        ).add_to(mbta_map)

    # ✅ **Add Color Bar (Only for Individual Feature Maps)**
    if not common:
        legend_html = f"""
        <div style="position: fixed; bottom: 50px; left: 50px; width: 40px; height: 180px; background-color: rgba(255, 255, 255, 0.8); z-index:9999; font-size:12px; border: none; padding: 10px;">
            <div style="height: 170px; width: 20px; background: linear-gradient(to top, green, yellow, red);"></div>
            <div style="position: absolute; bottom: 0; left: 35px;">{min_val:.2f}</div>
            <div style="position: absolute; top: 50%; left: 35px;">{median_val:.2f}</div>
            <div style="position: absolute; top: 0; left: 35px;">{max_val:.2f}</div>
        </div>
        """

    else:
        # Color legend for common occurrence map
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 100px; background-color: rgba(255, 255, 255, 0.8); z-index:9999; font-size:12px; border: none; padding: 10px;">
            <b>Common Occurrences</b><br>
            <div style="height: 15px; width: 15px; background: red; display: inline-block;"></div> Present in all frames<br>
            <div style="height: 15px; width: 15px; background: orange; display: inline-block;"></div> Present in 2 frames<br>
            <div style="height: 15px; width: 15px; background: yellow; display: inline-block;"></div> Present in 1 frames<br>
        </div>
        """
    mbta_map.get_root().html.add_child(folium.Element(legend_html))

    # ✅ **Description (Only for Individual Feature Maps)**
    if not common:
        description_html = f"""
        <div style="position: fixed; 
                    top: 10px; 
                    left: 10px; 
                    width: 300px; 
                    background-color: white; 
                    z-index:9999; 
                    font-size:14px; 
                    padding: 10px; 
                    border-radius: 5px; 
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            The stations are color-coded representing <strong>{feature.replace("_", " ").capitalize()}</strong>, 
            highlighting the top {top_k} stations in this feature.
        </div>
        """
    else:
        description_html = f"""
                <div style="position: fixed; 
                            top: 10px; 
                            left: 10px; 
                            width: 300px; 
                            background-color: white; 
                            z-index:9999; 
                            font-size:14px; 
                            padding: 10px; 
                            border-radius: 5px; 
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                    Represents the common stations which are overlapping in all 3 ranges.
                </div>
                """
    mbta_map.get_root().html.add_child(folium.Element(description_html))

    # ✅ **Save the Final Map**
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Different filenames for individual and common maps
    if common:
        map_path = os.path.join(output_folder, f"mbta_common_top{top_k}_{time_of_day}.html")
    else:
        map_path = os.path.join(output_folder, f"mbta_{feature}_top{top_k}_{time_of_day}.html")

    mbta_map.save(map_path)

    return map_path


