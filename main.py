import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize

from page_3_threat_features.attractiveness_features import AttractivenessFeaturesApp
from page_3_threat_features.gtd_window import GTDMapWindow
from page_3_threat_features.threat_features import ThreatFeaturesApp

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Machine Intelligence for Threat Deterrence")

        # Start Maximized (Keeps Minimize & Close Buttons, Removes Resize)
        self.showMaximized()

        # Disable resizing but keep Minimize and Close buttons
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)


        self.setStyleSheet("background-color: #FFFFFF;")

        layout = QVBoxLayout()

        # Sentry Logo at the top left corner
        logo_label = QLabel(self)
        logo_pixmap = QPixmap("info_logos/sentry.png")
        logo_label.setPixmap(logo_pixmap.scaled(int(1641 / 4), int(595 / 4), Qt.AspectRatioMode.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo_label.setStyleSheet("padding-left: 20px; padding-top: 20px;")  # Left-top padding

        # Title Label
        title_label = QLabel("Machine Intelligence for Effective Threat Deterrence and Risk Mitigation at Soft Targets and Crowded Places (RC.1)")
        title_label.setFont(QFont("Arial", 17, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333; margin-bottom: 25px; margin-top: 20px")  # Reduced gap

        # Description Label
        description_label = QLabel(
            "A hybrid knowledge-guided network science and machine learning system embedded with "
            "behavioral modeling and what-if simulations \n for predictive understanding of network-level "
            "threats leading to risk-informed policy and intervention or investment decisions."
        )
        description_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("margin: 10px 20px; color: #666; padding-top: 5px;margin-bottom: 10px")  # Reduced gap above

        # Workflow diagram
        self.workflow_label = QLabel(self)  # Create QLabel
        workflow_pixmap = QPixmap("info_logos/workflow.png")  # Load image
        # self.workflow_label.setPixmap(
        #     workflow_pixmap.scaled(int(1280 / 2), int(275 / 2), Qt.AspectRatioMode.KeepAspectRatio))
        self.workflow_label.setPixmap(
            workflow_pixmap.scaled(int(2100 / 3), int(463 / 3), Qt.AspectRatioMode.KeepAspectRatio))
        self.workflow_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.workflow_label.setStyleSheet("padding-left: 20px; padding-top: 20px; padding-bottom: 5")  # Left-top padding

        # Workflow diagram caption
        caption_label = QLabel("Network risk modeling and simulation approach")
        caption_label.setFont(QFont("Arial", 12, QFont.Weight.Medium))
        caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption_label.setStyleSheet("color: #333; margin-bottom: 10px;padding-bottom: 5")  # Reduced gap

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.threat_button = self.create_button("Urban Rail Network Data Analysis")
        self.dynamic_node_button = self.create_button("Rail Station Attractiveness Prediction")
        self.gtd_button = self.create_button("Global Terrorism Data Visualization")
        self.threat_button.clicked.connect(self.open_threat_features)
        self.dynamic_node_button.clicked.connect(self.open_attractiveness_features)
        self.gtd_button.clicked.connect(self.open_gtd_maps)
        buttons_layout.addWidget(self.gtd_button)
        buttons_layout.addWidget(self.threat_button)
        buttons_layout.addWidget(self.dynamic_node_button)


        # Lower Grid Layout for acknowledgments, logos, and team info
        lower_grid_layout = QGridLayout()

        # Acknowledgment label
        acknowledgment_label = QLabel(
            "This material is based upon work supported by the U.S. Department of Homeland Security \n "
            " under Grant Award 22STESE00001-04-00. The views and conclusions contained in this document \n"
            "are those of the authors and should not be interpreted as necessarily representing the official \n "
            "policies, either expressed or implied, of the U.S. Department of Homeland Security. \n"
        )
        acknowledgment_label.setFont(QFont("Arial", 10,QFont.Weight.Bold))
        acknowledgment_label.setStyleSheet("color: #666;")


        # Team Information Box
        team_info_box = self.create_team_info_box()

        # Placing elements in the grid
        lower_grid_layout.addWidget(acknowledgment_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        lower_grid_layout.addWidget(team_info_box, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        spacer = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum,
                             QSizePolicy.Policy.Expanding)  # Increased gap below buttons

        # Add widgets to the main layout
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(self.workflow_label)
        layout.addWidget(caption_label)
        layout.addLayout(buttons_layout)
        # layout.addItem(spacer)  # Adds extra space below buttons
        layout.addLayout(lower_grid_layout)  # Add the grid layout to the main layout
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Expanding))  # Adds extra space below buttons

        self.setLayout(layout)

    def create_button(self, text):
        """Creates a styled button."""
        button = QPushButton(text)
        button.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                background-color: #0073e6;
                color: white;
                border-radius: 8px;
                padding: 10px;
                border: none;
                margin: 5px;
                width: 60px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QPushButton:pressed {
                background-color: #004c99;
            }
        """)
        button.setFixedSize(380, 65)
        return button

    def create_team_info_box(self):
        """Creates a plain-text team members box."""
        frame = QFrame()
        frame.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border: 0px solid #ccc;
        """)

        frame_layout = QVBoxLayout()

        team_label = QLabel("Team Members")
        team_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        team_label.setStyleSheet("color: black; margin-bottom: 0px;")

        team_text = QLabel(
            "Auroop Ganguly1,2 (PI and POC)*, Samrat Chatterjee2,1 (Co-PI)**\n"
            "Postdoctoral Researcher: Dongqin Zhou\n"
            "Graduate Student: Orijeet Mukherjee\n"
            "Postgraduate Researcher: Soumyo Dey\n\n"
            "1 Northeastern University, Boston, MA\n"
            "2 Pacific Northwest National Laboratory, Richland, WA"
        )

        team_text.setFont(QFont("Arial", 12))
        team_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        team_text.setWordWrap(True)
        team_text.setStyleSheet("color: black; padding: 2px;")

        frame_layout.addWidget(team_label)
        frame_layout.addWidget(team_text)
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

    def open_gtd_maps(self):
        """Opens a new window displaying two GTD maps: US and Global"""
        self.gtd_window = GTDMapWindow()
        self.gtd_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
