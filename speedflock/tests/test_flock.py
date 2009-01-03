from __future__ import with_statement
from __future__ import division
import unittest
from copy import *
from pickle import *

from scipy import *

from speedflock import *

class TestFlock(unittest.TestCase):
    tags = ['speedflock']
    seed = 12345
    N = 40
    L = 10.
    v = 1.
    flockInitializer = ConstantVelocityMagnitudeRandomFlockInitializer(v)
    def setUp(self):
        self.flock = Flock(self.N, self.L, self.seed, self.flockInitializer)

    def test_constant_velocity_magnitude_random_flock_initializer(self):
        for i in range(0, self.N):
            self.assertAlmostEquals(linalg.norm(self.flock.v[i, :]), self.v)

    def assertFlockSame(self, f1, f2, places = 7):
        diff = linalg.norm(f1.x - f2.x) + linalg.norm(f1.v - f2.v)
        self.assertAlmostEquals(diff, 0, places)

    def test_seed(self):
        flock2 = Flock(self.N, self.L, self.seed, self.flockInitializer)
        self.assertFlockSame(self.flock, flock2)

    def test_copy(self):
        flock2 = deepcopy(self.flock)
        self.assertFlockSame(self.flock, flock2)

    def test_periodsub_and_distance(self):
        N = 2
        L = 1.
        flock = Flock(N, L, self.seed, self.flockInitializer)
        flock.x = array([[0.1, 0.1],
                        [0.9, 0.9]])
        r = flock.period_sub(flock.x[0,:], flock.x[1,:])
        diff = r - array([0.2, 0.2])
        self.assertAlmostEquals(linalg.norm(diff), 0)
        self.assertAlmostEquals(flock.distance_between_birds(0, 1), 0.2 * sqrt(2))
        
    def test_loop_position(self):
        diff = self.flock.loop_position(array([13, 15])) - array([3, 5])
        self.assertAlmostEquals(linalg.norm(diff), 0)
        diff = self.flock.loop_position(array([-7, -5])) - array([3, 5])
        self.assertAlmostEquals(linalg.norm(diff), 0)

    def test_geometry(self):
        for i in range(0, 100):
            v1 = random.rand(2)
            v2 = random.rand(2)
            d = self.flock.period_sub(v1, v2)
            self.assertTrue(abs(d[0]) < self.L/2)
            self.assertTrue(abs(d[1]) < self.L/2)
            v1p = self.flock.loop_position(d + v2)
            diff = v1 - v1p
            self.assertAlmostEquals(linalg.norm(diff), 0)
        
    def test_phi(self):
        N = 2
        L = 1.
        flock = Flock(N, L, self.seed, self.flockInitializer)
        flock.v = array([[2.0, 0],
                        [2.0, 0]])
        self.assertAlmostEquals(flock.phi(), 1)
        flock.v = array([[2.0, 0],
                        [-2.0, 0]])
        self.assertAlmostEquals(flock.phi(), 0)
