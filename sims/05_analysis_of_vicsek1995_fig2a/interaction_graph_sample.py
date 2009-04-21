import sys
sys.path.append('../..')
import pylab
import flocking
import cPickle as pickle
import glob
from scipy import *
import flocking.sim
import flocking.analysis
from scipy import *
import scipy.optimize
fig_width_pt = 380.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (math.sqrt(5)-1.0)/2.0         # Aesthetic ratio
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width*golden_mean      # height in inches
fig_size =  [fig_width,fig_height]
params = {'backend': 'ps',
          'axes.labelsize': 10,
          'text.fontsize': 10,
          'legend.fontsize': 10,
          'xtick.labelsize': 8,
          'ytick.labelsize': 8,
          'text.usetex': True,
          'figure.figsize': fig_size}
pylab.rcParams.update(params)
folder = flocking.sim.S3Folder('01_reproduce_vicsek1995_fig2a')
batch = flocking.sim.Batch.load_from_folder(folder)

keys = [(seed.flockstep.velocity_updater.noise_adder.eta, seed.hash_key)
        for seed in batch.seeds.values() if seed.flockseed.N == 1000
        and min(abs(seed.flockstep.velocity_updater.noise_adder.eta - 
                    array([0.02, 0.62, 0.98])))<0.0001]
keys = [key[1] for key in sorted(keys)]

for key in keys:
    sim = batch.load(key)
    eta100 = int(sim.flockstep.velocity_updater.noise_adder.eta*100)
    d = flocking.analysis.InteractionTime()(sim.samples['compact_adjacency'], 
                                            start_at = 10000, average_on = 100, max_delta = 500)
    (x, y) = flocking.analysis.SplitPlotter.get_x_y_from_dict(d)
    fitfunc = lambda p, x: p[0] + p[1] * exp(-x/p[2])
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    p0 = [0.0, y[0], 100]
    p, success = scipy.optimize.leastsq(errfunc, p0[:], args = (x, y))
    colors = {2:'r', 62:'g', 98:'b'}
    symbol = {2:'x', 62:'o', 98:'+'}
    pylab.plot(x, y, symbol[eta100]+colors[eta100], label = 'Noise $\\eta = %.2f$' % (eta100/100.0))
    pylab.plot(x, fitfunc(p, x), '-'+colors[eta100])
pylab.legend(loc = 'best')
pylab.xlabel('Time $\\Delta t$')
pylab.xlim(0, 50)
pylab.ylabel('Average of correlation $\\frac{1}{T} \\sum_{t} I(t, \\Delta t)$')
pylab.savefig('graph/interaction_graph_sample.eps')

