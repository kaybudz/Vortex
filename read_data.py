import serial
import serial.tools.list_ports
import csv
import threading
import time

# add more error mitigation 
class live_read():
    def __init__(self, port=None, baud=115200):
        self.start = False
        self.simEnabled = False
        self.simulation = False
        # self.csv_filename = 'C:/Users/kayla/Python311/Vortex/cansat_2023_simp.txt'
        self.csv_filename = 'Flight_1093.csv'
        self.sim_filename = ''
        self.port = port
        self.chosen_port = self.port
        self.baud = baud
        self.port_list = []
        self.avport = serial.tools.list_ports.comports()
        
        # selecting the port
        for port in self.avport:
            self.port_list.append(port.device)
            
        # making lists for individual variables
        # initial conditions are example packet from launchpad
        self.team = [0,0]
        self.time = [0,0]
        self.pckt = [0,0]
        self.mode = [0,0]
        self.state = [0,0]
        self.alt = [0,0]
        self.temp = [0,0]
        self.press = [0,0]
        self.volt = [0,0]
        self.curr = [0,0]
        self.g_roll = [0,0]
        self.g_pitch = [0,0]
        self.g_yaw = [0,0]
        self.a_roll =[0,0]
        self.a_pitch = [0,0]
        self.a_yaw = [0,0]
        self.gps_time = [0,0]
        self.gps_alt = [0,0]
        self.lat = [0,0]
        self.lon = [0,0]
        self.sats = [0,0]
        self.cmd = [0,0]
        self.data_list = [0,0]
    
    def select_port(self):
        if self.chosen_port is not None:
            try:
                self.ser = serial.Serial(self.chosen_port, self.baud, timeout=0.1)
                print(f"Connected to {self.chosen_port}")
                self.port = self.chosen_port
            except serial.SerialException:
                print(f"ERROR: Could not open {self.chosen_port}")
        else:
            print("ERROR: No port selected")
            return

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
                with open("Flight_1093.csv", mode = 'a', newline = '') as file:
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
                    self.gps_time.append((self.data_list[16])) # gps time
                    self.gps_alt.append(float(self.data_list[17])) # gps altitude
                    self.lat.append(float(self.data_list[18])) # latitude
                    self.lon.append(float(self.data_list[19])) # longitude
                    self.sats.append(float(self.data_list[20])) # satellites
                    # self.cmd.append(self.data_list[21]) # command echo
                    self.cmd.append(",".join(self.data_list[21:]))
                else: 
                    print('ERROR: Packet is too short')
    # def update(self):
    #     if not self.start:
    #         return False

    #     data = self.ser.readline().decode('UTF-8', errors='ignore').strip()

    #     if not data:
    #         return False

    #     print(f"RECEIVED: {data}")

    #     data_list = data.split(',')
    #     with open("Flight_1093.csv", mode = 'a', newline = '') as file:
    #         writer = csv.writer(file)
    #         writer.writerow(self.data_list)

    #     if len(data_list) < 22:
    #         print(f"IGNORED NON-TELEMETRY OR SHORT PACKET: {data}")
    #         return False

    #     try:
    #         self.team.append(int(self.data_list[0]))
    #         self.time.append(self.data_list[1])
    #         self.pckt.append(int(self.data_list[2]))
    #         self.mode.append(self.data_list[3])
    #         self.state.append(self.data_list[4])
    #         self.alt.append(float(self.data_list[5]))
    #         self.temp.append(float(self.data_list[6]))
    #         self.press.append(float(self.data_list[7]))
    #         self.volt.append(float(self.data_list[8]))
    #         self.curr.append(float(self.data_list[9]))
    #         self.g_roll.append(float(self.data_list[10]))
    #         self.g_pitch.append(float(self.data_list[11]))
    #         self.g_yaw.append(float(self.data_list[12]))
    #         self.a_roll.append(float(self.data_list[13]))
    #         self.a_pitch.append(float(self.data_list[14]))
    #         self.a_yaw.append(float(self.data_list[15]))
    #         self.gps_time.append(self.data_list[16])
    #         self.gps_alt.append(float(self.data_list[17]))
    #         self.lat.append(float(self.data_list[18]))
    #         self.lon.append(float(self.data_list[19]))
    #         self.sats.append(float(self.data_list[20]))
    #         self.cmd.append(",".join(self.data_list[21:]))

    #         return True

    #     except (ValueError, IndexError) as e:
    #         print(f"TELEMETRY PARSE ERROR: {e}")
    #         print(f"RAW PACKET: {data}")
    #         return False
    
    # TEST THAT THIS ACTUALLY WORKS
    def send(self,command):
        try:
            # self.write = serial.Serial('COM6', 115200, timeout=2) #COM is subject to change
            self.ser.write(command.encode('UTF-8'))
        except:
            print('ERROR: Port not found')
        print(command)

    def start_sim(self, sim_filename):
        self.simulation = True
        self.sim_thread = threading.Thread(target=self.run_sim, args=(sim_filename,), daemon=True)
        self.sim_thread.start()

    # FAKE SIM MODE
    def run_sim(self, csv_filename):
        with open(csv_filename, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None) # skips header if present
            for line in csv_reader:
                self.data_list = line
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
                    self.gps_time.append((self.data_list[16])) # gps time
                    self.gps_alt.append(float(self.data_list[17])) # gps altitude
                    self.lat.append(float(self.data_list[18])) # latitude
                    self.lon.append(float(self.data_list[19])) # longitude
                    self.sats.append(float(self.data_list[20])) # satellites
                    self.cmd.append(",".join(self.data_list[21:]))
                else: 
                    print('ERROR: Packet is too short')
                
                # delays to 1Hz
                time.sleep(1)
                
                # breaks sim if stop sim is recieved
                if not self.simulation: # sim is disabled
                    break

    # def run_sim(self, sim_filename):
    #     with open(sim_filename, mode='r') as file:
    #         csv_reader = csv.reader(file)
    #         next(csv_reader, None) # skips header if present
    #         for line in csv_reader:
    #             # print(line)
    #             # if line[0:1] == '#':
    #             #     print('Skipped Line')
    #             #     continue  # Skip this line
    #             try:
    #                 self.sim_data_list = line
    #                 self.sim_data_list[1] = '1093'
    #                 self.simp = ','.join(self.sim_data_list)
    #                 #self.ser.write(self.simp.encode('UTF-8'))
    #                 self.ser.write((self.simp + '\n').encode('UTF-8'))
    #                 print(self.simp)
    #             except: 
    #                 print('ERROR')
                
    #             # delays to 1Hz
    #             time.sleep(1)
                
    #             # breaks sim if stop sim is recieved
    #             if not self.simulation: # sim is disabled
    #                 break
    
    def stop_sim(self):
        self.simulation = False