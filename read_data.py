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
            self.ser = serial.Serial(port, baud, timeout=2)
            print(f"Connected to {port}")
        except serial.SerialException:
            print(f"ERROR: Could not open {port}")
            self.ser = None
            
        # making lists for individual variables
        # initial conditions are example packet from launchpad
        self.team = ['1093']
        self.time = ['13:39:12']
        self.pckt = [1,2,3,4,5]
        self.mode = ['F']
        self.state = ['DESCENT']
        self.alt = [0.0,13.0]
        self.temp = ['30.1']
        self.press = ['9550.5']
        self.volt = ['10.4']
        self.curr = ['2.53']
        self.g_roll = ['0']
        self.g_pitch = ['0']
        self.g_yaw = ['0']
        self.a_roll =['0']
        self.a_pitch = ['0']
        self.a_yaw = ['0']
        self.gps_time = ['13:39:11']
        self.gps_alt = ['0.4']
        self.lat = ['38.2201']
        self.lon = ['79.3601']
        self.sats = ['6']
        self.cmd = ['CMD1093CAL']

    def start_read(self):
        self.start = True
        # SET UP COM TO BE AN INPUT OPTION?

    def update(self):
        # with self.serial.readline():
            if self.start == True:
                data = self.ser.readline().decode('UTF-8', errors='ignore').strip()
                if data is not None:
                        first_list = data.split(',,')
                        req_list = first_list[0]
                        ex_list = first_list[1]
                        data_list = req_list.split(',')
                        extra_list = ex_list.split(',')
                        data_list.append(extra_list[0])
                        data_list.append(extra_list[1])
                        with open("Vortex_1093.csv", mode = 'a', newline = '') as file:
                            writer = csv.writer(file)
                            writer.writerow(data_list)
                        
                        # separating main data list into individual lists
                        if len(data_list) >= 22:
                            #print(data_list)
                            #print('data is updating')
                            self.team.append(int(data_list[0]))
                            self.time.append(data_list[1])
                            self.pckt.append(int(data_list[2]))
                            self.mode.append(data_list[3])
                            self.state.append(data_list[4])
                            self.alt.append(float(data_list[5]))
                            self.temp.append(float(data_list[6]))
                            self.press.append(float(data_list[7]))
                            self.volt.append(float(data_list[8]))
                            self.curr.append(float(data_list[9]))
                            self.g_roll.append(float(data_list[10]))
                            self.g_pitch.append(float(data_list[11]))
                            self.g_yaw.append(float(data_list[12]))
                            self.a_roll.append(float(data_list[13]))
                            self.a_pitch.append(float(data_list[14]))
                            self.a_yaw.append(float(data_list[15]))
                            self.gps_time.append(float(data_list[16]))
                            self.gps_alt.append(float(data_list[17]))
                            self.lat.append(float(data_list[18]))
                            self.lon.append(float(data_list[19]))
                            self.sats.append(int(data_list[20]))
                            self.cmd.append(data_list[21])
    
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

    # add individual get functions for things on lists??
