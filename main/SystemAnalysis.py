import os
import glob
import time
import numpy
import copy
import matplotlib.pyplot as pyplot
import scipy.stats as stats


order = 5


fileList = glob.glob('../Data/SystemCharacterization*.npz')

curves = numpy.array([])

for i, f in enumerate(fileList):
    m = numpy.load(f, allow_pickle = True)

    metadata = m['Metadata'][()]

    t = numpy.linspace(0, metadata['Duration'], m['T'].size)
    T_ = m['T']
    P_ = m['P']
    
    steps = numpy.where(numpy.diff(P_))[0]
    steps = numpy.append(steps, t.size - 1)

    p = P_[steps - 1]

    curve = numpy.array([])
    
    for j in range(steps.size):
        slice = numpy.logical_and(t < t[steps[j]], t > t[steps[j]] - 3. * 60.)
        curve = numpy.append(curve, numpy.mean(T_[slice]))

    if curve[-1] < curve[0]:
        curve = numpy.flip(curve)
        p = numpy.flip(p)
    
    if curves.size == 0:
        curves = curve - curve[5]
    else:
        curves = numpy.column_stack((curves, curve - curve[5]))


mean = curves.mean(axis = 1)

polynomial = numpy.polyfit(p, mean, order)
f = numpy.poly1d(polynomial)

slope = (mean[5] - mean[0])

polynomialReverse = numpy.polyfit(mean, mean / slope, order)
reverse = numpy.poly1d(polynomialReverse)

polynomialFix = numpy.polyfit(mean / slope, p, order)
fix = numpy.poly1d(polynomialFix)

numpy.save('../Data/PolynomialReverse.npy', polynomialReverse)
numpy.save('../Data/PolynomialFix.npy', polynomialFix)

x = numpy.linspace(-1, 1, 200)
y = numpy.linspace(-20, 30, 200)

pyplot.scatter(p, mean, color = 'C1')

pyplot.plot(reverse(y), y)
pyplot.plot(x, f(fix(x)), 'k')

pyplot.show()

