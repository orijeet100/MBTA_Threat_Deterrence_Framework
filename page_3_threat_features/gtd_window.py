import sys
import os
import pandas as pd
import folium
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QGridLayout, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt

class GTDMapWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global Terrorism Database (GTD) Visualization")
        # Start Maximized (Keeps Minimize & Close Buttons, Removes Resize)
        self.showMaximized()

        # Disable resizing but keep Minimize and Close buttons
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        # Ensure output folder exists
        self.output_folder = "page_3_threat_features/GTD_data/maps"
        os.makedirs(self.output_folder, exist_ok=True)

        # Check if maps exist, otherwise generate them
        self.us_map_path = os.path.join(self.output_folder, "gtd_us_map.html")
        self.world_map_path = os.path.join(self.output_folder, "gtd_world_map.html")

        if not os.path.exists(self.us_map_path) or not os.path.exists(self.world_map_path):
            self.generate_gtd_maps()

        # Display UI once both maps are available
        self.setup_ui()

    def generate_gtd_maps(self):
        """Generates GTD maps and saves them as HTML files."""
        data_path = "page_3_threat_features/GTD_data/gtd_combined.csv"

        if not os.path.exists(data_path):
            print(f"Data file not found: {data_path}")
            return

        df = pd.read_csv(data_path, encoding="ISO-8859-1", low_memory=False)

        # Filter US and Non-US attacks
        us_attacks = df[df["country_txt"] == "United States"][:50]
        world_attacks = df[df["country_txt"] != "United States"][:50]

        us_attacks = us_attacks.dropna(subset=["latitude", "longitude"])
        world_attacks = world_attacks.dropna(subset=["latitude", "longitude"])


        # Function to create maps
        def create_map(attacks_df, title, output_file, center, zoom):
            """Generates a folium map with a title embedded on it."""
            m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

            # Add title as an HTML overlay inside the map
            title_html = f"""
            <div style="position: fixed; 
                        top: 10px; left: 50%; 
                        transform: translateX(-50%);
                        background-color: rgba(255, 255, 255, 0.8);
                        padding: 10px;
                        font-size: 16px;
                        font-weight: bold;
                        z-index:9999; 
                        border-radius: 5px;">
                {title}
            </div>
            """
            m.get_root().html.add_child(folium.Element(title_html))

            # Add the attack markers
            for _, row in attacks_df.iterrows():
                color = "red" if (row["iyear"] > 2001 and row["imonth"] > 9) else "yellow"
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=5,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=1.0,
                    tooltip=f"Attack type: {row['attacktype1_txt']}"
                ).add_to(m)

            # Add Legend
            legend_html = """
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 180px; height: 90px; 
                background-color: white; z-index:9999; font-size:14px;
                border-radius: 5px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                <b>Legend</b><br>
                <div style='background-color:red; width: 15px; height: 15px; display: inline-block;'></div> Post-9/11 Attacks <br>
                <div style='background-color:yellow; width: 15px; height: 15px; display: inline-block;'></div> Pre-9/11 Attacks <br>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            # Save map
            m.save(output_file)

        # Generate maps for US and World
        create_map(us_attacks, "Terrorist Attacks in the United States", self.us_map_path, [37.0902, -95.7129], 4)
        create_map(world_attacks, "Terrorist Attacks Outside the United States", self.world_map_path, [20, 0], 2)

    def setup_ui(self):
        """Sets up the UI layout with properly formatted map titles and spacing."""
        layout = QVBoxLayout()


        # Grid layout for two maps
        grid_layout = QGridLayout()

        # Web views for displaying maps
        self.map_views = [QWebEngineView(), QWebEngineView()]

        # Load generated maps
        self.map_views[0].setHtml(open(self.us_map_path).read())
        self.map_views[1].setHtml(open(self.world_map_path).read())


        grid_layout.addWidget(self.map_views[0], 1, 0)
        grid_layout.addWidget(self.map_views[1], 1, 1)

        # Adjust layout sizes
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(1, 1)

        # Add to main layout
        layout.addLayout(grid_layout)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GTDMapWindow()
    window.show()
    sys.exit(app.exec())
