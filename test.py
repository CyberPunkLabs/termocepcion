import atexit
import time
import numpy
import matplotlib.pyplot as pyplot

from Chamber import *
from Pid import *
from SetPoint import *

port = '/dev/ttyUSB0'

while True:
    uart = serial.Serial(port, baudrate = 115_200, bytesize = 8, parity = ‘N’, stopbits = 1, timeout = 0)

    if uart.in_waiting > 0:
        print(uart.read(self._uart.in_waiting))
