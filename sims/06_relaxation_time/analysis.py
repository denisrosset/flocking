import sys
sys.path.append('../..')

import flocking.sim
import flocking.analysis
import pylab
import random
from scipy import *
import scipy.optimize
import copy as copy_
pylab.hold(False)
folder = flocking.sim.S3Folder('06_relaxation_time')
batch = flocking.sim.Batch.load_from_folder(folder)
def plot_function(sims, keys_for_serie):
    x = array(range(0, 2000))
    y = zeros(2000)
    for i in x:
        y[i] = mean([sim.samples['phi'][i] for sim in sims])
    N = sims[0].flock.N
    eta = keys_for_serie['ScalarNoiseAdder_eta']
    type = 'r' if keys_for_serie.has_key('ConstantVelocityMagnitudeRandomFlockInitializer_v') else 'o'
    color = [
        '#000000',
        '#800000',
        '#008000',
        '#000080',
        '#008080',
        '#800080',
        '#808000',
        '#FF0000',
        '#00FF00',
        '#0000FF'
        ][int(eta*10)]
    if type == 'r':
        pylab.plot(x[::10], y[::10], '.', color = color, label = "Eta = %.2f" % eta)
    else:
        pylab.plot(x[::10], y[::10], '.', color = color)
    fitfunc = lambda p, x: p[0] + p[1] * exp(-x/p[2])
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    p0 = [0.1, y[0], 100]
    p, cov_x, infodict, mesg, ier = scipy.optimize.leastsq(errfunc, p0[:], args = (x, y), full_output=True)
    pylab.plot(x, fitfunc(p, x), '-', color = color)
    print type, N, eta, p[2]
plot_number = 0
def save_function(keys_for_plot):
    pylab.legend(loc = 'upper right')
    pylab.xlabel('Time steps')
    pylab.ylabel('Order parameter phi')
    axis = list(pylab.axis())
    axis[2] = 0
    axis[3] = 1
    pylab.title('')
    pylab.axis(axis)
    pylab.savefig('graph/plot_%d.png' % keys_for_plot['FlockSeed_N'])
    pylab.savefig('graph/plot_%d.pdf' % keys_for_plot['FlockSeed_N'])
    pylab.savefig('graph/plot_%d.eps' % keys_for_plot['FlockSeed_N'])
    pylab.close('all')


plot = flocking.analysis.SplitPlotter(batch,
                                      plot_function = plot_function,
                                      save_function = save_function,
#                                      filter = lambda sim: sim.flockseed.seed == 1000,
                                      p_vars = ['FlockSeed_N', 'FlockSeed_L'],
                                      c_vars = ['FlockSeed_seed'],
                                      s_vars = ['ScalarNoiseAdder_eta', 'ConstantVelocityMagnitudeRandomFlockInitializer_v', 'EvolutionFlockInitializer_steps'])
plot.plot()
