import sys
sys.path.append('../..')
import scipy
import scipy.stats
import flocking.measure
phi = []
T = 10000
phi2 = 0
phi4 = 0
class DummyMeasure():
    def __call__(self, flock, flockstep, fast = True):
        return flock

sampler = flocking.measure.PeriodicStatisticsSampler(DummyMeasure(), 1, 1, 0)

for i in range(0, T):
    N = 1000
    r=scipy.random.rand(N)*2*scipy.pi
    p = scipy.sqrt(scipy.sum(scipy.sin(r))**2+scipy.sum(scipy.cos(r))**2)/N
    phi.append(p)
    phi2 += p**2/T
    phi4 += p**4/T
    res = sampler(p, None, 0)
    
print scipy.stats.kurtosis(phi, bias = True), res, (1.0-phi4/(3*phi2**2))
