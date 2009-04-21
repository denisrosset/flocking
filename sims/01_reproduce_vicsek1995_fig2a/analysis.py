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
    sim = sims[0]
    (x, y) = flocking.analysis.SplitPlotter.get_x_y_from_dict(
        sim.samples['phi'])
    pylab.plot(x, y, label = "Eta = %.2f" % keys_for_serie['ScalarNoiseAdder_eta'])

plot_number = 0
def save_function(keys_for_plot):
    pylab.legend(loc = 'upper right')
    pylab.xlabel('Steps')
    pylab.title('Order parameter evolution for N = %d' % keys_for_plot['FlockSeed_N'])
    pylab.ylabel('\phi order parameter')
    axis = list(pylab.axis())
    axis[2] = 0
    axis[3] = 1
    pylab.axis(axis)
    pylab.savefig('plot_%d.png' % keys_for_plot['FlockSeed_N'])
    pylab.savefig('plot_%d.pdf' % keys_for_plot['FlockSeed_N'])
    pylab.close('all')


plot = flocking.analysis.SplitPlotter(batch,
                                      filter = lambda sim:
                                          abs(int(sim.flockstep.velocity_updater.noise_adder.eta*10)/10.0 -
                                              sim.flockstep.velocity_updater.noise_adder.eta) < 0.0001,
                                      plot_function = plot_function,
                                      save_function = save_function,
                                      s_vars = ['ScalarNoiseAdder_eta'])
plot.plot()
