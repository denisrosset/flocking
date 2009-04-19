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
folder = flocking.sim.S3Folder('01_reproduce_vicsek1995_fig2a')
batch = flocking.sim.Batch.load_from_folder(folder)

stride = int(sys.argv[1])
number_of_strides = int(sys.argv[2])

keys = sorted(batch.seeds.keys())
my_keys = [keys[i] for i in range(0, len(keys))
           if (i % number_of_strides) == stride]

print 'N', 'eta', 'rho', 'kappa'
for key in my_keys:
    sim = batch.load(key)
#    if sim.flock.N != 40:
#        continue
    try:
        d = flocking.analysis.InteractionTime()(sim.samples['compact_adjacency'], start_at = 10000, average_on = 100, max_delta = 500)
        (x, y) = flocking.analysis.SplitPlotter.get_x_y_from_dict(d)
        fitfunc = lambda p, x: p[0] + p[1] * exp(-x/p[2])
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [0.0, y[0], 100]
        p, success = scipy.optimize.leastsq(errfunc, p0[:], args = (x, y))
        kappa = p[2]
        N = sim.flock.N
        eta = sim.flockstep.velocity_updater.noise_adder.eta
        rho = flocking.analysis.LocalDensityOfAgents()(sim.samples['compact_adjacency'], start_at = 10000, average_on = 5000)/float(N)
        print N, eta, rho, kappa
    except:
        pass
    batch.release_memory()
