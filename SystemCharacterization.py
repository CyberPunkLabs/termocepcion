import atexit
import time
import numpy
import matplotlib.pyplot as pyplot

from Chamber import *
from Pid import *
from SetPoint import *


# Configuration variables

port = 'COM3'

dt_ = 0.750

powerValues   = numpy.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8])

#powerValues   = numpy.array([0.8, 0.6, 0.4, 0.2, 0.0, -0.2, -0.4, -0.6, -0.8, -1.0])
powerDuration = numpy.array([15, 10, 10, 10, 10, 10, 10, 10, 10, 10]) * 60.

duration = powerDuration.sum()

power = Step(powerValues, powerDuration)


# Functions / classes

def save():
    pyplot.close()

    print('Saving data...')
        
    metadata = {}
    metadata['Duration']  = elapsed
    metadata['Timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tStart))

    t  = numpy.array(T_)
    p  = numpy.array(P_)

    numpy.savez('../Data/SystemCharacterization_%s.npz' % time.strftime('%Y-%m-%d_%H%M', time.localtime(tStart)), Metadata = metadata, T = t, P = p)


def log(elapsed, T_, P_):
    timeString    = '[{:.1f} s]'.format(elapsed)
    chamberString = 'T: {:.2f} \u00B0C, P: {:.3f} au'.format(T_[-1], P_[-1])

    return '{:s} {:s}'.format(timeString, chamberString)


class Plot:
    def __init__(self):
        self._init = False
         
    def __call__(self, elapsed, T_, P_):
        if len(T_) > 2:
            if self._init == False:
                self._init = True

                pyplot.ion()
                self._fig, (self._ax0, self._ax1) = pyplot.subplots(2, 1, gridspec_kw = {'height_ratios': [3, 1]})

                self._l0a, = self._ax0.plot([], [], color = 'k')
                self._l0b, = self._ax0.plot([], [], color = 'C1')
                self._ax0.set_ylabel('T (\u00B0C)', color = 'C1')
                #self._ax0.set_xticks([])
                self._ax0.set_xlabel('Time (min)')

                self._l1, = self._ax1.plot([], [], color = 'C0')
                self._ax1.set_ylabel('P (au)', color = 'C0')
                self._ax1.set_ylim(-1.05, 1.05)
                self._ax1.set_xticks([])

            tChamber = numpy.linspace(0, elapsed, len(T_))

            t  = numpy.array(T_)
            p  = numpy.array(P_)

            self._l0b.set_xdata(tChamber / 60.)
            self._l0b.set_ydata(t)

            self._l1.set_xdata(tChamber / 60.)
            self._l1.set_ydata(p)

            self._ax0.set_xlim(tChamber[0] / 60., tChamber[-1] / 60.)
            self._ax1.set_xlim(tChamber[0] / 60., tChamber[-1] / 60.)

            Tmin0_ = min(t)
            Tmax0_ = max(t)
            
            if (Tmin0_ != Tmax0_):
                delta = (Tmax0_ - Tmin0_) / 50.
                self._ax0.set_ylim(Tmin0_ - delta, Tmax0_ + delta)
                
            self._fig.tight_layout()
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()


# Code
chamber = Chamber(port)

plot = Plot()

T_  = []
P_  = []

tStart = time.time()

while True:
    newT = chamber.read()

    if chamber.error:
        print('ERROR: Temperature chamber data link error!')
        quit()

    elapsed = time.time() - tStart

    if elapsed > duration:
        print('Execution Complete.')
        break

    if len(newT) > 0:
        newP = power(elapsed)
        
        chamber.write(newP, 0)

        if (len(P_) > 0.):
            lastP  = P_[-1]
        else:
            lastP  = 0.

        for i in range(len(newT) - 1):
            P_.append(lastP)

        T_.extend(list(numpy.array(newT)[:, 0]))
        P_.append(newP)

    if len(newT) > 0:
        print(log(elapsed, T_, P_))
        plot(elapsed, T_, P_)

save()