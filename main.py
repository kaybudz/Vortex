# main window for user interface
# 14 px minimum font size
# launchpad coordinates 38.37583 deg N, -79.6078 deg E
# cd96ff

# importing necessary libraries
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QLabel, QTableWidget, QPushButton, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import folium
from io import BytesIO
from read_data import live_read
import serial
import matplotlib.pyplot as plt # UV INSTALL THIS SO ETHAN CAN ACCESS
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure

dark_blue = QtGui.QColor(0, 107, 163)
class GCS(QMainWindow):
    # creating main window
    def __init__(self):
        super().__init__()
        
        # CODE FOR CREATING A UI
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
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet('background-color: white; font-family: roboto; font-size: 14px; font-weight: bold')
        self.data_table.horizontalHeader().setVisible(False)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers) # so that table cannot be edited live
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setGridStyle(Qt.SolidLine)
        self.data_table.setColumnCount(1)
        self.data_table.setRowCount(9)
        row_labels = [
            'Mission Time', 
            'Recieved Packets', 
            'Lost Packets', 
            'Payload Release',
            'Egg Release', 
            'Temperature (°C)',
            'GPS Latitude (°N)', 
            'GPS Longitude (°E)',
            'Satellites'
            ]
        self.data_table.setVerticalHeaderLabels(row_labels)
        data_layout.addWidget(self.data_table, 1)

        # making the button layout
        button_layout = QGridLayout()
        self.cx_on = QPushButton('CX On')
        self.cx_on.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.cx_on.clicked.connect(self.start_cx)

        self.cx_off = QPushButton('CX Off')
        self.cx_off.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.cx_off.clicked.connect(self.stop_cx)

        self.sim_enable = QPushButton('SIM Enable')
        self.sim_enable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.sim_enable.clicked.connect(self.sim_e)

        self.sim_activate = QPushButton('SIM Activate')
        self.sim_activate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.sim_activate.clicked.connect(self.sim_a)

        self.sim_disable = QPushButton('SIM Disable')
        self.sim_disable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.sim_disable.clicked.connect(self.sim_d)

        self.acs = QPushButton('ACS')
        self.acs.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.acs.clicked.connect(self.acs_sys)

        self.egg_release = QPushButton('Egg Drop')
        self.egg_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.egg_release.clicked.connect(self.egg_drop)

        self.probe_release = QPushButton('Release')
        self.probe_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.probe_release.clicked.connect(self.payload)

        self.calibrate = QPushButton('Calibrate')
        self.calibrate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.calibrate.clicked.connect(self.cal)

        self.set_time = QPushButton('Set Time')
        self.set_time.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.set_time.clicked.connect(self.time_set)

        # party_mode = QPushButton()
        # party_mode.setText('Party Mode')
        # party_mode.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        button_layout.addWidget(self.sim_enable, 0, 0)
        button_layout.addWidget(self.sim_activate, 0, 1)
        button_layout.addWidget(self.sim_disable, 1, 0)
        button_layout.addWidget(self.acs, 1, 1)
        button_layout.addWidget(self.cx_on, 2, 0)
        button_layout.addWidget(self.cx_off, 2, 1)
        button_layout.addWidget(self.calibrate, 3, 0)
        button_layout.addWidget(self.set_time, 3, 1)
        button_layout.addWidget(self.probe_release, 4, 0)
        button_layout.addWidget(self.egg_release, 4, 1)
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

        # # creating 3D plot
        # location = plt.figure()
        # loc_graph = location.add_subplot(111, projection='3d')
        # loc_graph.set_xlabel('Latitude(°N)')
        # loc_graph.set_ylabel('Longitude (°E)')
        # loc_graph.set_zlabel('Altitude (m)')
        # loc_graph.set_title('Flight Path')
        # # plt.show()

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
        gyro_graph.setLabel("left", "Rotation (deg/s)", color = "k", **{'font-size':'12pt'})
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
        # graph_layout.addWidget(loc_graph, 0, 0)
        graph_layout.addWidget(alt_graph, 0, 1)
        graph_layout.addWidget(volt_graph, 0, 2)
        graph_layout.addWidget(curr_graph, 1, 0)
        graph_layout.addWidget(accel_graph, 1, 1)
        graph_layout.addWidget(gyro_graph, 1, 2)

        # creating a line above the graphs to display additional information
        info_layout = QHBoxLayout()
        
        # adding information to the info layout
        # make sure to actually fill in with variables later
        fsw = QLabel('FSW State: ')
        fsw.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(fsw, 50)
        echo = QLabel('CMD Echo: ')
        echo.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(echo, 50)
        velocity = QLabel('Velocity (m/s): ')
        velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(velocity, 50)
        
        # put everything into one layout, numbers are for sizing ratios
        base_layout.addLayout(data_layout, 30)
        base_layout.addLayout(graph_layout, 90)

        # add header 
        final_layout.addLayout(info_layout)
        final_layout.addLayout(base_layout)

        # set data read to false
        self.data_read = False
        self.comm = live_read

        # MAKING CODE TO UPDATE GRAPHS
        # def update_graphs(self):
        #     c
        
    # MAKING BUTTON COMMANDS
    # MAKE THE COMMANDS ACTUALLY SEND

    # cx_on
    def start_cx(self):
        self.data_read = True
        # self.comm.send('CMD,1093,CX,ON')
        self.cx_on.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
    
    # cx_off
    def stop_cx(self):
        self.data_read = False
        # self.comm.send('CMD,1093,CX,OFF')
        self.cx_off.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
    
    # set time
    def time_set(self):
        # self.comm.send('CMD,1093,ST,UTC')
        self.data_table.setItem(0, 0, QTableWidgetItem('00:00:00'))
        # self.data_table.setItem(0, 0, QTableWidgetItem(time[-1]))
        self.set_time.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')

    # sim enable
    def sim_e(self):
        # self.comm.simEnabled = True
        # self.comm.send('CMD,1093,SIM,ENABLE')
        self.sim_enable.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')

    # sim activate
    def sim_a(self):
        # self.comm.simActivated = True
        self.sim_activate.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        # if self.comm.simEnabled:
        #     # self.comm.send('CMD,1093,SIM,ACTIVATE')
        #     # code to read CSV file
        #     if csv_filename:
        #         self.comm.sim_mode(csv_filename)   

    # sim disable
    def sim_d(self):
        # self.comm.simulation = False
        # self.comm.stop_simulation()
        # self.comm.send("CMD,1093,SIM,DISABLE")
        # self.comm.simEnabled = False
        self.sim_disable.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
    
    # calibration
    def cal(self):
        # self.comm.send("CMD,1093,CAL")
        self.calibrate.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
    
    # egg drop
    egg = False
    def egg_drop(self):
        if self.egg == False:
            self.egg = True
            # self.comm.send("CMD,3195,MEC,EGG,ON")
            self.egg_release.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        else:
            self.egg = False
            # self.comm.send("CMD,3195,MEC,EGG,OFF")
            self.egg_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    # payload release
    pl = False
    def payload(self):
        if self.pl == False:
            self.pl = True
            # self.comm.send("CMD,3195,MEC,PROBE,ON")
            self.probe_release.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        else:
            self.pl = False
            # self.comm.send("CMD,3195,MEC,PROBE,OFF")
            self.probe_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    # ACS
    sys = False
    def acs_sys(self):
        if self.sys == False:
            self.sys = True
            # self.comm.send("CMD,3195,MEC,ACS,ON")
            self.acs.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        else:
            self.sys = False
            # self.comm.send("CMD,3195,MEC,ACS,OFF")
            self.acs.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    
# opening main window
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GCS()
    window.show()
    app.exec()

