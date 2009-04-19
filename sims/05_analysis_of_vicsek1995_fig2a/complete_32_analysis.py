import sys
sys.path.append('../..')
import pylab
import flocking
import cPickle as pickle
import glob
from scipy import *
import flocking.sim
import flocking.analysis
import flocking.measure
import scipy.stats
from scipy import *
import scipy.optimize
import numpy
folder = flocking.sim.S3Folder('01_reproduce_vicsek1995_fig2a')
batch = flocking.sim.Batch.load_from_folder(folder)

stride = int(sys.argv[1])
number_of_strides = int(sys.argv[2])

keys = sorted(batch.seeds.keys())
my_keys = [keys[i] for i in range(0, len(keys))
           if (i % number_of_strides) == stride]

print 'N', 'eta', '<d>', 'var(d)'
for key in my_keys:
    sim = batch.load(key)
#    if sim.flock.N != 40:
#        continue
    d = []
    flocks = [flock for (time, flock) in sim.samples['flock'].items() if time >= 10000]
    for flock in flocks:
        d.append(flocking.measure.MeanNearestNeighborDistance()(flock, sim.flockstep))
        
    N = sim.flock.N
    eta = sim.flockstep.velocity_updater.noise_adder.eta
    print N, eta, numpy.mean(d), numpy.sqrt(numpy.var(d)/len(d))
                
    batch.release_memory()
