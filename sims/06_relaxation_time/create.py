
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

l = [(40, 3.1), (100, 5), (400, 10), (1000, 15.8)]
steps = int(2000)
seeds = range(1000, 1100)
samplers = {'phi': measure.PeriodicSampler(measure.Phi(), 1)}

sim_list = [flocking.papers.vicsek1995ntp.create(N = N,
                                                 L = L,
                                                 eta = eta,
                                                 seed = seed,
                                                 steps = steps,
                                                 samplers = samplers)
            for (N, L) in l
            for seed in seeds
            for eta in arange(0, 1, 0.1)]
def ordered_create(eta, seed = 1000, N = None, L = None, rho = None, steps = 0, samplers = {}):
    sim = flocking.papers.vicsek1995ntp.create(eta, seed, N, L, rho, steps, samplers)
    copyflockstep = copy_.deepcopy(sim.flockstep)
    copyflockstep.velocity_updater.noise_adder.eta = 0
    sim.flockseed.flock_initializer = EvolutionFlockInitializer(
        sim.flockseed.flock_initializer, copyflockstep, 1000)
    return SimSeed(sim.flockseed, sim.flockstep, steps, samplers)

sim_list += [ordered_create(N = N,
                            L = L,
                            eta = eta,
                            seed = seed,
                            steps = steps,
                            samplers = samplers)
             for (N, L) in l
             for seed in seeds
             for eta in arange(0, 1, 0.1)]

print len(sim_list)
folder = flocking.sim.S3Folder('06_relaxation_time')
batch = flocking.sim.Batch.create_from_seeds(sim_list, folder)
