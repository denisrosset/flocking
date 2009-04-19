import sys
sys.path.append('../..')
import pylab
import flocking
import cPickle as pickle
import glob
from scipy import *
for f in glob.glob('sims/*.pickle'):
    a = pickle.load(open(f))
    if a.flock.N == 40:
        import flocking.analysis
        d = flocking.analysis.InteractionTime()(a.samples['compact_adjacency'], average_on = 100, max_delta = 500)
        (x, y) = flocking.analysis.SplitPlotter.get_x_y_from_dict(d)
        fitfunc = lambda p, x: p[0] + p[1] * exp(-x/p[2])
        errfunc = lambda p, x, y: fitfunc(p, x) - y
        p0 = [0.0, y[0], 100]
        p, success = optimize.leastsq(errfunc, p0[:], args = (x, y))
#        pylab.plot(x, y, 'r.')
#        pylab.plot(x, fitfunc(p, x), 'r-')
#        pylab.show()
        print a.flockstep.velocity_updater.noise_adder.eta, p[2]
