import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize

from page_3_threat_features.attractiveness_features import AttractivenessFeaturesApp
from page_3_threat_features.threat_features import ThreatFeaturesApp

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Machine Intelligence for Threat Deterrence")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #f5f5f5;")

        layout = QVBoxLayout()

        # Title Label
        title_label = QLabel("RC.1: Machine Intelligence for Threat Deterrence and Risk Mitigation at Soft Infrastructure Network Targets")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333; margin-bottom: 20px; margin-top: 10px")

        # Logo
        logo_label = QLabel(self)
        logo_pixmap = QPixmap("info_logos/sentry.png")
        logo_label.setPixmap(logo_pixmap.scaled(196, 199, Qt.AspectRatioMode.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # Description Label
        description_label = QLabel(
            "A hybrid knowledge-guided network science and machine learning system embedded with "
            "behavioral modeling and what-if simulations for predictive understanding of network-level "
            "threats leading to risk-informed policy and intervention or investment decisions."
        )
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("margin: 10px 100px; color: #666;")

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.threat_button = self.create_button("Network Data Visualization")
        self.dynamic_node_button = self.create_button("Dynamic Node Attractiveness Prediction")
        self.simulated_failure_button = self.create_button("Simulated Network Failure Curves")
        self.threat_button.clicked.connect(self.open_threat_features)
        self.dynamic_node_button.clicked.connect(self.open_attractiveness_features)
        buttons_layout.addWidget(self.threat_button)
        buttons_layout.addWidget(self.dynamic_node_button)
        buttons_layout.addWidget(self.simulated_failure_button)

        # Lower Grid Layout for acknowledgments, logos, and team info
        lower_grid_layout = QGridLayout()

        # Acknowledgment label
        acknowledgment_label = QLabel(
            "This work is supported by DHS Center of \n Excellence: SENTRY. Findings do not necessarily \n reflect the funding agency's views."
        )
        acknowledgment_label.setFont(QFont("Arial", 10))
        acknowledgment_label.setStyleSheet("color: #666;")

        # Logos Label
        logos_label = QLabel()
        logos_pixmap = QPixmap("info_logos/lab_logo.png")
        logos_label.setPixmap(logos_pixmap.scaled(348, 98, Qt.AspectRatioMode.KeepAspectRatio))
        logos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Team Information Box
        team_info_box = self.create_team_info_box()

        # Placing elements in the grid
        lower_grid_layout.addWidget(acknowledgment_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        lower_grid_layout.addWidget(logos_label, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        lower_grid_layout.addWidget(team_info_box, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add widgets to the main layout
        layout.addWidget(title_label)
        layout.addWidget(logo_label)
        layout.addWidget(description_label)
        layout.addLayout(buttons_layout)
        layout.addLayout(lower_grid_layout)  # Add the grid layout to the main layout

        self.setLayout(layout)

    def create_button(self, text):
        """Creates a styled button."""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet("""
            QPushButton {
                background-color: #0073e6;
                color: white;
                border-radius: 8px;
                padding: 10px;
                border: none;
                margin: 5px;
                width: 50px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QPushButton:pressed {
                background-color: #004c99;
            }
        """)
        button.setFixedSize(350, 50)
        return button

    def create_team_info_box(self):
        """Creates a team member information box with better contrast and spacing."""
        frame = QFrame()
        frame.setStyleSheet("""
            background-color: white;
            width: 300px;
            height: 150px;
            border-radius: 10px;
            padding: 10px;
        """)

        frame_layout = QVBoxLayout()
        team_label = QLabel("📌 Team Members")
        team_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        team_label.setStyleSheet("color: black; margin-bottom: 5px;")
        frame_layout.addWidget(team_label)

        team_members = [
            "Orijeet Mukherjee: mukherjee.o@northeastern.edu",
            "Dongqin Zhou: d.zhou@northeastern.edu",
            "Samrat Chatterjee: samrat.chatterjee@pnnl.gov",
            "Auroop Ganguly : auroop@gmail.com"
        ]

        for member in team_members:
            label = QLabel(member)
            label.setFont(QFont("Arial", 9))
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet("color: black; padding: 2px;")
            frame_layout.addWidget(label)

        frame.setLayout(frame_layout)
        return frame

    def open_threat_features(self):
        """Opens the ThreatFeaturesApp widget."""
        self.threat_window = ThreatFeaturesApp()
        self.threat_window.show()

    def open_attractiveness_features(self):
        """Opens the Attractiveness Features Window."""
        self.attractiveness_window = AttractivenessFeaturesApp()
        self.attractiveness_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
