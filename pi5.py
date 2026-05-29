import serial
import time
import serial.tools.list_ports

class lights():
    def __init__(self):

        self.ports = serial.tools.list_ports.comports()
        
        for port in self.ports:
            print(f"Device: {port.device}, Description: {port.description}")
        
        self.used_port = ''

    def write_color(self):
        ser = serial.Serial(self.used_port, baudrate=9600, timeout=1)

        try:
            while True:
                # Data must be sent as bytes
                message = "Hello from Pi 5\n"
                ser.write(message.encode('utf-8')) 
                print(f"Sent: {message.strip()}")
                
                # Optional: Read response
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(f"Received: {line}")
                    
                time.sleep(1)
        except:
            ser.close()