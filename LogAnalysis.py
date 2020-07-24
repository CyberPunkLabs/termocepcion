import os
import glob
import time
import numpy
import copy
import matplotlib.pyplot as pyplot
import scipy.stats as stats


fileList = glob.glob('../Data/Characterization*.npz')

legend = [] #['Setpoint']

for i, f in enumerate(fileList):
    m = numpy.load(f, allow_pickle = True)

    metadata = m['Metadata'][()]

    sp = m['SP'][: ,0]
    t = numpy.linspace(0, metadata['Duration'], m['T'][:, 0].size)
    T_ = m['T'][:, 0]
    
    description = 'Kp: {:.4g}, Ki: {:.4g}, Kd: {:.4g}'.format(metadata['Kp'], metadata['Ki'], metadata['Kd'])

    #if i == 0:
    #    pyplot.plot(t, sp, 'k')
    #    legend.append('Setpoint')
    
    print('{:d}, {}: {:.3f}'.format(i, description, numpy.abs(T_ - sp).sum()))

    if i in [20,23,22]:
        pyplot.plot(t, T_ - sp)
        legend.append(description)

pyplot.legend(legend, frameon = False)
pyplot.show()
