import sys
sys.path.append('../..')
import flocking, time
from flocking import measure
import flocking.papers
from flocking.sim import *
from flocking.calc import *
from scipy import *
import pylab
import cPickle as pickle
samplers = {'flock': measure.PeriodicSampler(measure.Flock(), 100 * 1000),
            'phi': measure.PeriodicSampler(measure.Phi(), 100),
            'stats': measure.PeriodicStatisticsSampler(measure.Phi(), 10, 10000, 10000),
            'mean_nearest': measure.PeriodicStatisticsSampler(measure.MeanNearestNeighborDistance(), 10, 10000, 10000)}
etas = arange(0, 1, 0.02)
eta = sorted(etas)[2]
sim = flocking.papers.vicsek1995ntp.create(N = 40, L = 3.1, eta = eta, seed = 1000, steps = int(1e6), samplers = samplers).create()
while not sim.finished():
    print sim.step
    if len(sim.samples['stats']) > 0:
        k = max(sim.samples['stats'].keys())
        print sim.samples['stats'][k]
    sim.advance_simulation(stop_after_steps = 1000)
pickle.dump(sim, open('test_sim', 'wb'), pickle.HIGHEST_PROTOCOL)
