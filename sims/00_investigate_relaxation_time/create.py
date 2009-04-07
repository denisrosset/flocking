import sys
sys.path.append('../..')
import flocking, time
from flocking import measure
import flocking.papers
from flocking.sim import *
from flocking.calc import *
from scipy import *
import pylab

l = [(40, 3.1), (100, 5), (400, 10), (4000, 31.6), (10000, 50)]
steps = int(1e4)
seed = 1000
samplers = {'flock': measure.PeriodicSampler(measure.Flock(), 100),
            'phi': measure.PeriodicSampler(measure.Phi(), 10)}
sim_list = [flocking.papers.vicsek1995ntp.create(N = N,
                                                 L = L,
                                                 eta = eta,
                                                 seed = seed,
                                                 steps = steps,
                                                 samplers = samplers)
            for (N, L) in l
            for eta in arange(0, 1, 0.02)]
folder = flocking.sim.S3Folder('01_test_parallel')
batch = flocking.sim.Batch.create_from_seeds(sim_list, folder)
