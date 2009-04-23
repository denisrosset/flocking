
import sys
sys.path.append('../..')
import flocking, time
from flocking import measure
import flocking.papers
from flocking.sim import *
from flocking.calc import *
import copy as copy_
from scipy import *
import pylab

seeds = range(1000, 1100)

def create(seed, eta, ordered = False, metric = True):
    N = 1000
    L = 15.8
    v = 0.03
    dt = 1
    flock_initializer = ConstantVelocityMagnitudeRandomFlockInitializer(v)
    flockseed = FlockSeed(N, L, seed, flock_initializer)
    if metric:
        R = 1
        ns = MetricDistanceNeighborSelector(R)
    else:
        k = 60
        ns = TopologicalDistanceNeighborSelector(k)
    alg = OriginalVicsekAlgorithm()
    na = ScalarNoiseAdder(eta)
    vup = OriginalVicsekVelocityUpdater(na, v)
    fav = OriginalVicsekAverageForceEvaluator()
    flockstep = FlockStep(dt, ns, vup, alg, [fav])
    if ordered:
        copyflockstep = copy_.deepcopy(flockstep)
        copyflockstep.velocity_updater.noise_adder.eta = 0
        flockseed.flock_initializer = EvolutionFlockInitializer(
            flock_initializer, copyflockstep, 1000)
    steps = 2000
    samplers = {'phi': measure.PeriodicSampler(measure.Phi(), 1)}
    return SimSeed(flockseed, flockstep, steps, samplers)

sim_list = [create(seed, eta, ordered = ordered, metric = metric)
            for seed in seeds
            for ordered in [True, False]
            for metric in [True, False]
            for seed in range(1000, 1100)
            for eta in arange(0, 1, 0.1)]

print len(sim_list)
folder = flocking.sim.S3Folder('07_relaxation_time_with_topo')
batch = flocking.sim.Batch.create_from_seeds(sim_list, folder)
