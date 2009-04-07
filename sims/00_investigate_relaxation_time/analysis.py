import sys
sys.path.append('../..')

import flocking.sim
import flocking.analysis
import pylab
import random
from scipy import *
pylab.hold(False)
folder = flocking.sim.S3Folder('00_investigate_relaxation_time')
batch = flocking.sim.Batch.load_from_folder(folder)
def plot_function(sims, keys_for_serie):
    list_of_samples = [sim.samples['phi'] for sim in sims]
    dmean = dict([
            (t, mean([sample[t] for sample in list_of_samples]))
            for t in list_of_samples[0].keys()])
    dstddev = dict([
            (t, sqrt(var([sample[t] for sample in list_of_samples])))
            for t in list_of_samples[0].keys()])
    (x, ymean) = flocking.analysis.SplitPlotter.get_x_y_from_dict(dmean)
    (x, ystddev) = flocking.analysis.SplitPlotter.get_x_y_from_dict(dstddev)
    def reversed_a(a):
        return a[range(len(a) - 1, -1, -1)]
    color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
    dark_color = (color[0]/2, color[1]/2, color[2]/2, 0.2)
    pylab.fill(concatenate((x, reversed_a(x))), concatenate((ymean + ystddev, reversed_a(ymean - ystddev))), facecolor = dark_color, alpha = 0.2)
    pylab.plot(x, ymean, color = color, label = "Eta = %.2f" % keys_for_serie['ScalarNoiseAdder_eta'])

plot_number = 0
def save_function(keys_for_plot):
    global plot_number
    pylab.legend(loc = 'upper center')
    pylab.xlabel('Steps')
    pylab.ylabel('\phi order parameter')
    axis = list(pylab.axis())
    axis[2] = 0
    axis[3] = 1
    pylab.axis(axis)
    pylab.savefig('plot%d.png' % plot_number)
    pylab.close('all')
    plot_number += 1
plot = flocking.analysis.SplitPlotter(batch,
                                      plot_function = plot_function,
                                      save_function = save_function,
                                      s_vars = ['ScalarNoiseAdder_eta'])
plot.plot()
