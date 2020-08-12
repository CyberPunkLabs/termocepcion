import atexit
import time
import numpy

from Chamber import *
from Pid import *
from SetPoint import *


port = '/dev/ttyUSB0'

p = 4.0
target = numpy.array([12, 10])


chamber = Chamber(port)

while True:
    temp = chamber.read()

    if len(temp) > 0:
        temp = numpy.array(temp[0])

        error = target - temp
        out = numpy.clip(error * p, -1.0, 1.0)

        chamber.write(out[0], out[1])

        print("Temperature: [{:.2f}, {:.2f}], Output: [{:.2f}, {:.2}]".format(temp[0], temp[1], out[0], out[1]))
