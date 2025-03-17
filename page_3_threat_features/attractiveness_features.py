import sys
import os
import shutil

import numpy as np
import pandas as pd
import torch
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QComboBox, QLabel,
    QHBoxLayout, QPushButton, QGridLayout, QSpinBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from numpy import genfromtxt
from page_3_threat_features.GCN.gcn_lstm import GCN_LSTM
from visualizer import generate_attractiveness_map, nodes_df, generate_overlay_singular_map



class AttractivenessFeaturesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attractiveness & Threat Features")
        self.setGeometry(100, 40, 1200, 800)

        # Create temp playground directory if not exists
        self.source_folder = "page_3_threat_features/Feature_Label"
        self.temp_folder = "page_3_threat_features/temp_playground"
        self.gcn_folder = "page_3_threat_features/GCN"
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

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_temp_playground)

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
        top_layout.addWidget(self.reset_button)
        top_layout.addStretch()
        top_layout.addWidget(self.overlay_button)

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
        """Updates the selected feature's value, runs GCN-LSTM, and updates Attractiveness scores."""
        time_of_day = self.time_of_day_dropdown.currentText()
        station_name = self.station_dropdown.currentText()
        feature = self.feature_dropdown.currentText()
        new_value = self.feature_level_dropdown.currentText()

        csv_file = f"Feature_Label_{time_of_day}.csv"
        file_path = os.path.join(self.temp_folder, csv_file)

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df.loc[df["Station_Name"] == station_name, feature] = new_value
        df.to_csv(file_path, index=False)

        print(f"✅ Updated {feature} for {station_name}. Running GCN-LSTM...")

        # Pass required arguments to `run_gcn_lstm`
        self.run_gcn_lstm(updated_station=station_name, updated_feature=feature, new_value=new_value,
                          time_of_day=time_of_day)

    def run_gcn_lstm(self, updated_station, updated_feature, new_value, time_of_day):
        """
        Runs the GCN-LSTM model after updating the latest time step's features.
        Updates the `Attractiveness` scores in `temp_playground` and refreshes the map.
        """
        print(f"🔄 Running GCN-LSTM with updated {updated_feature} for {updated_station}...")

        # Define paths using self variables
        model_path = os.path.join(self.gcn_folder, "GCN_LSTM_weights.pth")
        features_path = os.path.join(self.gcn_folder, "Original_Features.pth")
        edge_index_path = os.path.join(self.gcn_folder, "edge_index.csv")

        # Load the model
        model = GCN_LSTM(input_dim=12, hidden_dim=64, output_dim=1, time_steps=9)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()

        # Load node features (sequence of tensors)
        features_seq = torch.load(features_path, map_location=torch.device('cpu'))  # List of 9 tensors
        latest_features = features_seq[-1].clone()  # Work on the last time step tensor

        # Load edge index
        edge_index_np = pd.read_csv(edge_index_path, header=None).values
        edge_index = torch.tensor(edge_index_np, dtype=torch.long).t().contiguous()

        # Load temp playground CSV
        csv_file = f"Feature_Label_{time_of_day}.csv"
        file_path = os.path.join(self.temp_folder, csv_file)
        df = pd.read_csv(file_path)

        # Get node index for the selected station
        station_idx = df.index[df["Station_Name"] == updated_station].tolist()
        if not station_idx:
            print(f"❌ Station {updated_station} not found in dataset.")
            return
        station_idx = station_idx[0]

        # One-hot encoding for categorical features
        if updated_feature in ["Threat_Level", "Defense_Posture"]:
            one_hot_columns = {
                "Threat_Level": ["Threat_Level_Low", "Threat_Level_Medium", "Threat_Level_High"],
                "Defense_Posture": ["Defense_Posture_Low", "Defense_Posture_Medium", "Defense_Posture_High"]
            }
            # Reset other categories to 0
            latest_features[station_idx, -3:] = 0
            if updated_feature in one_hot_columns:
                level_map = {"Low": 0, "Medium": 1, "High": 2}
                latest_features[station_idx, -3 + level_map[new_value]] = 1  # Set the correct one-hot feature
        else:
            # Update numerical feature directly
            feature_idx = {
                "D_nearest_police": 0, "D_nearest_fire": 1, "D_nearest_hospital": 2,
                "Population_Density": 3, "Average_Ridership": 4, "Crime_Index": 5
            }
            if updated_feature in feature_idx:
                latest_features[station_idx, feature_idx[updated_feature]] = float(new_value)

        # Update the last time step in the feature sequence
        features_seq[-1] = latest_features

        # Run model inference
        with torch.no_grad():
            predictions = model(torch.stack(features_seq), edge_index)  # Output shape: [114, 9, 1]

        # Extract final time step predictions
        attractiveness_scores = predictions[:, -1, 0].numpy()

        # Update temp playground CSV with new scores
        df["Attractiveness"] = attractiveness_scores
        df.to_csv(file_path, index=False)

        print(f"✅ Updated Attractiveness scores in {file_path}")

        # 🔄 **Refresh the map after updates**
        self.update_map()


    def extract_features(self, file_path):
        """Extracts 12 required features, applies one-hot encoding, and returns tensor."""
        df = pd.read_csv(file_path)

        # Features: 3 distances, 1 population density, 1 ridership, 1 crime index
        feature_columns = [
            "D_nearest_police", "D_nearest_fire", "D_nearest_hospital",
            "Population_Density", "Average_Ridership", "Crime_Index"
        ]

        # One-hot encode Threat_Level & Defense_Posture
        for category in ["Threat_Level", "Defense_Posture"]:
            for level in ["High", "Medium", "Low"]:
                column_name = f"{category}_{level}"
                df[column_name] = (df[category] == level).astype(int)
                feature_columns.append(column_name)

        return torch.tensor(df[feature_columns].values, dtype=torch.float)

    def reset_temp_playground(self):
        """ Restores the temp playground to its original state. """
        self.create_temp_playground()  # Re-copy the original files
        self.update_map()  # Refresh the map to reflect reset data

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
            "D_nearest_police", "D_nearest_fire", "D_nearest_hospital","D_police_fire",
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
