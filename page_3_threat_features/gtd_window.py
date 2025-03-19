import sys
import os
import pandas as pd
import folium
import webbrowser

def generate_gtd_map():
    """Generates a single GTD map with all urban rail attacks globally."""
    data_path = "page_3_threat_features/GTD_data/gtd_combined.csv"
    output_folder = "page_3_threat_features/GTD_data/maps"
    os.makedirs(output_folder, exist_ok=True)
    global_map_path = os.path.join(output_folder, "gtd_map_all.html")

    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return

    if os.path.exists(global_map_path):
        webbrowser.open(global_map_path)  # Open the existing map
        return

    df = pd.read_csv(data_path, encoding="ISO-8859-1", low_memory=False)

    # Filter for transportation attacks related to trains and subways
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[
        (df["targtype1_txt"] == "Transportation") &
        (df["targsubtype1_txt"].isin(["Train/Train Tracks/Trolley", "Subway"]))
    ]

    # Count statistics
    total_attacks = len(df)
    us_attacks = df[df["country_txt"] == "United States"]
    world_attacks = df[df["country_txt"] != "United States"]

    pre_9_11_us = len(us_attacks[(us_attacks["iyear"] < 2001) | ((us_attacks["iyear"] == 2001) & (us_attacks["imonth"] < 9))])
    post_9_11_us = len(us_attacks) - pre_9_11_us

    pre_9_11_global = len(df[(df["iyear"] < 2001) | ((df["iyear"] == 2001) & (df["imonth"] < 9))])
    post_9_11_global = total_attacks - pre_9_11_global

    # Most common attack types
    us_top_attacks = us_attacks["attacktype1_txt"].value_counts().head(2)
    world_top_attacks = world_attacks["attacktype1_txt"].value_counts().head(2)

    # Create the folium map with a simple base map
    m = folium.Map(location=[20, 0], zoom_start=3, tiles="CartoDB positron")  # Faster, less detailed map

    # Add title
    title_html = """
    <div style="position: fixed;
                top: 10px; left: 50%;
                transform: translateX(-50%);
                background-color: rgba(255, 255, 255, 0.9);
                padding: 15px;
                font-size: 27px;
                font-weight: bold;
                text-align: center;
                z-index:9999;
                border-radius: 8px;">
        Global Terrorist Attacks on Urban Rail
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Add markers with hover tooltips (Attack Type & Date)
    for _, row in df.iterrows():
        color = "red" if (row["iyear"] > 2001 or (row["iyear"] > 2001 and row["imonth"] > 9)) else "orange"
        attack_date = f"{int(row['imonth']):02d}-{int(row['iday']):02d}-{row['iyear']}"
        tooltip_text = f"Attack type: {row['attacktype1_txt']}<br>Date: {attack_date}"

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=2.5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1.0,
            tooltip=tooltip_text
        ).add_to(m)

    # Add Legend
    legend_html = """
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; width: 170px; height: 80px; 
        background-color: white; z-index:9999; font-size:14px;
        border-radius: 5px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Legend</b><br>
        <div style='background-color:red; width: 15px; height: 15px; display: inline-block;'></div> Post-9/11 Attacks <br>
        <div style='background-color:orange; width: 15px; height: 15px; display: inline-block;'></div> Pre-9/11 Attacks <br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Statistics Bar
    stats_html = f"""
    <div style="position: fixed;
                bottom: 20px; right: 10px;
                width: 350px;
                background-color: rgba(255, 255, 255, 0.9);
                z-index:9999; font-size:14px;
                border-radius: 5px; padding: 10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Attack Statistics</b><br>
        <b>Top Attack Types in U.S.:</b><br>
        {us_top_attacks.index[0]}: {us_top_attacks.iloc[0]} attacks<br>
        {us_top_attacks.index[1]}: {us_top_attacks.iloc[1]} attacks<br><br>

        <b>Top Attack Types Globally:</b><br>
        {world_top_attacks.index[0]}: {world_top_attacks.iloc[0]} attacks<br>
        {world_top_attacks.index[1]}: {world_top_attacks.iloc[1]} attacks<br><br>

        <b>Total Attacks:</b> {total_attacks}<br>
        <b>Pre-9/11 Attacks (U.S.):</b> {pre_9_11_us}<br>
        <b>Post-9/11 Attacks (U.S.):</b> {post_9_11_us}<br>
        <b>Pre-9/11 Attacks (Global):</b> {pre_9_11_global}<br>
        <b>Post-9/11 Attacks (Global):</b> {post_9_11_global}<br>
        <div style="font-style: italic; font-size: 12px; text-align: center; margin-top: 10px;">
        Source: Global Terrorism Dataset
    </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(stats_html))

    # Save map
    m.save(global_map_path)

    # Open map in the system default web browser
    webbrowser.open(global_map_path)


if __name__ == "__main__":
    generate_gtd_map()
    sys.exit(0)  # Exit the script immediately, no GUI window is created
