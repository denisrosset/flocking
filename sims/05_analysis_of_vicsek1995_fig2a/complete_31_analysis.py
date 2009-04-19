import sys
sys.path.append('../..')

import flocking.sim
import flocking.analysis
import pylab
import random
from scipy import *
import scipy.stats
pylab.hold(False)
folder = flocking.sim.S3Folder('01_reproduce_vicsek1995_fig2a')
batch = flocking.sim.Batch.load_from_folder(folder)

stride = int(sys.argv[1])
number_of_strides = int(sys.argv[2])

keys = sorted(batch.seeds.keys())
my_keys = [keys[i] for i in range(0, len(keys))
           if (i % number_of_strides) == stride]

print 'N', 'eta', 'mean', 'fluc', 'binder'
for key in my_keys:
    sim = batch.load(key)
    phi_dict = sim.samples['phi']
    phi = array([phi_dict[t] for t in phi_dict.keys() if t >= 10000])
    eta = sim.flockstep.velocity_updater.noise_adder.eta
    mean_ = mean(phi)
    fluc = sim.flock.N * var(phi)
    binder = -scipy.stats.kurtosis(phi)/3.0
    print sim.flock.N, eta, mean_, fluc, binder
    batch.release_memory()

