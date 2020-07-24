import atexit
import time
import numpy
import matplotlib.pyplot as pyplot

from Chamber import *
from Pid import *
from SetPoint import *


# Configuration variables

port = 'COM3'

ambientT = 23

dt_ = 0.750

Kp_ = 0.6
Ki_ = 0.005
Kd_ = 0.000


setPointValues0   = numpy.array([25., 10., 40., 10., 20., 30., 40., 30., 20., 10.])
setPointDuration0 = numpy.array([ 3.,  3.,  4.,  6.,  2.,  2.,  2.,  2.,  2.,  2.]) * 60.

setPointValues1   = numpy.array([10., 20., 30., 40.])
setPointDuration1 = numpy.array([5., 5., 5., 5.]) * 60.

duration = setPointDuration0.sum()

setPoint0 = Step(setPointValues0, setPointDuration0)
setPoint1 = Step(setPointValues1, setPointDuration1)


# Functions / classes

def save():
    pyplot.close()

    print('Saving data...')
        
    metadata = {}
    metadata['Duration']  = elapsed
    metadata['Timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tStart))
    metadata['Kp']        = Kp_
    metadata['Ki']        = Ki_
    metadata['Kd']        = Kd_

    sp = numpy.array(SP_)
    t  = numpy.array(T_)
    p  = numpy.array(P_)
    pid = numpy.array(PID_)

    numpy.savez('../Data/Data_%s.npz' % time.strftime('%Y-%m-%d_%H%M', time.localtime(tStart)), Metadata = metadata, SP = sp, T = t, P = p, PID = pid)


def log(elapsed, SP_, T_, P_, PID_):
    timeString    = '[{:.1f} s]'.format(elapsed)
    chamberString0 = 'Chamber0: [SP: {:.2f} \u00B0C, T: {:.2f} \u00B0C, P: {:.3f} AU, PID: ({:+.3f}, {:+.3f}, {:+.3f})]'.format(SP_[-1][0], T_[-1][0], P_[-1][0], PID_[-1][0][0], PID_[-1][0][1], PID_[-1][0][2])
    chamberString1 = 'Chamber1: [SP: {:.2f} \u00B0C, T: {:.2f} \u00B0C, P: {:.3f} AU, PID: ({:+.3f}, {:+.3f}, {:+.3f})]'.format(SP_[-1][1], T_[-1][1], P_[-1][1], PID_[-1][0][0], PID_[-1][0][1], PID_[-1][0][2])

    return '{:s} {:s} {:s}'.format(timeString, chamberString0, chamberString1)


class Plot:
    def __init__(self):
        self._init = False
         
    def __call__(self, elapsed, SP_, T_, P_, PID_):
        if len(T_) > 2:
            if self._init == False:
                self._init = True

                pyplot.ion()
                self._fig, (self._ax0, self._ax1, self._ax2, self._ax3) = pyplot.subplots(4, 1, gridspec_kw = {'height_ratios': [3, 1, 3, 1]})

                self._ax0.set_title('Chamber 0')
                self._l0a, = self._ax0.plot([], [], color = 'k')
                self._l0b, = self._ax0.plot([], [], color = 'C1')
                self._ax0.set_ylabel('T (\u00B0C)', color = 'C1')

                self._l1, = self._ax1.plot([], [], color = 'C0')
                self._ax1.set_ylabel('P (au)', color = 'C0')
                self._ax1.set_ylim(-1.05, 1.05)
                self._ax1.set_xticks([])

                self._ax2.set_title('Chamber 1')
                self._l2a, = self._ax2.plot([], [], color = 'k')
                self._l2b, = self._ax2.plot([], [], color = 'C1')
                self._ax2.set_ylabel('T (\u00B0C)', color = 'C1')

                self._l3, = self._ax3.plot([], [], color = 'C0')
                self._ax3.set_ylabel('P (au)', color = 'C0')
                self._ax3.set_ylim(-1.05, 1.05)
                self._ax3.set_xticks([])
                self._ax3.set_xlabel('Time (min)')

            tChamber = numpy.linspace(0, elapsed, len(T_))

            sp = numpy.array(SP_)
            t  = numpy.array(T_)
            p  = numpy.array(P_)

            self._l0a.set_xdata(tChamber / 60.)
            self._l0a.set_ydata(sp[:, 0])

            self._l0b.set_xdata(tChamber / 60.)
            self._l0b.set_ydata(t[:, 0])

            self._l1.set_xdata(tChamber / 60.)
            self._l1.set_ydata(p[:, 0])

            self._l2a.set_xdata(tChamber / 60.)
            self._l2a.set_ydata(sp[:, 1])

            self._l2b.set_xdata(tChamber / 60.)
            self._l2b.set_ydata(t[:, 1])

            self._l3.set_xdata(tChamber / 60.)
            self._l3.set_ydata(p[:, 1])

            self._ax0.set_xlim(tChamber[0] / 60., tChamber[-1] / 60.)
            self._ax1.set_xlim(tChamber[0] / 60., tChamber[-1] / 60.)
            self._ax2.set_xlim(tChamber[0] / 60., tChamber[-1] / 60.)
            self._ax3.set_xlim(tChamber[0] / 60., tChamber[-1] / 60.)

            Tmin0_ = min(min(t[:, 0]), min(sp[:, 0]))
            Tmax0_ = max(max(t[:, 0]), max(sp[:, 0]))
            Tmin1_ = min(min(t[:, 1]), min(sp[:, 1]))
            Tmax1_ = max(max(t[:, 1]), max(sp[:, 1]))
            
            if (Tmin0_ != Tmax0_):
                delta = (Tmax0_ - Tmin0_) / 50.
                self._ax0.set_ylim(Tmin0_ - delta, Tmax0_ + delta)
            
            if (Tmin1_ != Tmax1_):
                delta = (Tmax1_ - Tmin1_) / 50.
                self._ax2.set_ylim(Tmin1_ - delta, Tmax1_ + delta)
                
            self._fig.tight_layout()
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()


# Code
chamber = Chamber(port)

polynomialFix = numpy.load('../Data/Polynomial.npy')
#fix = numpy.poly1d(polynomial)
fix = lambda x: numpy.clip(numpy.poly1d(polynomialFix)(numpy.clip(x, -1.1, 1.9)), -1., 1.)

polynomialReverse = numpy.load('../Data/PolynomialReverse.npy')
reverse = numpy.poly1d(polynomialReverse)

pid0 = Pid(Kp_, Ki_, Kd_, dt_)
pid1 = Pid(Kp_, Ki_, Kd_, dt_)

plot = Plot()

SP_  = []
T_   = []
P_   = []
PID_ = []

tStart = time.time()

while True:
    newT = chamber.read()

    if chamber.error:
        print('ERROR: Temperature chamber data link error!')
        quit()

    elapsed = time.time() - tStart

    if elapsed > duration:
        print('Execution Complete.')
        save()
        break

    if len(newT) > 0:
        newSp0 = setPoint0(elapsed)
        newSp1 = setPoint1(elapsed)

        bias0 = reverse(newT[-1][0] - ambientT)

        newP0 = fix(bias0 + pid0(newSp0, newT[-1][0]))
        newP1 = fix(pid1(newSp1, newT[-1][1]))
        
        chamber.write(newP0, newP1)

        if (len(P_) > 0.):
            lastSp  = SP_[-1]
            lastP   = P_[-1]
            lastPID = PID_[-1]
        else:
            lastSp  = [0., 0.]
            lastP   = [0., 0.]
            lastPID = [[0., 0., 0.], [0., 0., 0.]]

        for i in range(len(newT) - 1):
            SP_.append(lastSp)
            P_.append(lastP)
            PID_.append(lastPID)

        SP_.append([newSp0, newSp1])
        T_.extend(newT)
        P_.append([newP0, newP1])
        PID_.append([pid0.PID, pid1.PID])

    if len(newT) > 0:
        print(log(elapsed, SP_, T_, P_, PID_))
        plot(elapsed, SP_, T_, P_, PID_)
