import serial
import csv

# add more error mitigation 

class live_read():
    start = False

    # making lists for individual variables
    team = []
    time = []
    pckt = []
    mode = []
    state = []
    alt = []
    temp = []
    press = []
    volt = []
    curr = []
    g_roll = []
    g_pitch = []
    g_yaw = []
    a_roll =[]
    a_pitch = []
    a_yaw = []
    gps_time = []
    gps_alt = []
    lat = []
    lon = []
    sats = []
    cmd = []

    def start(self):
        self.read = serial.Serial('COM13', 9600, timeout=2) #COM is subject to change

    def update(self):
        with self.read:
            if self.start == True:
                data = self.read.readline().decode('UTF-8', errors='ignore').strip()
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