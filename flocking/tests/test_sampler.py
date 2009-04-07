from flocking.measure import PeriodicStatisticsSampler
import unittest
import scipy, scipy.stats

class ReturnFlock:
    def __call__(self, flock, flockstep, step, fast = True):
        return flock
    
class TestPeriodicStatisticsSampler(unittest.TestCase):
    tags = ['flockingtest']
    def validate_distribution(self, dist, N, places = 3):
        samples = dist(size = N)
        periodic = PeriodicStatisticsSampler(ReturnFlock(), 1, 1)
        res = None
        for i in range(0, N):
            res = periodic(samples[i], None, i)
        self.assertAlmostEquals(res[1], scipy.stats.mean(samples), places)
        self.assertAlmostEquals(res[2], scipy.stats.var(samples), places)
        self.assertAlmostEquals(res[3], scipy.stats.skew(samples), places)
        self.assertAlmostEquals(res[4], scipy.stats.kurtosis(samples), places)
        
    def test(self):
        self.validate_distribution(scipy.random.standard_normal,
                                   10000)
        self.validate_distribution(scipy.random.laplace,
                                   10000)
