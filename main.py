# main window for user interface
# 14 px minimum font size
# launchpad coordinates 38.37583 deg N, -79.6078 deg E
# cd96ff

# importing necessary libraries
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QLabel, QTableWidget, QPushButton, QHeaderView, QFrame
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QColor, QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import folium
from io import BytesIO
from read_data import live_read

dark_blue = QtGui.QColor(0, 107, 163)
class GCS(QMainWindow):
    # creating main window
    def __init__(self):
        super().__init__()
        
        # determining screen size
        # avGeom = QDesktopWidget().availableGeometry()
        # avGeom.setTop(24)
        # self.setGeometry(avGeom)

        # setting up style of background of window
        self.setGeometry(100, 100, 1024, 600)
        self.setStyleSheet("background-color: #cce5ff;")
        self.setWindowTitle("Vortex Base Station")
        self.setWindowIcon(QIcon('Vortex_Logo.png'))
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # setting up layout and making universal font
        base_layout = QHBoxLayout()
        final_layout = QVBoxLayout(self.central_widget)

        # data table and buttons side of screen
        data_layout = QVBoxLayout()
        data_layout.setSpacing(10)

        # making the data table
        # table_frame = QFrame(data_table)
        # table_frame.setStyleSheet('border: 5px solid #cd96ff')
        data_table = QTableWidget()
        data_table.setStyleSheet('background-color: white; font-family: roboto; font-size: 14px; font-weight: bold')
        data_table.horizontalHeader().setVisible(False)
        data_table.setEditTriggers(QTableWidget.NoEditTriggers) # so that table cannot be edited live
        data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data_table.horizontalHeader().setStretchLastSection(True)
        data_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        data_table.setGridStyle(Qt.SolidLine)
        data_table.setColumnCount(1)
        data_table.setRowCount(9)
        row_labels = [
            'Mission Time', 
            'Packet Count',
            'Recieved Packets', 
            'Lost Packets', 
            'Payload Release',
            'Egg Release', 
            'GPS Latitude', 
            'GPS Longitude',
            'Satellites'
            ]
        data_table.setVerticalHeaderLabels(row_labels)
        data_layout.addWidget(data_table, 1)

        # making the button layout
        button_layout = QGridLayout()
        # button_layout.setSpacing(10)
        sim_enable = QPushButton()
        cx_on = QPushButton()
        cx_on.setText('CX On')
        cx_on.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        cx_off = QPushButton()
        cx_off.setText('CX Off')
        cx_off.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        sim_enable.setText('SIM Enable')
        sim_enable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        sim_activate = QPushButton()
        sim_activate.setText('SIM Activate')
        sim_activate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        sim_disable = QPushButton()
        sim_disable.setText('SIM Disable')
        sim_disable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        lock = QPushButton()
        lock.setText('Lock')
        lock.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        probe_release = QPushButton()
        probe_release.setText('Egg Drop')
        probe_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        para_deploy = QPushButton()
        para_deploy.setText('Release')
        para_deploy.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        calibrate = QPushButton()
        calibrate.setText('Calibrate')
        calibrate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        set_time = QPushButton()
        set_time.setText('Set Time')
        set_time.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        # party_mode = QPushButton()
        # party_mode.setText('Party Mode')
        # party_mode.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        button_layout.addWidget(sim_enable, 0, 0)
        button_layout.addWidget(sim_activate, 0, 1)
        button_layout.addWidget(sim_disable, 1, 0)
        button_layout.addWidget(lock, 1, 1)
        button_layout.addWidget(cx_on, 2, 0)
        button_layout.addWidget(cx_off, 2, 1)
        button_layout.addWidget(calibrate, 3, 0)
        button_layout.addWidget(set_time, 3, 1)
        button_layout.addWidget(para_deploy, 4, 0)
        button_layout.addWidget(probe_release, 4, 1)
        # button_layout.addWidget(party_mode, 4, 1)
        data_layout.addLayout(button_layout, 1)

        # graph side layout
        graph_layout = QGridLayout()
        graph_layout.setSpacing(5)

        # TEMPORARY FOR VISUAL PURPOSES
        latitude = [38.37583] 
        longitude = [-79.6078] 
        GPS = folium.Map(location = [latitude[0], longitude[0]], zoom_start=13) 
        icon = folium.CustomIcon('ufo.png', icon_size = (75,75)) 
        folium.Marker(location = [latitude[0], longitude[0]], popup = 'Payload', icon = icon).add_to(GPS) 
        data = BytesIO()
        GPS.save(data,close_file = False)
        html = data.getvalue().decode()
        webView = QWebEngineView(self)
        webView.setHtml(html) 

        alt_graph = PlotWidget() # placeholder graphs
        alt_graph.setBackground('white')
        alt_graph.setStyleSheet('border: 5px solid #006ba3')
        alt_graph.setTitle('Altitude', color = 'k', **{'font-size':'14pt', 'font-family':'Times New Roman'})
        alt_graph.setLabel("left", "Altitude (m)", color = "k", **{'font-size':'12pt'})
        alt_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        alt_graph.showGrid(x=True, y=True)
        # alt_graph.setStyleSheet('text-size: 16px; text-weight: bold')

        volt_graph = PlotWidget() # placeholder graphs
        volt_graph.setBackground('white')
        volt_graph.setStyleSheet('border: 5px solid #006ba3')
        volt_graph.setTitle('Voltage', color = 'k', **{'font-size':'14pt'})
        volt_graph.setLabel("left", "Voltage (V)", color = "k", **{'font-size':'12pt'})
        volt_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        volt_graph.showGrid(x=True, y=True)

        curr_graph = PlotWidget() # placeholder graphs
        curr_graph.setBackground('white')
        curr_graph.setStyleSheet('border: 5px solid #006ba3')
        curr_graph.setTitle('Current', color = 'k', **{'font-size':'14pt'})
        curr_graph.setLabel("left", "Current (A)", color = "k", **{'font-size':'12pt'})
        curr_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        curr_graph.showGrid(x=True, y=True)

        accel_graph = PlotWidget() # placeholder graphs
        accel_graph.setBackground('white')
        accel_graph.setStyleSheet('border: 5px solid #006ba3')
        accel_graph.setTitle('Acceleration', color = 'k', **{'font-size':'14pt'})
        accel_graph.setLabel("left", "Acceleration (deg/s^2)", color = "k", **{'font-size':'12pt'})
        accel_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        accel_graph.showGrid(x=True, y=True)

        gyro_graph = PlotWidget() # placeholder graphs
        gyro_graph.setBackground('white')
        gyro_graph.setStyleSheet('border: 5px solid #006ba3')
        gyro_graph.setTitle('Rotation', color = 'k', **{'font-size':'14pt'})
        gyro_graph.setLabel("left", "Rotation (deg)", color = "k", **{'font-size':'12pt'})
        gyro_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        gyro_graph.showGrid(x=True, y=True)

        # TEMPORARY FIX
        alt_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        volt_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        curr_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        accel_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        gyro_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)

        # adding graphs to graph layout
        graph_layout.addWidget(webView, 0, 0)
        graph_layout.addWidget(alt_graph, 0, 1)
        graph_layout.addWidget(volt_graph, 0, 2)
        graph_layout.addWidget(curr_graph, 1, 0)
        graph_layout.addWidget(accel_graph, 1, 1)
        graph_layout.addWidget(gyro_graph, 1, 2)

        # creating a line above the graphs to display additional information
        info_layout = QHBoxLayout()
        
        # adding information to the info layout
        fsw = QLabel('FSW State: ')
        fsw.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(fsw)
        echo = QLabel()
        echo.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        echo.setText('CMD_Echo: ') # make sure to add variable later that actually reads the cmd_echo
        info_layout.addWidget(echo)
        
        # put everything into one layout, numbers are for sizing ratios
        base_layout.addLayout(data_layout, 30)
        base_layout.addLayout(graph_layout, 90)

        # add header 
        final_layout.addLayout(info_layout)
        final_layout.addLayout(base_layout)
    
    
# opening main window
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GCS()
    window.show()
    app.exec()

