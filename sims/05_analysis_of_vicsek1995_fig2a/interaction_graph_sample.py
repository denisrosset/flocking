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

keys = [seed.hash_key for seed in batch.seeds.values() if seed.flockseed.N == 1000
        and min(abs(seed.flockstep.velocity_updater.noise_adder.eta - array([0.02, 0.62, 0.98])))<0.0001]


for key in keys:
    sim = batch.load(key)
    try:
        d = flocking.analysis.InteractionTime()(sim.samples['compact_adjacency'], start_at = 10000, average_on = 100, max_delta = 500)
        (x, y) = flocking.analysis.SplitPlotter.get_x_y_from_dict(d)
        fitfunc = lambda p, x: p[0] + p[1] * exp(-x/p[2])
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [0.0, y[0], 100]
        p, success = scipy.optimize.leastsq(errfunc, p0[:], args = (x, y))
        pylab.plot(x, y, '.')
        pylab.plot(x, fitfunc(p, x), '-')
    except:
        pass
    batch.release_memory()
pylab.savefig('graph/interaction_graph_sample.eps')

