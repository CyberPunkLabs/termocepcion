
import atexit
import time
import numpy
#import matplotlib.pyplot as pyplot

from Chamber import *
from Pid import *
from SetPoint import *

port = '/dev/ttyUSB0'


chamber = Chamber(port)

while True:
    temp = chamber.read()

    if len(temp) > 0:
        print(temp)
