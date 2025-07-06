import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
from visualizer import generate_mbta_map_without_features

class MBTAMapApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MBTA Map Viewer (No Features)")
        self.setGeometry(100, 100, 900, 600)

        # Generate the MBTA Map without additional features
        map_path = generate_mbta_map_without_features()

        layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.browser.setHtml(open(map_path).read())

        layout.addWidget(self.browser)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MBTAMapApp()
    window.show()
    sys.exit(app.exec())
