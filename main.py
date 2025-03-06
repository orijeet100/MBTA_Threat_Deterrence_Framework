import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize

from page_3_threat_features.threat_features import ThreatFeaturesApp


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Machine Intelligence for Threat Deterrence")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f5f5f5;")

        layout = QVBoxLayout()

        # **Title Label**
        title_label = QLabel("Machine Intelligence for Threat Deterrence and Risk Mitigation at Soft Infrastructure Network Targets")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333; margin-bottom: 20px; margin-top: 10px")

        # **Grid Layout for Buttons & Images**
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)


        # **Button Definitions**
        self.threat_button = self.create_button("Network Data Visualization")
        self.dynamic_node_button = self.create_button("Dynamic Node Attractiveness Prediction")
        self.simulated_failure_button = self.create_button("Simulated Network Failure Curves")

        # **Image Paths**
        self.image_paths = {
            "Network Data Visualization": "info_logos/iloveimg-resized/first_page.png",
            "Dynamic Node Attractiveness Prediction": "info_logos/iloveimg-resized/second_page",
            "Simulated Network Failure Curves": "info_logos/iloveimg-resized/third_page"
        }

        # **Image Labels**
        self.image_labels = {
            "Network Data Visualization": self.add_image_label(self.image_paths["Network Data Visualization"]),
            "Dynamic Node Attractiveness Prediction": self.add_image_label(self.image_paths["Dynamic Node Attractiveness Prediction"]),
            "Simulated Network Failure Curves": self.add_image_label(self.image_paths["Simulated Network Failure Curves"])
        }

        # **Adding Buttons & Images to the Grid Layout**
        self.add_button_with_image(grid_layout, self.threat_button, self.image_labels["Network Data Visualization"], 0, 0)
        self.add_button_with_image(grid_layout, self.dynamic_node_button, self.image_labels["Dynamic Node Attractiveness Prediction"], 0, 1)
        self.add_button_with_image(grid_layout, self.simulated_failure_button, self.image_labels["Simulated Network Failure Curves"], 0, 2)

        self.threat_button.clicked.connect(self.open_threat_features)
        bottom_layout = QHBoxLayout()

        # **Spacer to Create Vertical Spacing**
        vertical_spacer = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # **Team Member Information Box**
        team_info_box = self.create_team_info_box()

        # **Adding Elements to the Layout**
        layout.addWidget(title_label)
        layout.addLayout(grid_layout)
        layout.addItem(vertical_spacer)

        # **Acknowledgment and Logos**
        bottom_layout = QHBoxLayout()

        # Acknowledgment label
        acknowledgment_label = QLabel(
            "This work is supported by DHS Center \n of Excellence: SENTRY.  Findings do not \n necessarily reflect the funding agency's views.")
        acknowledgment_label.setFont(QFont("Arial", 10))
        acknowledgment_label.setStyleSheet("color: #666;")
        bottom_layout.addWidget(acknowledgment_label)

        bottom_layout.addStretch()

        # Logos Label in the center
        logos_label = QLabel()
        logos_pixmap = QPixmap("info_logos/lab_logo.png")
        logos_label.setPixmap(logos_pixmap.scaled(300, 100, Qt.AspectRatioMode.KeepAspectRatio))
        logos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(logos_label)
        bottom_layout.addStretch()  # Ensures logos stay centered

        # Team Info Box on the right
        team_info_box = self.create_team_info_box()
        bottom_layout.addWidget(team_info_box)

        layout.addLayout(bottom_layout)
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
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QPushButton:pressed {
                background-color: #004c99;
            }
        """)
        return button

    def add_image_label(self, image_path):
        """Creates an image label with rounded corners and hover effect."""
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(QSize(150, 150), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            border-radius: 15px;
            border: 2px solid transparent;
        """)  # Rounded border

        return image_label

    def add_button_with_image(self, layout, button, image_label, row, col):
        """Adds button and image to the layout and links hover events."""
        layout.addWidget(button, row, col, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label, row + 1, col, Qt.AlignmentFlag.AlignCenter)

        # **Connect hover events to change image border**
        button.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handles hover event to add/remove a border around images."""
        if event.type() == event.Type.Enter:
            self.update_image_border(obj, True)
        elif event.type() == event.Type.Leave:
            self.update_image_border(obj, False)
        return super().eventFilter(obj, event)

    def update_image_border(self, button, hovered):
        """Updates the border of the corresponding image label when a button is hovered."""
        image_mapping = {
            self.threat_button: self.image_labels["Network Data Visualization"],
            self.dynamic_node_button: self.image_labels["Dynamic Node Attractiveness Prediction"],
            self.simulated_failure_button: self.image_labels["Simulated Network Failure Curves"]
        }

        if button in image_mapping:
            if hovered:
                image_mapping[button].setStyleSheet("""
                    border-radius: 15px;
                    border: 3px solid black;
                """)
            else:
                image_mapping[button].setStyleSheet("""
                    border-radius: 15px;
                    border: 2px solid transparent;
                """)

    def create_team_info_box(self):
        """Creates a team member information box with better contrast and spacing."""
        frame = QFrame()
        frame.setStyleSheet("""
            background-color: white;
            width: 400px;
            border-radius: 10px;
            padding: 10px;
        """)

        frame_layout = QVBoxLayout()

        # **Title**
        team_label = QLabel("📌 Team Members")
        team_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        team_label.setStyleSheet("color: black; margin-bottom: 5px;")  # Ensure text is visible
        frame_layout.addWidget(team_label)

        # **Team Members List**
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
            label.setStyleSheet("""
                color: black;
                padding: 2px;
            """)
            frame_layout.addWidget(label)

        frame.setLayout(frame_layout)
        return frame

    def open_threat_features(self):
        """Opens the ThreatFeaturesApp widget."""
        self.threat_window = ThreatFeaturesApp()
        self.threat_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
