# creating UI for practice animations
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtGui import QColor, QIcon, QPixmap, QFont
from PyQt5.QtCore import QPropertyAnimation
from pyqtgraph import PlotWidget
import folium
from io import BytesIO

class party(QMainWindow):
    # creating main window
    def __init__(self):
        super().__init__()
        
        # setting up style of background of window
        self.setGeometry(100, 100, 1024, 600)
        self.setStyleSheet("background-color: #cce5ff;")
        self.setWindowTitle("Vortex Base Station")
        self.setWindowIcon(QIcon('Vortex_Logo.png'))
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)




# opening main window
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = party()
    window.show()
    app.exec()