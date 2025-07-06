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
from numpy import genfromtxt

from page_3_threat_features.GCN.gcn_lstm import GCN_LSTM
from visualizer import generate_attractiveness_map, nodes_df, generate_overlay_singular_map



class AttractivenessFeaturesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rail Station Attractiveness Prediction")
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
        # time_of_day_options = [
        #     filename.replace("Feature_Label_", "").replace(".csv", "")
        #     for filename in os.listdir(self.temp_folder) if filename.endswith(".csv")
        # ]
        time_of_day_options = ["VERY_EARLY_MORNING", "EARLY_AM", "AM_PEAK", "MIDDAY_BASE",
                               "MIDDAY_SCHOOL", "PM_PEAK", "EVENING", "LATE_EVENING", "NIGHT"]

        # Dropdown for Time of Day
        self.time_of_day_dropdown = QComboBox()
        self.time_of_day_dropdown.addItems(time_of_day_options)
        self.time_of_day_dropdown.setCurrentText("VERY_EARLY_MORNING")  # Default
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

    # def simulate_change(self):
    #     """ Modifies the selected feature's value for the selected station and updates the temp dataset with GCN-LSTM predictions. """
    #     time_of_day = self.time_of_day_dropdown.currentText()
    #     station_name = self.station_dropdown.currentText()
    #     feature = self.feature_dropdown.currentText()
    #     new_value = self.feature_level_dropdown.currentText()
    #
    #     csv_file = f"Feature_Label_{time_of_day}.csv"
    #     file_path = os.path.join(self.temp_folder, csv_file)
    #
    #     if not os.path.exists(file_path):
    #         print(f"File not found: {file_path}")
    #         return
    #
    #     # ✅ 1. Load the CSV and modify the selected station's feature
    #     df = pd.read_csv(file_path)
    #     df.loc[df["Station_Name"] == station_name, feature] = new_value
    #     df.to_csv(file_path, index=False)  # Save the update
    #
    #     # ✅ 2. Load the GCN-LSTM Model
    #     model_path = os.path.join(self.gcn_folder, "GCN_LSTM_weights.pth")
    #     if not os.path.exists(model_path):
    #         print("GCN-LSTM model weights not found!")
    #         return
    #
    #     model = GCN_LSTM(input_dim=12, hidden_dim=64, output_dim=1, time_steps=9)
    #     model.load_state_dict(torch.load(model_path))
    #     model.eval()
    #
    #     # ✅ 3. Load Graph Structure
    #     edge_index = np.genfromtxt(os.path.join(self.gcn_folder, "edge_index.csv"), delimiter=",", dtype=int)
    #     edge_index = torch.tensor(edge_index.T, dtype=torch.long)  # Ensure correct shape
    #
    #     # ✅ 4. Extract Features for the Last 9 Time Windows
    #     time_windows = [
    #         "VERY_EARLY_MORNING", "EARLY_AM", "AM_PEAK", "MIDDAY_BASE",
    #         "MIDDAY_SCHOOL", "PM_PEAK", "EVENING", "LATE_EVENING", "NIGHT"
    #     ]
    #
    #     feature_tensors = []
    #     for t in time_windows:
    #         file_t = os.path.join(self.temp_folder, f"Feature_Label_{t}.csv")
    #         if not os.path.exists(file_t):
    #             print(f"Missing time window file: {file_t}")
    #             return
    #
    #         df_t = pd.read_csv(file_t)
    #         feature_values = df_t.set_index("Station_Name").loc[:, feature]  # Extract feature column
    #         feature_tensors.append(torch.tensor(feature_values.values, dtype=torch.float32))
    #
    #     # ✅ 5. Stack the extracted features into a sequence
    #     features_sequence = torch.stack(feature_tensors)  # Shape: [9, num_nodes]
    #
    #     # ✅ 6. Make Predictions
    #     with torch.no_grad():
    #         predicted_values = model(features_sequence.unsqueeze(0), edge_index)  # Add batch dimension
    #         predicted_values = predicted_values.squeeze(0)  # Remove batch dim
    #
    #     # ✅ 7. Save Predictions to the Temp Playground
    #     for i, t in enumerate(time_windows):
    #         file_t = os.path.join(self.temp_folder, f"Feature_Label_{t}.csv")
    #         df_t = pd.read_csv(file_t)
    #         df_t.loc[df_t["Station_Name"] == station_name, feature] = predicted_values[i].item()
    #         df_t.to_csv(file_t, index=False)
    #
    #     print(f"Updated predictions saved for {station_name} in all time windows.")
    #
    #     # ✅ 8. Refresh the Map with the New Data
    #     self.update_map()

    def simulate_change(self):
        """ Modifies the selected feature's value for the selected station, runs the GCN-LSTM model,
            and updates 'Attractiveness' in temp files for all 9 time windows. """

        time_windows = [
            "VERY_EARLY_MORNING", "EARLY_AM", "AM_PEAK", "MIDDAY_BASE",
            "MIDDAY_SCHOOL", "PM_PEAK", "EVENING", "LATE_EVENING", "NIGHT"
        ]

        time_of_day = self.time_of_day_dropdown.currentText()
        station_name = self.station_dropdown.currentText()
        feature = self.feature_dropdown.currentText()
        new_value = self.feature_level_dropdown.currentText()

        csv_file = f"Feature_Label_{time_of_day}.csv"
        file_path = os.path.join(self.temp_folder, csv_file)

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        # 🔹 Step 1: Load the CSV file from temp_playground
        df = pd.read_csv(file_path)

        # 🔹 Step 2: Apply the manual change
        df.loc[df["Station_Name"] == station_name, feature] = new_value

        # 🔹 Step 3: Save the updated dataframe back to temp_playground
        df.to_csv(file_path, index=False)

        # 🔹 Step 4: Reload the updated dataset before running the model
        df = pd.read_csv(file_path)

        # ✅ Load Edge Index
        edge_index = np.genfromtxt(os.path.join(self.gcn_folder, "edge_index.csv"), delimiter=',', dtype=int)
        # Ensure edge_index is a 2-row tensor (2, num_edges)
        if edge_index.shape[0] != 2:
            edge_index = edge_index.T  # Transpose if needed

        # Convert to PyTorch tensor (2, num_edges)
        edge_index = torch.tensor(edge_index, dtype=torch.long)

        # ✅ Load Original Features
        features = []
        for time in time_windows:
            csv_path = os.path.join(self.temp_folder, f"Feature_Label_{time}.csv")
            df = pd.read_csv(csv_path)

            # Apply the change for the selected station and feature
            df.loc[df["Station_Name"] == station_name, feature] = new_value

            # Convert Threat_Level and Defense_Posture to One-Hot Encoding dynamically
            categorical_features = ["Threat_Level", "Defense_Posture"]
            df = pd.get_dummies(df, columns=categorical_features)

            # Final selected features for prediction
            all_feature_columns = [
                                      "D_nearest_police", "D_nearest_fire", "D_nearest_hospital",
                                      "Population_Density", "Average_Ridership", "Crime_Index"
                                  ] + [col for col in df.columns if
                                       "Threat_Level_" in col or "Defense_Posture_" in col]  # Dynamically get one-hot columns

            # Ensure correct column order and convert to numeric
            df = df[["ID"] + all_feature_columns].copy()
            df[all_feature_columns] = df[all_feature_columns].astype(float)
            df.sort_values(by="ID", inplace=True)  # Ensure consistent order
            features.append(torch.tensor(df[all_feature_columns].values, dtype=torch.float32))

        # ✅ Stack tensors to shape (9, num_nodes, num_features)
        features_tensor = torch.stack(features)  # Shape: (9, num_nodes, num_features)

        # ✅ Load Pretrained GCN-LSTM Model
        model_path = os.path.join(self.gcn_folder, "GCN_LSTM_weights.pth")
        model = GCN_LSTM(input_dim=features_tensor.shape[2], hidden_dim=64, output_dim=1, time_steps=9, gcn_dropout=0.5,
                         lstm_dropout=0)
        model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
        model.eval()

        # ✅ Run Predictions
        with torch.no_grad():
            attractiveness_predictions = model(features_tensor, edge_index)  # Shape: (9, num_nodes, 1)

        # ✅ Update Attractiveness in all CSV files
        for i, time in enumerate(time_windows):
            csv_path = os.path.join(self.temp_folder, f"Feature_Label_{time}.csv")
            df = pd.read_csv(csv_path)
            # Extract predictions for the correct time step
            df["Attractiveness"] = attractiveness_predictions[:, i, 0].numpy()  # Extracts predictions for time step i
            df.to_csv(csv_path, index=False)  # Save updated CSV

        print("Updated Attractiveness values for all time slots.")

        # ✅ Refresh UI
        self.update_map()

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
