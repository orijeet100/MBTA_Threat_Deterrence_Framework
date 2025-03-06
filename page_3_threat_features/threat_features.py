import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QComboBox, QLabel, QHBoxLayout, QSpinBox, QCheckBox, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QSize, QTimer
from visualizer import generate_threat_feature_map, nodes_df, layer_files
from page_2_map_with_features.map_features import MapFeaturesApp  # Import the centrality features window

# Load Available Time of Day CSVs
# threat_folder = "page_3_threat_features/Feature_Tables"
threat_folder = "page_3_threat_features/Feature_Label_with_Names_2025.02.24"
crime_folder = "page_3_threat_features/Crime_Data"  # Folder for crime heatmap data
# time_of_day_options = [
#     filename.replace("Feature_Table_", "").replace(".csv", "")
#     for filename in os.listdir(threat_folder) if filename.endswith(".csv")
# ]

time_of_day_options = [
    filename.replace("Feature_Label_with_Names_", "").replace(".csv", "")
    for filename in os.listdir(threat_folder) if filename.endswith(".csv")
]

# Default Time of Day
default_time = "EARLY_AM"

# Feature columns from the updated dataset
# feature_columns = [
#     "D_nearest_police", "D_nearest_fire", "D_nearest_hospital",
#     "Protection_Level", "Total_Population", "average_ridership",
#     "All_Crime_Index", "Threat_level"
# ]

feature_columns = [
    "D_nearest_police", "D_nearest_fire", "D_nearest_hospital",
    "Defense_Posture", "Population_Density", "Average_Ridership",
    "Crime_Index", "Threat_Level","Attractiveness"
]

class ThreatFeaturesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Threat Features of the Network")
        self.setGeometry(100, 40, 1200, 900)

        layout = QVBoxLayout()

        # **Button to open Centrality Features**
        self.centrality_button = QPushButton("📊 Centrality Features")
        self.centrality_button.setFixedSize(QSize(160, 30))
        self.centrality_button.clicked.connect(self.open_centrality_features)

        # Dropdown for Time of Day
        self.time_of_day_dropdown = QComboBox()
        self.time_of_day_dropdown.addItems(time_of_day_options)
        self.time_of_day_dropdown.setCurrentText(default_time)
        # self.time_of_day_dropdown.currentTextChanged.connect(self.update_features)

        # Dropdown for Feature Selection
        self.feature_dropdown = QComboBox()
        self.current_feature = "Crime_Index"  # Default feature
        self.feature_dropdown.addItems(feature_columns)
        self.feature_dropdown.setCurrentText(self.current_feature)
        # self.feature_dropdown.currentTextChanged.connect(self.update_map)
        self.feature_dropdown.currentTextChanged.connect(self.check_feature_type)


        # Top K Selector
        self.top_k_selector = QSpinBox()
        self.top_k_selector.setMinimum(1)
        self.top_k_selector.setMaximum(len(nodes_df))
        self.top_k_selector.setValue(len(nodes_df))  # Default: Show all nodes

        # "Go" Button for Top K Update
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.apply_filters)  # Connect this button to apply filters and update the map Connect this button to trigger the map update


        # **Checkboxes for External Layers (Police, Fire, Hospital)**
        self.layer_checkboxes = {}
        self.categorical_features = {"Defense_Posture", "Threat_Level"}
        layers_layout = QHBoxLayout()
        layers_layout.addWidget(QLabel("Toggle Layers: "))

        for layer_name in layer_files.keys():
            checkbox = QCheckBox(layer_name)
            checkbox.setChecked(False)  # Default: Layers off
            checkbox.stateChanged.connect(self.apply_filters)
            self.layer_checkboxes[layer_name] = checkbox
            layers_layout.addWidget(checkbox)

        # **HeatMap Toggle (Crime HeatMap)**
        self.heatmap_checkbox = QCheckBox("Show Crime HeatMap")
        self.heatmap_checkbox.setChecked(False)
        self.heatmap_checkbox.stateChanged.connect(self.apply_filters)

        # ✅ **Align HeatMap Toggle with Layer Toggles**
        layers_layout.addWidget(self.heatmap_checkbox)
        layers_layout.addStretch()  # Adds spacing between elements

        # Layouts
        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.centrality_button)  # Adding the new button
        top_row_layout.addWidget(QLabel("Time of Day:"))
        top_row_layout.addWidget(self.time_of_day_dropdown)
        top_row_layout.addWidget(QLabel("Feature:"))
        top_row_layout.addWidget(self.feature_dropdown)
        top_row_layout.addWidget(QLabel("Top K Nodes:"))
        top_row_layout.addWidget(self.top_k_selector)
        top_row_layout.addWidget(self.go_button)  # Add the "Go" button next to the Top K selector
        top_row_layout.addStretch()

        # Web View for displaying the map
        self.browser = QWebEngineView()
        # self.update_map()  # Generate initial map

        # Add widgets to layout
        layout.addLayout(top_row_layout)  # Includes new centrality button
        layout.addLayout(layers_layout)  # Layer + HeatMap toggles in same row
        layout.addWidget(self.browser)
        self.setLayout(layout)
        self.update_map(self.time_of_day_dropdown.currentText(), self.feature_dropdown.currentText(), self.top_k_selector.value())


    def open_centrality_features(self):
        """Opens the Centrality Features Window (MapFeaturesApp)."""
        self.centrality_window = MapFeaturesApp()
        self.centrality_window.show()

    def update_features(self):
        """ Updates feature dropdown when time of day changes while keeping selection intact. """
        selected_time = self.time_of_day_dropdown.currentText()
        current_feature = self.feature_dropdown.currentText()

        # Ensure previous selection exists in the new dropdown
        if current_feature in feature_columns:
            self.feature_dropdown.setCurrentText(current_feature)
        else:
            self.feature_dropdown.setCurrentText("Crime_Index")  # Default if previous selection is invalid

        self.check_feature_type(current_feature)

        # Update map after UI stabilizes
        QTimer.singleShot(100, self.apply_filters)

    def check_feature_type(self, feature):
        """ Enable or disable Top K Selector based on whether the feature is categorical """
        if feature in self.categorical_features:
            self.top_k_selector.setEnabled(False)
        else:
            self.top_k_selector.setEnabled(True)


    def apply_filters(self):
        """ Retrieves the selections and updates the map based on them. """
        selected_time = self.time_of_day_dropdown.currentText()
        selected_feature = self.feature_dropdown.currentText()
        top_k = self.top_k_selector.value() if self.top_k_selector.isEnabled() else None
        self.update_map(selected_time, selected_feature, top_k)

    def update_map(self, selected_time, selected_feature, top_k):
        """ Updates map based on selected feature, time of day, top K selection, and layer toggles """
        # selected_time = self.time_of_day_dropdown.currentText()
        # selected_feature = self.feature_dropdown.currentText()
        # top_k = self.top_k_selector.value()

        # Enable or disable Top K Selector based on feature type
        self.check_feature_type(selected_feature)

        # top_k = self.top_k_selector.value() if self.top_k_selector.isEnabled() else None

        # Get active layers
        active_layers = [layer for layer, checkbox in self.layer_checkboxes.items() if checkbox.isChecked()]

        # Check if HeatMap should be displayed
        show_heatmap = self.heatmap_checkbox.isChecked()

        map_path = generate_threat_feature_map(selected_time, selected_feature, top_k, active_layers, show_heatmap)
        if map_path:
            self.browser.setHtml(open(map_path).read())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThreatFeaturesApp()
    window.show()
    sys.exit(app.exec())
