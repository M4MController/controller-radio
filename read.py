import serial

# Connect to Xbee
ser = serial.Serial("/dev/ttyACM0", 19200)

while True:
    print(ser.read())
