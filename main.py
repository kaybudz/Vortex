# main window for user interface
# 14 px minimum font size
# launchpad coordinates 38.37583 deg N, -79.6078 deg E
# cd96ff

# importing necessary libraries
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QLabel, QTableWidget, QPushButton, QHeaderView, QTableWidgetItem, QFrame
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from pyqtgraph import PlotWidget, mkPen, LegendItem
import folium
from io import BytesIO
from read_data import live_read
import serial
import matplotlib # UV INSTALL THIS SO ETHAN CAN ACCESS
matplotlib.use('QT5Agg')
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time

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

        # # TEMPORARY FOR VISUAL PURPOSES
        # latitude = [38.37583] 
        # longitude = [-79.6078] 
        # GPS = folium.Map(location = [latitude[0], longitude[0]], zoom_start=13) 
        # icon = folium.CustomIcon('ufo.png', icon_size = (75,75)) 
        # folium.Marker(location = [latitude[0], longitude[0]], popup = 'Payload', icon = icon).add_to(GPS) 
        # data = BytesIO()
        # GPS.save(data,close_file = False)
        # html = data.getvalue().decode()
        # webView = QWebEngineView(self)
        # webView.setHtml(html) 
        
        # setting time
        # self.time = [0]
        self.time = list(range(10))

        # creating 3D plot
        location = Figure(constrained_layout=True) # still cant see z axis
        canvas = FigureCanvas(location)
        loc_graph = location.add_subplot(111, projection='3d')
        loc_graph.set_xlabel('Latitude(°N)')
        loc_graph.set_ylabel('Longitude (°E)')
        loc_graph.set_zlabel('Altitude (m)')
        loc_graph.set_title('Flight Path')
        loc_graph.mouse_init(rotate_btn=None, zoom_btn=None) # keeps plot static
        loc_frame = QFrame()
        loc_frame.setStyleSheet("background-color: white; border: 5px solid #006ba3")
        frame = QVBoxLayout(loc_frame)
        frame.addWidget(canvas)

        # altitude graph
        self.alt_graph = PlotWidget() # placeholder graphs
        self.alt_graph.setBackground('white')
        self.alt_graph.setStyleSheet('border: 5px solid #006ba3')
        self.alt_graph.setTitle('Altitude', color = 'k', **{'font-size':'14pt', 'font-family':'Times New Roman'})
        self.alt_graph.setLabel("left", "Altitude (m)", color = "k", **{'font-size':'12pt'})
        self.alt_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        self.alt_graph.showGrid(x=True, y=True)
        self.alt_graph.setMouseEnabled(x=False, y=False)

        # voltage graph
        self.volt_graph = PlotWidget() # placeholder graphs
        self.volt_graph.setBackground('white')
        self.volt_graph.setStyleSheet('border: 5px solid #006ba3')
        self.volt_graph.setTitle('Voltage', color = 'k', **{'font-size':'14pt'})
        self.volt_graph.setLabel("left", "Voltage (V)", color = "k", **{'font-size':'12pt'})
        self.volt_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        self.volt_graph.showGrid(x=True, y=True)
        self.volt_graph.setMouseEnabled(x=False, y=False)

        # current graph
        self.curr_graph = PlotWidget() # placeholder graphs
        self.curr_graph.setBackground('white')
        self.curr_graph.setStyleSheet('border: 5px solid #006ba3')
        self.curr_graph.setTitle('Current', color = 'k', **{'font-size':'14pt'})
        self.curr_graph.setLabel("left", "Current (A)", color = "k", **{'font-size':'12pt'})
        self.curr_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        self.curr_graph.showGrid(x=True, y=True)
        self.curr_graph.setMouseEnabled(x=False, y=False)

        # acceleration graph
        self.accel_graph = PlotWidget() # placeholder graphs
        self.accel_graph.setBackground('white')
        self.accel_graph.setStyleSheet('border: 5px solid #006ba3')
        self.accel_graph.setTitle('Acceleration', color = 'k', **{'font-size':'14pt'})
        self.accel_graph.setLabel("left", "Acceleration (deg/s^2)", color = "k", **{'font-size':'12pt'})
        self.accel_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        self.accel_graph.showGrid(x=True, y=True)
        self.accel_graph.setMouseEnabled(x=False, y=False)
    
        # rotation graph
        self.gyro_graph = PlotWidget() # placeholder graphs
        self.gyro_graph.setBackground('white')
        self.gyro_graph.setStyleSheet('border: 5px solid #006ba3')
        self.gyro_graph.setTitle('Rotation', color = 'k', **{'font-size':'14pt'})
        self.gyro_graph.setLabel("left", "Rotation (deg/s)", color = "k", **{'font-size':'12pt'})
        self.gyro_graph.setLabel("bottom", "Time (s)", color = "k", **{'font-size':'12pt'})
        self.gyro_graph.showGrid(x=True, y=True)
        self.gyro_graph.setMouseEnabled(x=False, y=False)

        # TEMPORARY FIX
        self.alt_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        self.volt_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        self.curr_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        self.accel_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)
        self.gyro_graph.getPlotItem().setContentsMargins(0, 0, 0, 10)

        # establishing graph lines
        self.alt_line = self.alt_graph.plot([], [], pen='k')
        self.volt_line = self.volt_graph.plot([], [], pen='k')
        self.curr_line = self.curr_graph.plot([], [], pen='k')

        self.accel_graph.addLegend(offset=(1,1))
        alegend = LegendItem()                      
        alegend.setParentItem(self.accel_graph.graphicsItem()) 
        alegend.anchor((0, 1), (0, 1))
        self.aroll_line = self.accel_graph.plot([], [], pen='r', name='Roll')
        self.apitch_line = self.accel_graph.plot([], [], pen='g', name='Pitch')
        self.ayaw_line = self.accel_graph.plot([], [], pen='b', name='Yaw')
        
        self.gyro_graph.addLegend(offset=(1,1))
        glegend = LegendItem()                      
        glegend.setParentItem(self.gyro_graph.graphicsItem()) 
        glegend.anchor((0, 1), (0, 1))
        self.groll_line = self.gyro_graph.plot([], [], pen='r', name='Roll')
        self.gpitch_line = self.gyro_graph.plot([], [], pen='g', name='Pitch')
        self.gyaw_line = self.gyro_graph.plot([], [], pen='b', name='Yaw')

        # adding graphs to graph layout
        # graph_layout.addWidget(webView, 0, 0)
        graph_layout.addWidget(loc_frame, 0, 0), canvas.draw()
        graph_layout.addWidget(self.alt_graph, 0, 1)
        graph_layout.addWidget(self.volt_graph, 0, 2)
        graph_layout.addWidget(self.curr_graph, 1, 0)
        graph_layout.addWidget(self.accel_graph, 1, 1)
        graph_layout.addWidget(self.gyro_graph, 1, 2)

        # creating a line above the graphs to display additional information
        info_layout = QHBoxLayout()
        
        # adding information to the info layout
        # make sure to actually fill in with variables later
        self.fsw = QLabel('FSW State: ')
        self.fsw.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(self.fsw, 50)
        self.echo = QLabel('CMD Echo: ')
        self.echo.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(self.echo, 50)
        self.velocity = QLabel('Velocity (m/s): ')
        self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        info_layout.addWidget(self.velocity, 50)
        
        # put everything into one layout, numbers are for sizing ratios
        base_layout.addLayout(data_layout, 30)
        base_layout.addLayout(graph_layout, 90)

        # add header 
        final_layout.addLayout(info_layout)
        final_layout.addLayout(base_layout)

        # set initial conditions
        self.data_read = False
        self.comm = live_read()
        self.probe = 0 # tells us  the payload has not been released from the container
        self.egg = 0 # tells us the egg has not been released from the payload
        self.r_packet = 0 # recieved packet count
        self.l_packet = 0 # lost packet count

        # starting timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.apply_update)
        # self.time = [0]

    # MAKING CODE TO UPDATE GRAPHS
    def apply_update(self):
        # print statement for testing purposes
        # print('New data added')
        self.comm.update()
        self.timer.start(1000)

        # updating data table
        self.data_table.setItem(0, 0, QTableWidgetItem(str(self.comm.time[-1]))) # mission time

        # updating packet count
        if self.comm.pckt[-1] != self.comm.pckt[-2]:
            if self.comm.pckt[-1] - self.comm.pckt[-2] == 1:
                if self.r_packet == 0:
                    self.r_packet = self.r_packet + 2
                else:
                    self.r_packet = self.r_packet + 1
            else:
                if self.l_packet == 0:
                    self.l_packet = self.l_packet + 1
                else:
                    self.l_packet = self.l_packet + 1
        self.data_table.setItem(0, 1, QTableWidgetItem(str(self.r_packet))) 
        self.data_table.setItem(0, 2, QTableWidgetItem(str(self.l_packet)))

        # payload release
        if self.probe == 0:
            self.data_table.setItem(0, 3, QTableWidgetItem('N'))
        elif self.probe == 1:
            self.data_table.setItem(0, 3, QTableWidgetItem('Y'))

        # egg release
        if self.egg == 0:
            self.data_table.setItem(0, 4, QTableWidgetItem('N'))
        elif self.egg == 1:
            self.data_table.setItem(0, 4, QTableWidgetItem('Y'))
        
        self.data_table.setItem(0, 5, QTableWidgetItem(str(self.comm.temp[-1]))) # temperature
        self.data_table.setItem(0, 6, QTableWidgetItem(str(self.comm.lat[-1]))) # latitude
        self.data_table.setItem(0, 7, QTableWidgetItem(str(self.comm.lon[-1]))) # longitude
        self.data_table.setItem(0, 8, QTableWidgetItem(str(self.comm.sats[-1]))) # satellites

        # updating top line
        # fsw label
        self.fsw.setText('FSW State: ' + str(self.comm.state[-1]))
        if self.comm.state[-1] == 'LAUNCH_PAD':
            self.fsw.setStyleSheet('background-color: red; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        elif self.comm.state[-1] == 'ASCENT':
            self.fsw.setStyleSheet('background-color: orange; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        elif self.comm.state[-1] == 'APOGEE':
            self.fsw.setStyleSheet('background-color: yellow; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        elif self.comm.state[-1] == 'DESCENT':
            self.fsw.setStyleSheet('background-color: green; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        elif self.comm.state[-1] == 'PROBE_RELEASE':
            self.fsw.setStyleSheet('background-color: blue; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.probe = 1 # tells us the payload has been released from the container
        elif self.comm.state[-1] == 'PAYLOAD_RELEASE':
            self.fsw.setStyleSheet('background-color: purple; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.egg = 1 # tells us the egg has been released from the payload
        elif self.comm.state[-1] == 'LANDED':
            self.fsw.setStyleSheet('background-color: pink; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')

        # cmd echo label
        self.echo.setText('CMD Echo: ' + str(self.comm.cmd[-1]))

        # velocity label
        if self.comm.state[-1] == 'DESCENT':
            if self.probe == 0:
                if (self.comm.alt[-1] - self.comm.alt[-2]) >= 12 and (self.comm.alt[-1] - self.comm.alt[-2]) <= 18:
                    self.velocity.setStyleSheet('background-color: green; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
                elif (self.comm.alt[-1] - self.comm.alt[-2]) <= 12 or (self.comm.alt[-1] - self.comm.alt[-2]) >= 18:
                    self.velocity.setStyleSheet('background-color: red; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            elif self.probe == 1:
                if (self.comm.alt[-1] - self.comm.alt[-2]) >= 2 and (self.comm.alt[-1] - self.comm.alt[-2]) <= 8 and self.probe == 1:
                    self.velocity.setStyleSheet('background-color: green; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
                elif (self.comm.alt[-1] - self.comm.alt[-2]) <= 2 or (self.comm.alt[-1] - self.comm.alt[-2]) >= 8 and self.probe == 1: 
                    self.velocity.setStyleSheet('background-color: red; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            else:
                self.velocity.setStyleSheet('background-color: white; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        self.velocity.setText('Velocity (m/s): ' + str(self.comm.alt[-1] - self.comm.alt[-2]))

        # setting time for graphs
        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1)

        # updating graphs
        # altitude
        self.altitude = [self.comm.alt[-1] for _ in range(10)]
        self.comm.alt = self.comm.alt[1:]
        self.alt_line.setData(self.time, self.altitude)

        # voltage
        self.voltage = [self.comm.volt[-1] for _ in range(10)]
        self.comm.volt = self.comm.volt[1:]
        self.volt_line.setData(self.time, self.voltage)

        # current
        self.current = [self.comm.curr[-1] for _ in range(10)]
        self.comm.curr = self.comm.curr[1:]
        self.curr_line.setData(self.time, self.current)

        # acceleration
        self.accel_roll = [self.comm.a_roll[-1] for _ in range(10)]
        self.accel_pitch = [self.comm.a_pitch[-1] for _ in range(10)]
        self.accel_yaw = [self.comm.a_yaw[-1] for _ in range(10)]
        self.comm.a_roll = self.comm.a_roll[1:]
        self.comm.a_pitch = self.comm.a_pitch[1:]
        self.comm.a_yaw = self.comm.a_yaw[1:]
        self.aroll_line.setData(self.time, self.accel_roll)
        self.apitch_line.setData(self.time, self.accel_pitch)
        self.ayaw_line.setData(self.time, self.accel_yaw)

        # rotation
        self.gyro_roll = [self.comm.g_roll[-1] for _ in range(10)]
        self.gyro_pitch = [self.comm.g_pitch[-1] for _ in range(10)]
        self.gyro_yaw = [self.comm.g_yaw[-1] for _ in range(10)]
        self.comm.g_roll = self.comm.g_roll[1:]
        self.comm.g_pitch = self.comm.g_pitch[1:]
        self.comm.g_yaw = self.comm.g_yaw[1:]
        self.groll_line.setData(self.time, self.gyro_roll)
        self.gpitch_line.setData(self.time, self.gyro_pitch)
        self.gyaw_line.setData(self.time, self.gyro_yaw)

    # MAKING BUTTON COMMANDS
    # cx_on
    def start_cx(self):
        self.data_read = True
        self.comm.send('CMD,1093,CX,ON\n')
        self.cx_on.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        self.cx_off.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.comm.start_read()
        self.apply_update()

    # cx_off
    def stop_cx(self):
        self.data_read = False
        self.comm.send('CMD,1093,CX,OFF\n')
        self.cx_off.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        self.cx_on.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.timer.stop()
    
    # set time
    def time_set(self):
        self.comm.send('CMD,1093,ST,UTC\n')
        self.data_table.setItem(0, 0, QTableWidgetItem('00:00:00'))
        # self.data_table.setItem(0, 0, QTableWidgetItem(time[-1]))
        self.set_time.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')

    # sim enable
    def sim_e(self):
        self.comm.simEnabled = True
        self.comm.send('CMD,1093,SIM,ENABLE\n')
        self.sim_enable.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        self.sim_disable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    # sim activate
    def sim_a(self):
        self.comm.simulation = True
        if self.comm.simEnabled:
            self.sim_activate.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
            self.comm.send('CMD,1093,SIM,ACTIVATE\n')
            csv_filename = self.comm.csv_filename
            # code to read CSV file
            if csv_filename:
                self.comm.run_sim(csv_filename)   

    # sim disable
    def sim_d(self):
        self.comm.simulation = False
        self.comm.simEnabled = False
        self.comm.stop_sim(self)
        self.comm.send("CMD,1093,SIM,DISABLE\n")
        self.sim_disable.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        self.sim_enable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.sim_activate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
    
    # calibration
    def cal(self):
        self.comm.send("CMD,1093,CAL\n")
        self.calibrate.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
    
    # egg drop
    egg = False
    def egg_drop(self):
        if self.egg == False:
            self.egg = True
            self.comm.send("CMD,1093,MEC,EGG,ON\n")
            self.egg_release.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        else:
            self.egg = False
            self.comm.send("CMD,1093,MEC,EGG,OFF\n")
            self.egg_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    # payload release
    pl = False
    def payload(self):
        if self.pl == False:
            self.pl = True
            self.comm.send("CMD,1093,MEC,PROBE,ON\n")
            self.probe_release.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        else:
            self.pl = False
            self.comm.send("CMD,1093,MEC,PROBE,OFF\n")
            self.probe_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    # ACS
    sys = False
    def acs_sys(self):
        if self.sys == False:
            self.sys = True
            self.comm.send("CMD,1093,MEC,ACS,ON\n")
            self.acs.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        else:
            self.sys = False
            self.comm.send("CMD,1093,MEC,ACS,OFF\n")
            self.acs.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')

    
# opening main window
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GCS()
    window.show()
    app.exec()

