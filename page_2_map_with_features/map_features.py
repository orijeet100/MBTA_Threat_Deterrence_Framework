import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QSpinBox, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QSize
from visualizer import generate_mbta_map_with_centrality, nodes_df

class MapFeaturesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MBTA Map with Centrality Features")
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout()

        # Dropdown Menu for Selecting Centrality
        self.centrality_dropdown = QComboBox()
        self.centrality_dropdown.addItems([
            "No Centrality", "Domirank", "Degree", "Betweenness", "Eigen Vector", "Closeness"
        ])
        self.centrality_dropdown.currentTextChanged.connect(self.update_map)

        # Top K Selector
        self.top_k_selector = QSpinBox()
        self.top_k_selector.setMinimum(0)
        self.top_k_selector.setMaximum(len(nodes_df))  # Max = total nodes
        self.top_k_selector.setValue(len(nodes_df))  # Default: All nodes are colored
        self.top_k_selector.valueChanged.connect(self.update_map)

        # Fix Dropdown Width
        self.centrality_dropdown.setFixedSize(QSize(120, 25))
        self.top_k_selector.setFixedSize(QSize(70, 25))

        # Label for Top K
        self.top_k_label = QLabel("Top K nodes")
        self.top_k_label.setFixedSize(QSize(80, 25))  # Adjust label width

        # Layout for controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.centrality_dropdown)
        control_layout.addWidget(self.top_k_label)
        control_layout.addWidget(self.top_k_selector)
        control_layout.addStretch()

        # Web View for displaying the map
        self.browser = QWebEngineView()

        # Generate default map
        self.update_map()

        layout.addLayout(control_layout)
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def update_map(self):
        selected_centrality = self.centrality_dropdown.currentText()
        top_k = self.top_k_selector.value()

        # Disable Top K selection when "No Centrality" is selected
        self.top_k_selector.setEnabled(selected_centrality != "No Centrality")

        # Generate updated map based on selection
        map_path = generate_mbta_map_with_centrality(selected_centrality, top_k)
        self.browser.setHtml(open(map_path).read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapFeaturesApp()
    window.show()
    sys.exit(app.exec())
