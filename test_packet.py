import time
import serial

class Test:
    def fake_packet(self):
        self.ser = serial.Serial('COM6', 115200, timeout=0.1)

        # Start with 1..24
        self.packet = [i for i in range(1, 25)]

        while True:
            # Convert list → bytes
            data = bytes(self.packet)
            self.ser.write(data)
            print("Sent:", data)

            # Increment each byte, wrap at 255
            self.packet = [(b + 1) % 256 for b in self.packet]

            time.sleep(1)  # <-- send once per second
            print(self.packet)


