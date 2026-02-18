import serial
import csv
import threading
import time
# do i need to import time??

# add more error mitigation 
class live_read():
    def __init__(self, port='COM8', baud=115200):
        self.start = False
        self.simEnabled = False
        self.simulation = False
        self.csv_filename = 'Vortex_1093.csv'

        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            print(f"Connected to {port}")
        except serial.SerialException:
            print(f"ERROR: Could not open {port}")
            self.ser = None
            
        # making lists for individual variables
        # initial conditions are example packet from launchpad
        self.team = []
        self.time = []
        self.pckt = []
        self.mode = []
        self.state = []
        self.alt = []
        self.temp = []
        self.press = []
        self.volt = []
        self.curr = []
        self.g_roll = []
        self.g_pitch = []
        self.g_yaw = []
        self.a_roll =[]
        self.a_pitch = []
        self.a_yaw = []
        self.gps_time = []
        self.gps_alt = []
        self.lat = []
        self.lon = []
        self.sats = []
        self.cmd = []
        self.data_list = []

    def start_read(self):
        self.start = True
        # SET UP COM TO BE AN INPUT OPTION?

    def update(self):
        # with self.serial.readline():
            #print('update has been run')
        if self.start == True:
            data = self.ser.readline().decode('UTF-8', errors='ignore').strip()
            if data:
                    #print('data')
                    # first_list = data.split(',,')
                    # req_list = first_list[0]
                    # ex_list = first_list[1]
                    # data_list = req_list.split(',')
                    # extra_list = ex_list.split(',')
                    # data_list.append(extra_list[0])
                    # data_list.append(extra_list[1])
                    self.data_list = data.split(',')
                    with open("Vortex_1093.csv", mode = 'a', newline = '') as file:
                        writer = csv.writer(file)
                        writer.writerow(self.data_list)
                    
                    # separating main data list into individual lists
                    if len(self.data_list) >= 22:
                        #print(data_list)
                        #print('data is updating')
                        self.team.append(int(self.data_list[0])) # team ID
                        self.time.append(self.data_list[1]) # mission time
                        self.pckt.append(int(self.data_list[2])) # packet count
                        self.mode.append(self.data_list[3]) # flight or sim mode
                        self.state.append(self.data_list[4]) # fsw state
                        self.alt.append(float(self.data_list[5])) # altitude
                        self.temp.append(float(self.data_list[6])) # temperature
                        self.press.append(float(self.data_list[7])) # pressure
                        self.volt.append(float(self.data_list[8])) # voltage
                        self.curr.append(float(self.data_list[9])) # current
                        self.g_roll.append(float(self.data_list[10])) # gyro roll
                        self.g_pitch.append(float(self.data_list[11])) # gyro pitch
                        self.g_yaw.append(float(self.data_list[12])) # gyro yaw
                        self.a_roll.append(float(self.data_list[13])) # accel roll
                        self.a_pitch.append(float(self.data_list[14])) # accel pitch
                        self.a_yaw.append(float(self.data_list[15])) # accel yaw
                        self.gps_time.append(float(self.data_list[16])) # gps time
                        self.gps_alt.append(float(self.data_list[17])) # gps altitude
                        self.lat.append(float(self.data_list[18])) # latitude
                        self.lon.append(float(self.data_list[19])) # longitude
                        self.sats.append(int(self.data_list[20])) # satellites
                        self.cmd.append(self.data_list[21]) # command echo
                    else: 
                        print('ERROR: Packet is too short')
    
    # TEST THAT THIS ACTUALLY WORKS
    def send(self,command):
        try:
            # self.write = serial.Serial('COM6', 115200, timeout=2) #COM is subject to change
            self.ser.write(command.encode('UTF-8'))
        except:
            print('ERROR: Port not found')
        print(command)

    def start_sim(self, csv_filename):
        self.simulation = True
        self.sim_thread = threading.Thread(target=self.run_sim, args=(csv_filename,), daemon=True)
        self.sim_thread.start()

    def run_sim(self, csv_filename):
        with open(csv_filename, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None) # skips header if present
            for line in csv_reader:
                if not self.simulation: # sim is disabled
                    break
                if line and line [0] == 'CMD': # a command has been sent
                    line[1] = '1093'
                    command = ','.join(line) # joins packet separated by commas
                    self.send(command)
    
    def stop_sim(self, command):
        self.simulation = False