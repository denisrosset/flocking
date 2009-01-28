import sys
sys.path.append('../..')
import flocking, time
import flocking.measure
import flocking.papers
from flocking.sim import *
from flocking.calc import *
from scipy import *
import pylab

l = [(40, 3.1), (100, 5), (400, 10), (4000, 31.6), (10000, 50)]
steps = 1000
seed = 1000
samplers = {'flock': (flocking.measure.Flock(), 200),
            'phi': (flocking.measure.Phi(), 10)}
sim_list = [flocking.papers.vicsek1995ntp.create(N,
                                                 L,
                                                 angle_eta,
                                                 seed,
                                                 steps,
                                                 samplers)
            for (N, L) in l
            for angle_eta in arange(0, 5, 0.5)]
folder = flocking.sim.S3Folder('vicsek1995ntp_fig2a')
batch = flocking.sim.Batch.create_from_seeds(sim_list, folder)
