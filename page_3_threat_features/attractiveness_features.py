import sys
import os
import shutil
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QComboBox, QLabel,
    QHBoxLayout, QPushButton, QGridLayout, QSpinBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from visualizer import generate_attractiveness_map, nodes_df, generate_overlay_singular_map


# ,generate_overlay_singular_map


class AttractivenessFeaturesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attractiveness & Threat Features")
        self.setGeometry(100, 40, 1200, 800)

        # Create temp playground directory if not exists
        self.source_folder = "page_3_threat_features/Feature_Label"
        self.temp_folder = "page_3_threat_features/temp_playground"
        self.create_temp_playground()

        self.setup_ui()

    def create_temp_playground(self):
        """ Copies original feature files to a temporary directory for modifications. """
        if os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder)  # Clear existing temp files
        shutil.copytree(self.source_folder, self.temp_folder)  # Copy fresh files

    def setup_ui(self):
        layout = QVBoxLayout()

        # Load Available Time of Day from files
        time_of_day_options = [
            filename.replace("Feature_Label_", "").replace(".csv", "")
            for filename in os.listdir(self.temp_folder) if filename.endswith(".csv")
        ]

        # Dropdown for Time of Day
        self.time_of_day_dropdown = QComboBox()
        self.time_of_day_dropdown.addItems(time_of_day_options)
        self.time_of_day_dropdown.setCurrentText("EARLY_AM")  # Default
        self.time_of_day_dropdown.currentTextChanged.connect(self.update_map)

        # Station Dropdown
        self.station_dropdown = QComboBox()
        self.station_dropdown.addItems(sorted(nodes_df["stop_name"].unique()))  # Sorted alphabetically

        # Feature Dropdown
        self.feature_dropdown = QComboBox()
        self.feature_dropdown.addItems(["Threat_Level", "Defense_Posture"])
        self.feature_dropdown.setCurrentText("Defense_Posture")  # Default
        self.feature_dropdown.currentTextChanged.connect(self.update_feature_level_dropdown)

        # Feature Level Dropdown (Defaults to "Low")
        self.feature_level_dropdown = QComboBox()
        self.feature_level_dropdown.addItems(["High", "Medium", "Low"])
        self.feature_level_dropdown.setCurrentText("Low")

        # Simulate Button
        self.simulate_button = QPushButton("Simulate")
        self.simulate_button.clicked.connect(self.simulate_change)

        # Overlay Features Button
        self.overlay_button = QPushButton("Overlay Features")
        self.overlay_button.clicked.connect(self.open_overlay_window)

        # Web View for displaying the map
        self.browser = QWebEngineView()

        # Layout management
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Select Time of Day:"))
        top_layout.addWidget(self.time_of_day_dropdown)
        top_layout.addWidget(QLabel("Select Station:"))
        top_layout.addWidget(self.station_dropdown)
        top_layout.addWidget(QLabel("Select Feature:"))
        top_layout.addWidget(self.feature_dropdown)
        top_layout.addWidget(self.feature_level_dropdown)
        top_layout.addWidget(self.simulate_button)
        top_layout.addWidget(self.overlay_button)
        top_layout.addStretch()

        layout.addLayout(top_layout)
        layout.addWidget(self.browser)

        self.setLayout(layout)
        self.update_map()  # Initialize the map on startup

    def update_feature_level_dropdown(self):
        """ Ensures that 'High', 'Medium', 'Low' appear only when relevant. """
        selected_feature = self.feature_dropdown.currentText()
        self.feature_level_dropdown.setVisible(selected_feature in ["Threat_Level", "Defense_Posture"])

    def update_map(self):
        """ Loads the map based on the selected parameters. """
        time_of_day = self.time_of_day_dropdown.currentText()
        map_html_path = generate_attractiveness_map(time_of_day)
        if map_html_path:
            self.browser.setHtml(open(map_html_path).read())

    def simulate_change(self):
        """ Modifies the selected feature's value for the selected station and updates the temp dataset. """
        time_of_day = self.time_of_day_dropdown.currentText()
        station_name = self.station_dropdown.currentText()
        feature = self.feature_dropdown.currentText()
        new_value = self.feature_level_dropdown.currentText()

        csv_file = f"Feature_Label_{time_of_day}.csv"
        file_path = os.path.join(self.temp_folder, csv_file)

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        # Load the CSV and modify the selected station's feature
        df = pd.read_csv(file_path)
        df.loc[df["Station_Name"] == station_name, feature] = new_value
        df.to_csv(file_path, index=False)

        # Refresh the map
        self.update_map()

    def open_overlay_window(self):
        """ Opens a new window to show the overlay maps. """
        self.overlay_window = OverlayMapWindow(self.time_of_day_dropdown.currentText())
        self.overlay_window.show()


class OverlayMapWindow(QWidget):
    def __init__(self, time_of_day):
        super().__init__()
        self.setWindowTitle("Overlay Feature Maps")
        self.setGeometry(50, 50, 1400, 900)
        self.time_of_day = time_of_day
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Feature selection dropdowns
        feature_columns_overlay = [
            "D_nearest_police", "D_nearest_fire", "D_nearest_hospital",
            "Population_Density", "Average_Ridership",
            "Crime_Index", "Attractiveness"
        ]

        self.feature_dropdowns = [QComboBox() for _ in range(3)]
        for dropdown in self.feature_dropdowns:
            dropdown.addItems(feature_columns_overlay)

        self.top_k_selector = QSpinBox()
        self.top_k_selector.setMinimum(1)
        self.top_k_selector.setMaximum(len(nodes_df))
        self.top_k_selector.setValue(len(nodes_df))  # Default: Show all nodes

        self.generate_button = QPushButton("Generate Overlay Maps")
        self.generate_button.clicked.connect(self.generate_overlay_maps)

        # Dropdown Layout
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(QLabel("Feature 1:"))
        dropdown_layout.addWidget(self.feature_dropdowns[0])
        dropdown_layout.addWidget(QLabel("Feature 2:"))
        dropdown_layout.addWidget(self.feature_dropdowns[1])
        dropdown_layout.addWidget(QLabel("Feature 3:"))
        dropdown_layout.addWidget(self.feature_dropdowns[2])
        dropdown_layout.addWidget(QLabel("Top K:"))
        dropdown_layout.addWidget(self.top_k_selector)
        dropdown_layout.addWidget(self.generate_button)
        dropdown_layout.addStretch()

        layout.addLayout(dropdown_layout)

        # Web views for the 4 maps
        self.map_views = [QWebEngineView() for _ in range(4)]
        grid_layout = QGridLayout()
        for i, view in enumerate(self.map_views):
            grid_layout.addWidget(view, i // 2, i % 2)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def generate_overlay_maps(self):
        """ Generates overlay maps and loads them into the window. """
        features = [dropdown.currentText() for dropdown in self.feature_dropdowns]
        top_k = self.top_k_selector.value()

        # Generate paths for the 3 individual feature maps
        map_paths = [
            generate_overlay_singular_map(self.time_of_day, feature, top_k, common=False)
            for feature in features
        ]

        # Generate the common nodes overlay map
        common_map_path = generate_overlay_singular_map(self.time_of_day, features, top_k, common=True)

        # Update the UI with the new maps
        all_maps = map_paths + [common_map_path]  # Combine individual maps with the common overlay

        for i, view in enumerate(self.map_views):
            view.setHtml(open(all_maps[i]).read())  # Load the generated HTML maps



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttractivenessFeaturesApp()
    window.show()
    sys.exit(app.exec())
