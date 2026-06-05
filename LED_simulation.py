import time
import serial

class LED():
    def __init__(self):
        # time.sleep(2)
        try:
            self.ser = serial.Serial("/dev/ttyAMA0")
        except serial.SerialException:
            print(f"ERROR: Could not open port")
        self.flight_states = [
            'LAUNCH_PAD',
            'ASCENT',
            'APOGEE',
            'DESCENT',
            'PROBE_RELEASE',
            'PAYLOAD_RELEASE',
            'LANDED',
            'Waiting',
            'Galaxy'
          ]

    def send_LED(self,state):   
        try:
            message = f"{state}\n"
            self.ser.write(message.encode('utf-8'))
            print('Sent: ',state)
            # time.sleep(4)
        except KeyboardInterrupt:
            print('\nStopping flight state transmission...')
            self.ser.close()
            print('UART closed cleanly')