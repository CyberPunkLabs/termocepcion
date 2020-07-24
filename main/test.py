iimport serial

port = '/dev/ttyUSB0'

uart = serial.Serial(port, baudrate = 115_200, bytesize = 8, parity = 'N', stopbits = 1, timeout = 0)

while True:
    if uart.in_waiting > 0:
        print(uart.read(uart.in_waiting))
