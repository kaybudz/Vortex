# GROUND STATION CODE EDITED TO TAKE IN LIVE DATA

# importing necessary libraries
from random import randint
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from pyqtgraph import PlotWidget, mkPen, LegendItem
from offline_folium import offline
import folium
from io import BytesIO
import serial
import csv

# creating main window for ground station
class Ui_MainWindow():
    
    def setupUi(self, MainWindow):
        # creating main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920,1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setStyleSheet("background-color: green;")
        MainWindow.setAutoFillBackground(True)

        # initializing serial
        self.ser = False

        # establish lists for variables 
        self.team_list = [0]
        self.mission_list = ['0']
        self.packet_list = [0]
        self.sw_list = ['0']
        self.pl_list = ['0']
        self.altitude_list = [0]
        self.temperature_list = [0]
        self.voltage_list = [0]
        self.latitude_list = [0]
        self.longitude_list = [0]
        self.roll_list = [0]
        self.pitch_list = [0]
        self.yaw_list = [0]
        self.pressure_list = [0]
        self.speed_list = [0]

        # creating graph frame
        self.graph_frame = QtWidgets.QFrame(self.centralwidget)
        self.graph_frame.setGeometry(QtCore.QRect(512, 212, 1373, 841))
        self.graph_frame.setObjectName("graph_frame")
        self.graph_frame.setStyleSheet('border: 10px solid black')

        # creating layout of graphs
        self.gridLayout = QtWidgets.QGridLayout(self.graph_frame)
        self.gridLayout.setContentsMargins(11, -1, -1, -1)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.header_font = QtGui.QFont('Roc Grotesk', 12)
        self.header_font.setBold
        self.label_font = QtGui.QFont('Roc Grotesk', 10)
        self.label_font.setBold

        # altitude graph
        self.altitude = PlotWidget(self.graph_frame)
        self.altitude.setMouseEnabled(x=False, y=False)
        self.altitude.setObjectName("altitude")
        self.gridLayout.addWidget(self.altitude, 0, 0, 1, 1)
        self.altitude.setBackground("w")
        self.altitude.setTitle("Altitude vs Time", color = "k", size = "14pt")
        self.altitude.setLabel("left", "Altitude (m)", color = "k")
        self.altitude.setLabel("bottom", "Time (s)", color = "k")
        self.altitude.showGrid(x=True, y=True)
        
        # Code for live graph
        self.altitude.setYRange(0, 550)
        self.time = list(range(10))
        self.alt_graph = [self.altitude_list[-1] for _ in range(10)] 
        self.aline = self.altitude.plot(
            self.time,
            self.alt_graph,
            pen=mkPen('k'),
        )

        # air speed graph
        self.speed = PlotWidget(self.graph_frame)
        self.speed.setMouseEnabled(x=False, y=False)
        self.speed.setObjectName("speed")
        self.gridLayout.addWidget(self.speed, 0, 1, 1, 1)
        self.speed.setBackground("w")
        self.speed.setTitle("Air Speed vs Time", color = "k", size = "14pt")
        self.speed.setLabel("left", "Air Speed (m/s)", color = "k")
        self.speed.setLabel("bottom", "Time (s)", color = "k")
        self.speed.showGrid(x=True, y=True)
        
        # Code for live graph
        self.speed.setYRange(-25, 25)
        self.time = list(range(10))
        self.speed_graph = [self.speed_list[-1] for _ in range(10)] 
        self.sline = self.speed.plot(
            self.time,
            self.speed_graph,
            pen=mkPen('k'),
        )
        # tilt graph
        self.tilt = PlotWidget(self.graph_frame)
        self.tilt.setMouseEnabled(x=False, y=False)
        self.tilt.setObjectName("tilt")
        self.gridLayout.addWidget(self.tilt, 0, 2, 1, 1)
        self.tilt.setBackground("w")
        self.tilt.setTitle("Gyroscope vs Time", color = "k", size = "14pt")
        self.tilt.setLabel("left", "Gyroscope (deg)", color = "k")
        self.tilt.setLabel("bottom", "Time (s)", color = "k")
        self.tilt.showGrid(x=True, y=True)
        
        # Code for live graph
        self.tilt.setYRange(0, 360)
        self.time = list(range(10))
        self.roll = [self.roll_list[-1] for _ in range(10)]
        self.pitch = [self.pitch_list[-1] for _ in range(10)]
        self.yaw = [self.yaw_list[-1] for _ in range(10)]
        
        # adding a legend
        self.tilt.addLegend(offset=(1,1))
        legend = LegendItem()                      
        legend.setParentItem(self.tilt.graphicsItem()) 
        legend.anchor((0, 1), (0, 1))                
        self.roll_curve = self.tilt.plot(self.time, self.roll, pen='r', name='Gyro Roll')
        self.pitch_curve = self.tilt.plot(self.time, self.pitch, pen='g', name='Gyro Pitch')
        self.yaw_curve = self.tilt.plot(self.time, self.yaw, pen='b', name='Gyro Yaw')

        # temperature graph
        self.temperature = PlotWidget(self.graph_frame)
        self.temperature.setMouseEnabled(x=False, y=False)
        self.temperature.setObjectName("temperature")
        self.gridLayout.addWidget(self.temperature, 1, 0, 1, 1)
        self.temperature.setBackground("w")
        self.temperature.setTitle("Temperature vs Time", color = "k", size = "14pt")
        self.temperature.setLabel("left", "Temperature (°C)", color = "k")
        self.temperature.setLabel("bottom", "Time (s)", color = "k")
        self.temperature.showGrid(x=True, y=True)
        
        # Code for live graph
        self.temperature.setYRange(0, 40)
        self.time = list(range(10))
        self.temp_graph = [self.temperature_list[-1] for _ in range(10)] 
        self.line = self.temperature.plot(self.time, self.temp_graph, pen=mkPen('k'))

        # pressure graph
        self.pressure = PlotWidget(self.graph_frame)
        self.pressure.setMouseEnabled(x=False, y=False)
        self.pressure.setObjectName("pressure")
        self.gridLayout.addWidget(self.pressure, 1, 1, 1, 1)
        self.pressure.setBackground("w")
        self.pressure.setTitle("Pressure vs Time", color = "k", size = "14pt")
        self.pressure.setLabel("left", "Pressure (kPa)", color = "k")
        self.pressure.setLabel("bottom", "Time (s)", color = "k")
        self.pressure.showGrid(x=True, y=True)
        
        # Code for live graph
        self.pressure.setYRange(0, 110)
        self.time = list(range(10))
        self.pressure_graph = [self.pressure_list[-1] for _ in range(10)] 
        self.pline = self.pressure.plot(
            self.time,
            self.pressure_graph,
            pen=mkPen('k'),
        )

        # location widget as a folium map 
        self.latitude = [34.901034609560796] 
        self.longitude = [-86.6156509355818] 
        self.location_map = folium.Map(location = [self.latitude[0], self.longitude[0]], zoom_start=13)
        self.icon = folium.CustomIcon('C:/Users/kayla/Python311/GCS/wheres_little_wing.png', icon_size = (36,30)) 
        self.location_map = folium.Map(location = [self.latitude[0], self.longitude[0]], zoom_start = 13)
        folium.Marker(location = [self.latitude[0], self.longitude[0]], popup = 'Little Wing', icon = self.icon).add_to(self.location_map)    
        
        # save map data to data object
        data = BytesIO()
        self.location_map.save(data,close_file = False)
        html = data.getvalue().decode()
        self.webView = QWebEngineView(self.graph_frame)
        self.gridLayout.addWidget(self.webView, 1, 2, 1, 1)
        self.webView.setHtml(html)      

        # adding wingstop logo
        self.logo_layout = QtWidgets.QFrame(self.centralwidget)
        self.logo_layout.setGeometry(QtCore.QRect(26, 26, 470, 285))
        self.logo_layout.setStyleSheet('border: 10px solid black')
        self.logo_pixmap = QtGui.QPixmap("C:/Users/kayla/Downloads/wingstop_logo.png")
        self.logo_width, self.logo_height = 450, 450
        self.logo_pixmap = self.logo_pixmap.scaled(self.logo_width, self.logo_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.logo_label = QtWidgets.QLabel(self.logo_layout)
        self.logo_label.setPixmap(self.logo_pixmap)

        # party after clicking logo
        self.logo_button = QtWidgets.QPushButton(self.centralwidget)
        self.logo_button.setGeometry(QtCore.QRect(26, 26, 470, 285))
        self.logo_button.setStyleSheet("background-color: transparent")
        self.logo_button.setObjectName("party")
        #self.logo_layout.addWidget(self.logo_button)
        #self.logo.setFont(self.button_font)
        self.logo_button.clicked.connect(self.party) 
        
        # adding wingstop quote
        self.slogan_layout = QtWidgets.QFrame(self.centralwidget)
        self.slogan_layout.setGeometry(QtCore.QRect(720, 46, 1373, 100))
        self.sloganLabel = QtWidgets.QLabel(self.slogan_layout)
        self.sloganLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.sloganLabel.setStyleSheet('color: white; font-weight: bold; font-family: Roc Grotesk; font-size: 30pt;')
        self.sloganLabel.setText("Wing-Stop Don't Stop! Go Little Wing!")

        # adding chicken wings
        wing1_layout = QtWidgets.QFrame(self.centralwidget)
        wing1_layout.setGeometry(QtCore.QRect(500, 26, 100, 100))
        wing1_pixmap = QtGui.QPixmap("C:/Users/kayla/Python311/GCS/wheres_little_wing.png")
        wing1_width, wing1_height = 100, 100
        wing1_pixmap = wing1_pixmap.scaled(wing1_width, wing1_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.wing1_label = QtWidgets.QLabel(wing1_layout)
        self.wing1_label.setPixmap(wing1_pixmap)

        wing2_layout = QtWidgets.QFrame(self.centralwidget)
        wing2_layout.setGeometry(QtCore.QRect(600, 26, 100, 100))
        wing2_pixmap = QtGui.QPixmap("C:/Users/kayla/Python311/GCS/wheres_little_wing.png")
        wing2_width, wing2_height = 100, 100
        wing2_pixmap = wing2_pixmap.scaled(wing2_width, wing2_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.wing2_label = QtWidgets.QLabel(wing2_layout)
        self.wing2_label.setPixmap(wing2_pixmap)

        wing3_layout = QtWidgets.QFrame(self.centralwidget)
        wing3_layout.setGeometry(QtCore.QRect(1700, 26, 100, 100))
        wing3_pixmap = QtGui.QPixmap("C:/Users/kayla/Python311/GCS/wheres_little_wing.png")
        wing3_width, wing3_height = 100, 100
        wing3_pixmap = wing3_pixmap.scaled(wing3_width, wing3_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.wing3_label = QtWidgets.QLabel(wing3_layout)
        self.wing3_label.setPixmap(wing3_pixmap)

        wing4_layout = QtWidgets.QFrame(self.centralwidget)
        wing4_layout.setGeometry(QtCore.QRect(1800, 26, 100, 100))
        wing4_pixmap = QtGui.QPixmap("C:/Users/kayla/Python311/GCS/wheres_little_wing.png")
        wing4_width, wing4_height = 100, 100
        wing4_pixmap = wing4_pixmap.scaled(wing4_width, wing4_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.wing4_label = QtWidgets.QLabel(wing4_layout)
        self.wing4_label.setPixmap(wing4_pixmap)

        # creating button frame
        self.button_frame = QtWidgets.QFrame(self.centralwidget)
        self.button_frame.setGeometry(QtCore.QRect(512, 122, 1373, 100))
        self.button_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.button_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.button_frame.setObjectName("button_frame")
        self.button_font = QtGui.QFont('Roc Grotesk', 14)
        self.button_font.setBold
        self.button_frame.setStyleSheet('border: 10px solid black')

        # creating layout for buttons
        self.button_layout = QtWidgets.QHBoxLayout(self.button_frame)
        self.button_layout.setObjectName("button_layout")

        # start serial read button
        self.beacon = QtWidgets.QPushButton(self.button_frame)
        self.beacon.setStyleSheet("background-color : white")
        self.beacon.setObjectName("beacon")
        self.button_layout.addWidget(self.beacon)
        self.beacon.setFont(self.button_font)
        self.beacon.clicked.connect(self.start_serial_read) 

        # calibrate button
        self.calibrate = QtWidgets.QPushButton(self.button_frame)
        self.calibrate.setStyleSheet("background-color : white")
        self.calibrate.setObjectName("calibrate")
        self.button_layout.addWidget(self.calibrate)
        self.calibrate.setFont(self.button_font)
        self.calibrate.clicked.connect(self.calibrate_was_clicked) 

        # release button
        self.release = QtWidgets.QPushButton(self.button_frame)
        self.release.setStyleSheet("background-color : white")
        self.release.setObjectName("release")
        self.button_layout.addWidget(self.release)
        self.release.setFont(self.button_font)
        self.release.clicked.connect(self.release_was_clicked) 

        # creating table for live data
        self.table_frame = QtWidgets.QTableWidget(self.centralwidget)
        self.table_frame.setGeometry(QtCore.QRect(26, 326, 470, 726))
        self.table_frame.setStyleSheet('border: 10px solid black')
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.verticalHeader().setStyleSheet("""QHeaderView::section {font-size: 10pt; font-family: 'Roc Grotesk'; font-weight: bold; padding: 4px; }""")
        self.tableWidget.setStyleSheet('background color: white;')
        self.tableWidget.setGeometry(QtCore.QRect(36, 336, 450, 706)) 
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.tableWidget.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget.setWordWrap(True)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        
        # creating rows and columns of the table as well as setting colors and fonts
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(14)
        self.tableWidget.setStyleSheet("background-color : white")
        self.table_font = QtGui.QFont('Roc Grotesk', 12)
        self.table_font.setBold

        # team ID
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(self.team_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # mission time
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.mission_list[-1]))
        self.tableWidget.setFont(self.table_font)

        # packet count
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        self.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(self.packet_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # software state
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        self.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(self.sw_list[-1]))
        self.tableWidget.setFont(self.table_font)
        
        # payload state
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, item)
        self.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(self.pl_list[-1]))
        self.tableWidget.setFont(self.table_font)

        # air speed
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        self.tableWidget.setItem(0, 5, QtWidgets.QTableWidgetItem(str(self.speed_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # altitude
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, item)
        self.tableWidget.setItem(0, 6, QtWidgets.QTableWidgetItem(str(self.altitude_list[-1])))
        self.tableWidget.setFont(self.table_font)

        # temperature
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, item)
        self.tableWidget.setItem(0, 7, QtWidgets.QTableWidgetItem(str(self.temperature_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # voltage
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, item)
        self.tableWidget.setItem(0, 8, QtWidgets.QTableWidgetItem(str(self.voltage_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # latitude
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, item)
        self.tableWidget.setItem(0, 9, QtWidgets.QTableWidgetItem(str(self.latitude_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # longitude
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(10, item)
        self.tableWidget.setItem(0, 10, QtWidgets.QTableWidgetItem(str(self.longitude_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # gyro roll
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(11, item)
        self.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem(str(self.roll_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # gyro pitch
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(12, item)
        self.tableWidget.setItem(0, 12, QtWidgets.QTableWidgetItem(str(self.pitch_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        # gyro yaw
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(13, item)
        self.tableWidget.setItem(0, 13, QtWidgets.QTableWidgetItem(str(self.yaw_list[-1])))
        self.tableWidget.setFont(self.table_font)
        
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        
        # Making menu and status bar
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1255, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # determing what names are
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Wing-Stop Ground Station"))
        self.beacon.setText(_translate("MainWindow", "Start Serial"))
        self.calibrate.setText(_translate("MainWindow", "Calibrate"))
        self.release.setText(_translate("MainWindow", "Release Glider"))
        self.tableWidget.setSortingEnabled(False)
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Team ID"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "Mission Time"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "Packet Count"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "Software State"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "Payload State"))
        item = self.tableWidget.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "Velocity (m/s)"))
        item = self.tableWidget.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "Altitude (m)"))
        item = self.tableWidget.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "Temperature (°C)"))
        item = self.tableWidget.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "Voltage (V)"))
        item = self.tableWidget.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "Latitude (°N)"))
        item = self.tableWidget.verticalHeaderItem(10)
        item.setText(_translate("MainWindow", "Longitude (°E)"))
        item = self.tableWidget.verticalHeaderItem(11)
        item.setText(_translate("MainWindow", "Gyro Roll (°)"))
        item = self.tableWidget.verticalHeaderItem(12)
        item.setText(_translate("MainWindow", "Gyro Pitch (°)"))
        item = self.tableWidget.verticalHeaderItem(13)
        item.setText(_translate("MainWindow", "Gyro Yaw (°)"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Data"))
    
    # start serial button function
    def start_serial_read(self):
        self.beacon.setStyleSheet("background-color : brown")
        self.start_serial_read = True
        print ('start serial was clicked')
        self.ser = serial.Serial('COM13', 9600, timeout = 2)

        # initializing timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_widgets)
        self.timer.start()
        self.update_information()

    # release button function
    def release_was_clicked(self):
        with self.ser:
            self.release_string = 'lemon pepper'
            self.ser.write(self.release_string.encode('utf-8'))
        print('release was clicked')
        self.release.setStyleSheet("background-color : brown")
    
    # calibration button function
    def calibrate_was_clicked(self):
        with self.ser:
            self.release_string = 'hot honey'
            self.ser.write(self.release_string.encode('utf-8'))
        print('calibrate was clicked')
        self.calibrate.setStyleSheet("background-color : brown")

    def party(self):
        print('party time!')
        # DO SOMETHING FUN

    # updating information lists
    def update_information(self):
        with self.ser:
            if self.start_serial_read == True:   
                #print('reading') 
                data = self.ser.readline().decode('UTF-8', errors='ignore').strip()

                # getting information into a single list
                if data is not None:
                    #print('data')
                    first_list = data.split(',,')
                    req_list = first_list[0]
                    our_list = first_list[1]
                    data_list = req_list.split(',')
                    extra_list = our_list.split(',')
                    data_list.append(extra_list[0])
                    data_list.append(extra_list[1])
                    with open("WingStop.csv", mode = 'a', newline = '') as file:
                        writer = csv.writer(file)
                        writer.writerow(data_list)

                    # separating main data list into individual lists
                    if len(data_list) >= 15:
                        #print(data_list)
                        #print('data is updating')
                        self.team_list.append(int(data_list[0]))
                        self.mission_list.append(data_list[1])
                        self.packet_list.append(int(data_list[2]))
                        self.sw_list.append(data_list[3])
                        self.pl_list.append(data_list[4])
                        self.altitude_list.append(float(data_list[5]))
                        self.temperature_list.append(float(data_list[6]))
                        self.voltage_list.append(float(data_list[7]))
                        self.latitude_list.append(float(data_list[8]))
                        self.longitude_list.append(float(data_list[9]))
                        self.roll_list.append(float(data_list[10]))
                        self.pitch_list.append(float(data_list[11]))
                        self.yaw_list.append(float(data_list[12]))
                        self.pressure_list.append(float(data_list[13]))
                        self.speed_list.append(float(data_list[14]))
    
    # function to update widgets
    def update_widgets(self):
        #print('updating')

        # update information
        self.update_information()

        # update time
        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1)

        # update altitude graph
        self.alt_graph = self.alt_graph[1:]
        self.alt_graph.append(self.altitude_list[-1]) # replace with sensor data
        self.aline.setData(self.time, self.alt_graph)

        # update temperature graph
        self.temp_graph = self.temp_graph[1:]
        self.temp_graph.append(self.temperature_list[-1]) # replace with sensor data
        self.line.setData(self.time, self.temp_graph)

        # update pressure graph
        self.pressure_graph = self.pressure_graph[1:]
        self.pressure_graph.append(self.pressure_list[-1]) # replace with sensor data
        self.pline.setData(self.time, self.pressure_graph)

        # update air speed graph
        self.speed_graph = self.speed_graph[1:]
        self.speed_graph.append(self.speed_list[-1]) # replace with sensor data
        self.sline.setData(self.time, self.speed_graph)

        # update tilt graph
        self.roll = self.roll[1:]
        self.roll.append(self.roll_list[-1]) # replace with sensor data
        self.roll_curve.setData(self.time, self.roll)
        self.pitch = self.pitch[1:]
        self.pitch.append(self.pitch_list[-1])
        self.pitch_curve.setData(self.time, self.pitch)
        self.yaw = self.yaw[1:]
        self.yaw.append(self.yaw_list[-1])
        self.yaw_curve.setData(self.time, self.yaw)

        # update gps marker location
        self.location_map = folium.Map(location = [self.latitude[-1], self.longitude[-1]], zoom_start = 13)
        folium.Marker([self.latitude[-1], self.longitude[-1]], popup = "Little Wing!", icon = self.icon).add_to(self.location_map)
        data = BytesIO()
        self.location_map.save(data, close_file=False)
        html = data.getvalue().decode()
        self.webView.setHtml(html)

        # updating table values
        self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(self.team_list[-1])))
        self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.mission_list[-1]))
        self.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(self.packet_list[-1])))
        self.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(self.sw_list[-1]))
        self.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(self.pl_list[-1]))
        self.tableWidget.setItem(0, 5, QtWidgets.QTableWidgetItem(str(self.speed_list[-1])))
        self.tableWidget.setItem(0, 6, QtWidgets.QTableWidgetItem(str(self.altitude_list[-1])))
        self.tableWidget.setItem(0, 7, QtWidgets.QTableWidgetItem(str(self.temperature_list[-1])))
        self.tableWidget.setItem(0, 8, QtWidgets.QTableWidgetItem(str(self.voltage_list[-1])))
        self.tableWidget.setItem(0, 9, QtWidgets.QTableWidgetItem(str(self.latitude_list[-1])))
        self.tableWidget.setItem(0, 10, QtWidgets.QTableWidgetItem(str(self.longitude_list[-1])))
        self.tableWidget.setItem(0, 11, QtWidgets.QTableWidgetItem(str(self.roll_list[-1])))
        self.tableWidget.setItem(0, 12, QtWidgets.QTableWidgetItem(str(self.pitch_list[-1])))
        self.tableWidget.setItem(0, 13, QtWidgets.QTableWidgetItem(str(self.yaw_list[-1])))

# opening main window
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
