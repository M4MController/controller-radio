import serial

# Connect to Xbee
ser = serial.Serial("/dev/ttyUSB0", 19200)

# Send data (a string)
ser.write(b"sfs")
