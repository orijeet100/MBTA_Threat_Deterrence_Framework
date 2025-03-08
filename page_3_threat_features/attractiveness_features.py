import sys
import os
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QComboBox, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QSize, QUrl
from visualizer import generate_attractiveness_map

class AttractivenessFeaturesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attractiveness Map Visualization")
        self.setGeometry(100, 40, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Load Available Time of Day from files
        threat_folder = "page_3_threat_features/Feature_Label_with_Names_2025.02.24"
        time_of_day_options = [
            filename.replace("Feature_Label_with_Names_", "").replace(".csv", "")
            for filename in os.listdir(threat_folder) if filename.endswith(".csv")
        ]

        # Dropdown for Time of Day
        self.time_of_day_dropdown = QComboBox()
        self.time_of_day_dropdown.addItems(time_of_day_options)

        # Button to refresh the map
        self.refresh_button = QPushButton("Refresh Map")
        self.refresh_button.clicked.connect(self.update_map)

        # Web View for displaying the map
        self.browser = QWebEngineView()

        # Layout management
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Select Time of Day:"))
        top_layout.addWidget(self.time_of_day_dropdown)
        top_layout.addWidget(self.refresh_button)

        layout.addLayout(top_layout)
        layout.addWidget(self.browser)

        self.setLayout(layout)
        self.initial_load()

    def initial_load(self):
        """ Load the map for the first time with a default time of day. """
        self.time_of_day_dropdown.setCurrentText("EARLY_AM")
        self.update_map()

    def update_map(self):
        """ Load the map based on the selected time of day. """
        time_of_day = self.time_of_day_dropdown.currentText()
        map_html_path = generate_attractiveness_map(time_of_day)
        print(map_html_path)
        if map_html_path:
            self.browser.setHtml(open(map_html_path).read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttractivenessFeaturesApp()
    window.show()
    sys.exit(app.exec())
