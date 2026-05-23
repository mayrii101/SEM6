import serial
import time
import random

# arduino -> tools -> port
PORT = '/dev/cu.usbserial-0001'

# serial connection
esp32 = serial.Serial(PORT, 115200)

time.sleep(2)

states = ["LOW", "MEDIUM", "HIGH"]

while True:
    state = random.choice(states)

    print(f"Sending: {state}")

    esp32.write((state + "\n").encode())

    time.sleep(5)
