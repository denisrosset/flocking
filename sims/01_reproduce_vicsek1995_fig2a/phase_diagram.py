import sys
sys.path.append('../..')

import flocking.sim
import flocking.analysis
import pylab
import random
from scipy import *
pylab.hold(False)
folder = flocking.sim.S3Folder('01_reproduce_vicsek1995_fig2a')
batch = flocking.sim.Batch.load_from_folder(folder)
def plot_function(sims, keys_for_serie):
    x = []
    y = []
    for (xc, yc) in sims:
        x.append(xc)
        y.append(yc)
    pylab.plot(x, y, 'x', label = "N = %d" % keys_for_serie['FlockSeed_N'])

plot_number = 0
def map_function(sim):
    stats = sim.samples['stats']
    x = sim.flockstep.velocity_updater.noise_adder.eta
    y = stats[max(stats.iterkeys())][1]
    return (x, y)
  
def save_function(keys_for_plot):
    print keys_for_plot
    pylab.legend(loc = 'upper right')
    pylab.xlabel('Noise eta')
    pylab.title('Phase diagram')
    pylab.ylabel('\phi order parameter mean')
    axis = list(pylab.axis())
    axis[2] = 0
    axis[3] = 1
    pylab.axis(axis)
    pylab.savefig('phase_diagram.png')
    pylab.savefig('phase_diagram.pdf')
    pylab.close('all')


plot = flocking.analysis.SplitPlotter(batch,
                                      map_function = map_function,
                                      plot_function = plot_function,
                                      save_function = save_function,
                                      c_vars = ['FlockSeed_seed', 'ScalarNoiseAdder_eta', 'FlockSeed_L'],
                                      s_vars = ['FlockSeed_N'])
plot.plot()

