# launchpad coordinates 38.37583 deg N, -79.6078 deg E
# test launch target coordinates 31.072094 deg N, -86.053301 deg E

# importing necessary libraries
import sys
import os
from PyQt5 import QtGui, QtWidgets 
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QWidget, QLabel, QTableWidget, QPushButton, QHeaderView, QTableWidgetItem, QFrame, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from pyqtgraph import PlotWidget, mkBrush, mkPen, LegendItem
from io import BytesIO
from read_data import live_read
import matplotlib 
matplotlib.use('QT5Agg')
import matplotlib.pylab as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from LED_simulation import LED
import time
#from playsound import playsound # add sounds to hitting buttons? is there any sort of speaker system with the pi5
#import pygame

dark_blue = QtGui.QColor(0, 107, 163)
class GCS(QMainWindow):
    # creating main window
    def __init__(self):
        super().__init__()
    
        # CODE FOR CREATING A UI
        # setting up style of background of window
        # self.setGeometry(100, 100, 1024, 600)
        self.setStyleSheet("background-color: #cce5ff;")
        self.setWindowTitle("Vortex Base Station")
        self.setWindowIcon(QIcon('Vortex_Logo.png'))
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget) 
        self.lat_history = []
        self.lon_history = []
        self.alt_history = []

        # set initial conditions
        self.data_read = False
        self.comm = live_read()
        self.led = LED()
        self.probe = 0 # tells us  the payload has not been released from the container
        self.egg = 0 # tells us the egg has not been released from the payload
        self.r_packet = 0 # recieved packet count
        self.l_packet = 0 # lost packet count
        self.sys = False # acs system activation, should this be defaulted to true?
        self.play = False # setting condition for party mode
        self.lat_coord = 0
        self.long_coord = 0
        self.curr_pckt = ''
        self.partytime = 0

        # # make hours:minutes:seconds accurate to start time of experiment
        # self.hours = '3'
        # self.minutes = '21'
        # self.seconds = '54'

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

        self.egg_release = QPushButton('Egg Release')
        self.egg_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.egg_release.clicked.connect(self.egg_drop)

        self.egg_lock = QPushButton('Egg Lock')
        self.egg_lock.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.egg_lock.clicked.connect(self.egg_secure)

        self.probe_release = QPushButton('Release')
        self.probe_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.probe_release.clicked.connect(self.payload)

        self.probe_lock = QPushButton('Lock')
        self.probe_lock.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.probe_lock.clicked.connect(self.payload_lock)

        self.reset = QPushButton('Reset')
        self.reset.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.reset.clicked.connect(self.reset_sd)

        self.calibrate = QPushButton('Calibrate')
        self.calibrate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.calibrate.clicked.connect(self.cal)

        self.set_time = QPushButton('Set Time')
        self.set_time.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.set_time.clicked.connect(self.time_set)

        button_layout.addWidget(self.sim_enable, 0, 0)
        button_layout.addWidget(self.sim_activate, 0, 1)
        button_layout.addWidget(self.sim_disable, 1, 0)
        #button_layout.addWidget(self.acs, 1, 1)
        button_layout.addWidget(self.cx_on, 2, 0)
        button_layout.addWidget(self.cx_off, 2, 1)
        button_layout.addWidget(self.calibrate, 3, 0)
        button_layout.addWidget(self.set_time, 3, 1)
        button_layout.addWidget(self.probe_release, 4, 0)
        button_layout.addWidget(self.probe_lock, 4, 1)
        button_layout.addWidget(self.egg_release, 5, 0)
        button_layout.addWidget(self.egg_lock, 5, 1)
        button_layout.addWidget(self.reset, 1, 1)
        data_layout.addLayout(button_layout, 1)

        # adding port dropdown
        self.ports = QComboBox()
        self.ports.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        self.ports.addItems(self.comm.port_list[:])
        self.ports.currentTextChanged.connect(self.update_ports)
        data_layout.addWidget(self.ports)

        # adding csv filename for sim mode
        self.file_input = QLineEdit('SIM File')
        self.file_input.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        data_layout.addWidget(self.file_input)

        # adding manual command line
        # self.command_input = QLineEdit('Command Input')
        # self.command_input.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        # data_layout.addWidget(self.command_input)

        # adding party button
        self.party_mode = QPushButton('DO NOT PRESS')
        self.party_mode.setStyleSheet('background-color: red; font-family: roboto; font-size: 16px; font-weight: bold')
        self.party_mode.clicked.connect(self.party)
        data_layout.addWidget(self.party_mode)

        # graph side layout
        graph_layout = QGridLayout()
        graph_layout.setSpacing(5)
        
        # setting time
        self.time = list(range(10))

        # creating 3D plot
        # MAKE THIS NOT LOOK LIKE SHIT
        self.location = Figure() # still cant see z axis constrained_layout=True
        self.canvas = FigureCanvas(self.location)
        self.loc_graph = self.location.add_subplot(111, projection='3d')
        self.location.subplots_adjust(left=0, right=0.79, bottom=0.05, top=1)
        self.loc_graph.set_xlabel('Latitude(°N)', labelpad=2)
        self.loc_graph.set_ylabel('Longitude (°E)', labelpad=2)
        self.loc_graph.set_zlabel('Altitude (m)', labelpad=1.5)
        self.loc_graph.set_title('Flight Path', pad=0)
        self.loc_graph.mouse_init(rotate_btn=None, zoom_btn=None) # keeps plot static
        loc_frame = QFrame()
        loc_frame.setStyleSheet("background-color: white; border: 5px solid #006ba3")
        frame = QVBoxLayout(loc_frame)
        frame.addWidget(self.canvas)
        self.gps_line, = self.loc_graph.plot([], [], [], lw=2)

        self.loc_graph.scatter(self.lat_coord, self.long_coord, 0, c='red', s=50)
        self.loc_graph.autoscale(enable=True, axis='both', tight=None)

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
        self.alt_line = self.alt_graph.plot([], [], pen='k', width=10)
        self.volt_line = self.volt_graph.plot([], [], pen='k', width=10)
        self.curr_line = self.curr_graph.plot([], [], pen='k', width=10)

        self.accel_graph.addLegend(offset=(1,1))
        alegend = LegendItem()                     
        alegend.setParentItem(self.accel_graph.graphicsItem()) 
        alegend.anchor((0, 1), (0, 1))
        self.aroll_line = self.accel_graph.plot([], [], pen='r', width=10, name='Roll')
        self.apitch_line = self.accel_graph.plot([], [], pen='g', width=10, name='Pitch')
        self.ayaw_line = self.accel_graph.plot([], [], pen='b', width=10, name='Yaw')

        self.gyro_graph.addLegend(offset=(1,1))
        glegend = LegendItem()                      
        glegend.setParentItem(self.gyro_graph.graphicsItem()) 
        glegend.anchor((0, 1), (0, 1))
        self.groll_line = self.gyro_graph.plot([], [], pen='r', width=10, name='Roll')
        self.gpitch_line = self.gyro_graph.plot([], [], pen='g', width=10, name='Pitch')
        self.gyaw_line = self.gyro_graph.plot([], [], pen='b', width=10, name='Yaw')

        # adding graphs to graph layout
        graph_layout.addWidget(loc_frame, 0, 0), self.canvas.draw()
        graph_layout.addWidget(self.alt_graph, 0, 1)
        graph_layout.addWidget(self.volt_graph, 0, 2)
        graph_layout.addWidget(self.curr_graph, 1, 0)
        graph_layout.addWidget(self.accel_graph, 1, 1)
        graph_layout.addWidget(self.gyro_graph, 1, 2)

        # creating a line above the graphs to display additional information
        info_layout = QHBoxLayout()
        
        # adding information to the info layout
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


        # starting timer for updates
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.apply_update)

        # calling available ports
        try:
            self.update_ports()
        except:
            print('ERROR: No ports found')
    
    def update_ports(self):
        new_port = self.ports.currentText()
        print("Switching to:", new_port)

        # Update chosen port
        self.comm.chosen_port = new_port

        # connecting to select port
        self.comm.select_port()

    def party(self):
        self.partytime = 1
        # if self.play is False:
        #     playsound('C:/Users/kayla/Python311/Vortex/intergalactic_clipped.mp3')
        #     self.play = True
    # # Initialize mixer once
    #     if not hasattr(self, "pygame_initialized"):
    #         pygame.mixer.init()
    #         pygame.mixer.music.load('C:/Users/kayla/Python311/Vortex/intergalactic_clipped.mp3')
    #         # self.pygame_initialized = True
    #     if self.play is False:
    #         pygame.mixer.music.play()
    #         self.play = True
    #     else:
    #         pygame.mixer.music.stop()
    #         self.play = False
    
    # MAKING CODE TO UPDATE GRAPHS
    def apply_update(self):

        # new_telemetry_received = self.comm.update()

        # if not new_telemetry_received:
        #     return

    # Table and graph updates only happen for a new telemetry packet
        # print statement for testing purposes
        # print('New data added')

        self.comm.update()

        # updating data table
        # establishing initial mission time
        # FAKE MISSION TIME
        # if int(self.seconds) < 60:
        #     self.seconds = int(self.seconds) + 1
        # elif int(self.seconds) > 60 & int(self.minutes) < 60:
        #     self.minutes = int(self.minutes) + 1
        #     self.seconds = 0
        # else:
        #     self.hours = int(self.hours) + 1
        #     self.minutes = 0
        # self.data_table.setItem(0, 0, QTableWidgetItem(f"{int(self.hours):02d}:{int(self.minutes):02d}:{int(self.seconds):02d}"))
        # print(f"{int(self.hours):02d}:{int(self.minutes):02d}:{int(self.seconds):02d}")

        # updating packet count 
        # GET RID OF PCKT COUNTING WHEN NO INFO
        #if self.curr_pckt != self.comm.pckt[-1]:
        try:
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
        except:
            print('Not enough packets')
            #self.curr_pckt = self.comm.pckt[-1]
        
        self.data_table.setItem(0, 1, QTableWidgetItem(str(self.r_packet))) 
        self.data_table.setItem(0, 2, QTableWidgetItem(str(self.l_packet)))
        
        # mission time
        self.data_table.setItem(0, 0, QTableWidgetItem(str(self.comm.time[-1])))

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
        if self.partytime == 1:
            print('party')
            # try:
            #     self.led.send_LED('Galaxy')
            # except:
            #     print('Galaxy')
        elif self.comm.state[-1] == 'LAUNCH_PAD':
            self.fsw.setStyleSheet('background-color: #ea9999; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            # try:
            #     self.led.send_LED('LAUNCH_PAD')
            # except:
            #     print('LAUNCH_PAD')
        elif self.comm.state[-1] == 'ASCENT':
            self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.fsw.setStyleSheet('background-color: #f9cb9c; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            # try:
            #     self.led.send_LED('ASCENT')
            # except:
            #     print('ASCENT')
        elif self.comm.state[-1] == 'APOGEE':
            self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.fsw.setStyleSheet('background-color: #ffe599; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            # try:
            #     self.led.send_LED('APOGEE')
            # except:
            #     print('APOGEE')
        elif self.comm.state[-1] == 'DESCENT':
            self.fsw.setStyleSheet('background-color: #b6d7a8; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            # try:
            #     self.led.send_LED('DESCENT')
            # except:
            #     print('DESCENT')
        elif self.comm.state[-1] == 'PROBE_RELEASE':
            self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.fsw.setStyleSheet('background-color: #a4c2f4; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.probe = 1 # tells us the payload has been released from the container
            # try:
            #     self.led.send_LED('PROBE_RELEASE')
            # except:
            #     print('PROBE_RELEASE')
        elif self.comm.state[-1] == 'PAYLOAD_RELEASE':
            self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.fsw.setStyleSheet('background-color: #b4a7d6; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.egg = 1 # tells us the egg has been released from the payload
            # try:
            #     self.led.send_LED('PAYLOAD_RELEASE')
            # except:
            #     print('PAYLOAD_RELEASE')
        elif self.comm.state[-1] == 'LANDED':
            self.velocity.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            self.fsw.setStyleSheet('background-color: #f6b8d6; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
            # try:
            #     self.led.send_LED('LANDED')
            # except:
            #     print('LANDED')
        else:
            try:
                self.led.send_LED('Waiting')
            except:
                return

        # cmd echo label
        self.echo.setText('CMD Echo: ' + str(self.comm.cmd[-1]))

        # velocity label
        if self.comm.state[-1] == 'DESCENT':
            if self.probe == 0:
                if abs(self.comm.alt[-1] - self.comm.alt[-2]) >= 12 and abs(self.comm.alt[-1] - self.comm.alt[-2]) <= 18:
                    self.velocity.setStyleSheet('background-color: #b6d7a8; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
                elif abs(self.comm.alt[-1] - self.comm.alt[-2]) <= 12 or abs(self.comm.alt[-1] - self.comm.alt[-2]) >= 18:
                    self.velocity.setStyleSheet('background-color: #ea9999; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        elif self.comm.state[-1] == 'PROBE_RELEASE':
            if self.probe == 1:
                if abs(self.comm.alt[-1] - self.comm.alt[-2]) >= 2 and abs(self.comm.alt[-1] - self.comm.alt[-2]) <= 8 and self.probe == 1:
                    self.velocity.setStyleSheet('background-color: #b6d7a8; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
                elif abs(self.comm.alt[-1] - self.comm.alt[-2]) <= 2 or abs(self.comm.alt[-1] - self.comm.alt[-2]) >= 8 and self.probe == 1: 
                    self.velocity.setStyleSheet('background-color: #ea9999; font-family: roboto; font-size: 16px; font-weight: bold; border: 2px solid black')
        self.velocity.setText('Velocity (m/s): ' + str(round((self.comm.alt[-1] - self.comm.alt[-2]),2)))

        # setting time for graphs
        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1)

        # updating graphs
        # flight path
        self.lat_history.append(float(self.comm.lat[-1]))
        self.lon_history.append(float(self.comm.lon[-1]))
        self.alt_history.append(float(self.comm.alt[-1]))

        self.gps_line.set_data(self.lat_history, self.lon_history)
        self.gps_line.set_3d_properties(self.alt_history)

        # update axes limits
        # self.loc_graph.set_xlim(min(self.lat_history), max(self.lat_history))
        # self.loc_graph.set_ylim(min(self.lon_history), max(self.lon_history))
        # self.loc_graph.set_zlim(min(self.alt_history), max(self.alt_history))
        lat_min = min(self.lat_history)
        lat_max = max(self.lat_history)

        lon_min = min(self.lon_history)
        lon_max = max(self.lon_history)

        alt_min = min(self.alt_history)
        alt_max = max(self.alt_history)

        # Add padding if the values are identical
        if lat_min == lat_max:
            lat_min -= 0.0001
            lat_max += 0.0001

        if lon_min == lon_max:
            lon_min -= 0.0001
            lon_max += 0.0001

        if alt_min == alt_max:
            alt_min -= 1
            alt_max += 1

        self.loc_graph.set_xlim(lat_min, lat_max)
        self.loc_graph.set_ylim(lon_min, lon_max)
        self.loc_graph.set_zlim(alt_min, alt_max)

        # redraw canvas
        self.canvas.draw_idle()
    
        # altitude
        if len(self.comm.alt) > 0:
            window = min(10, len(self.comm.alt))
            self.alt_line.setData(self.time[-window:], self.comm.alt[-window:])

        # voltage
        if len(self.comm.volt) > 0:
            window = min(10, len(self.comm.volt))
            self.volt_line.setData(self.time[-window:], self.comm.volt[-window:])

        # current
        if len(self.comm.curr) > 0:
            window = min(10, len(self.comm.curr))
            self.curr_line.setData(self.time[-window:], self.comm.curr[-window:])

        # acceleration
        if len(self.comm.a_roll) > 0:
            window = min(10, len(self.comm.a_roll))
            self.aroll_line.setData(self.time[-window:], self.comm.a_roll[-window:])
        if len(self.comm.a_pitch) > 0:
            window = min(10, len(self.comm.a_pitch))
            self.apitch_line.setData(self.time[-window:], self.comm.a_pitch[-window:])
        if len(self.comm.a_yaw) > 0:
            window = min(10, len(self.comm.a_yaw))
            self.ayaw_line.setData(self.time[-window:], self.comm.a_yaw[-window:])

        # rotation
        if len(self.comm.g_roll) > 0:
            window = min(10, len(self.comm.g_roll))
            self.groll_line.setData(self.time[-window:], self.comm.g_roll[-window:])
        if len(self.comm.g_pitch) > 0:
            window = min(10, len(self.comm.g_pitch))
            self.gpitch_line.setData(self.time[-window:], self.comm.g_pitch[-window:])
        if len(self.comm.a_yaw) > 0:
            window = min(10, len(self.comm.g_yaw))
            self.gyaw_line.setData(self.time[-window:], self.comm.g_yaw[-window:])

        # updating cmd echo
        if self.comm.cmd[-1] == 'CMD,1093,CX,ON':
            self.cx_on.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
            self.cx_off.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        elif self.comm.cmd[-1] == 'CMD,1093,CX,OFF':
            self.cx_off.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
            self.cx_on.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        elif self.comm.cmd[-1] == 'CMD,1093,ST,UTC':
            self.set_time.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        elif self.comm.cmd[-1] == 'CMD,1093,CAL':
            self.calibrate.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        elif self.comm.cmd[-1] == "CMD,1093,MEC,PROBE,UNLOCK":
            self.probe = 1
            self.probe_release.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        elif self.comm.cmd[-1] == "CMD,1093,MEC,PROBE,LOCK":
            self.probe_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
            if self.comm.state[-1] == 'PROBE_RELEASE':
                self.probe = 1
            elif self.comm.state[-1] == 'PAYLOAD_RELEASE':
                self.probe = 1
                self.egg = 1
            elif self.comm.state[-1] == 'LANDED':
                self.probe = self.probe
                self.egg = self.egg
            else: 
                self.probe = 0
        elif self.comm.cmd[-1] == "CMD,1093,MEC,EGG,UNLOCK":
            self.egg = 1
            self.egg_release.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        elif self.comm.cmd[-1] == "CMD,1093,MEC,EGG,LOCK":
            self.egg_release.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
            self.egg = 0
            if self.comm.state == 'PAYLOAD_RELEASE':
                self.egg = 1
                self.probe = 1
        else:
            return

    # MAKING BUTTON COMMANDS
    # cx_on
    def start_cx(self):
        self.data_read = True
        self.comm.send('CMD,1093,CX,ON\n')
        self.comm.start_read()
        self.timer.start()
        self.apply_update()
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    # cx_off
    def stop_cx(self):
        self.data_read = False
        self.comm.send('CMD,1093,CX,OFF\n')
        self.timer.stop()
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
    
    # set time
    def time_set(self):
        self.comm.send('CMD,1093,ST,UTC\n')
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    # sim enable
    def sim_e(self):
        try:
            self.comm.sim_filename = self.file_input.text()
            #self.comm.sim_filename = 'cansat_2023_simp.txt'
            print(self.comm.sim_filename)
        except:
            print('Define SIM File')
        self.comm.simEnabled = True
        self.comm.send('CMD,1093,SIM,ENABLE\n')
        if self.echo == 'CMD,1093,SIM,ENABLE':
            self.sim_enable.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
            self.sim_disable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    # sim activate
    def sim_a(self):
        # csv_filename = self.comm.sim_filename
        # self.comm.simulation = True
        # if self.comm.simEnabled:
        #     self.comm.send('CMD,1093,SIM,ACTIVATE\n')
        #     if self.echo == 'CMD,1093,SIM,ACTIVATE':
        #         self.sim_activate.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
        #     # csv_filename = self.comm.csv_filename
        #     # code to read CSV file
        #     if csv_filename:
        #         self.comm.start_sim(csv_filename)   
        # self.data_read = True
        # time.sleep(2)
        # try: 
        #     self.apply_update()
        # except:
        #     print('Could not update simulation')
        # #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
        csv_filename = self.comm.sim_filename

        if not self.comm.simEnabled:
            print("Enable simulation before activating it")
            return

        self.comm.simulation = True
        self.data_read = True

        # Start receiving telemetry from the CanSat
        self.comm.send('CMD,1093,CX,ON\n')
        self.comm.start_read()

        # Tell the CanSat to activate simulation mode
        self.comm.send('CMD,1093,SIM,ACTIVATE\n')

        # Begin sending SIMP commands
        if csv_filename:
            self.comm.start_sim(csv_filename)

        # Let the timer continuously update the GUI
        self.timer.start()

    # sim disable
    def sim_d(self):
        self.comm.simulation = False
        self.comm.simEnabled = False
        self.data_read = False
        self.comm.stop_sim()
        self.comm.send("CMD,1093,SIM,DISABLE\n")
        if self.echo == "CMD,1093,SIM,DISABLE":
            self.sim_disable.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
            self.sim_enable.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
            self.sim_activate.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
    
    # calibration
    def cal(self):
        self.comm.send("CMD,1093,CAL\n")
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
    
    # egg drop
    def egg_drop(self):
        self.egg = 1
        self.comm.send("CMD,1093,MEC,EGG,UNLOCK\n")
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    def egg_secure(self):
        self.egg = 0
        self.comm.send("CMD,1093,MEC,EGG,LOCK\n")
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    # payload release
    def payload(self):
        self.probe = 1
        self.comm.send("CMD,1093,MEC,PROBE,UNLOCK\n")
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
    
    # payload lock
    def payload_lock(self):
        self.probe = 0
        self.comm.send("CMD,1093,MEC,PROBE,LOCK\n")
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    # reset sd
    def reset_sd(self):
        self.comm.send("CMD,1093,SD,RESET\n")
        #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')

    # ACS
    def acs_sys(self):
        if self.sys == False:
            self.sys = True
            self.comm.send("CMD,1093,MEC,ACS,LEFT\n")
            self.acs.setStyleSheet('background-color: #7eb4d0; font-family: roboto; font-size: 16px; font-weight: bold')
            #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
        else:
            self.sys = False
            self.comm.send("CMD,1093,MEC,ACS,RIGHT\n]")
            self.acs.setStyleSheet('background-color: #cd96ff; font-family: roboto; font-size: 16px; font-weight: bold')
            #playsound('C:/Users/kayla/Python311/Vortex/laser.mp3')
    
# opening main window
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GCS()
    window.show()
    app.exec()

