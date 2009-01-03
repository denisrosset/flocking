from __future__ import with_statement
from __future__ import division
import unittest
from copy import *
from pickle import *
import scipy.weave
from scipy import *

from speedflock import *

class TestVicsekUpdaters(unittest.TestCase):
    tags = ['speedflock']
    seed = 1000
    N = 10
    L = 2
    v = 1
    R = 1.5
    eta = 1.5
    dt = 0.01

    def test_compare_fast_slow(self):
        flockstep1 = deepcopy(self.flockstep)
        flockstep1.fast = False
        flockstep1.neighbor_selector.fast = False
        flockstep1.velocity_update.fast = False
        flockstep1.noise_adder.fast = False
        flockstep1.fav_evaluator.fast = False
        flockstep1.fint_evaluator.fast = False
        flockstep1.fvreg_evaluator.fast = False

        flock1 = deepcopy(self.flock)
        steps = 2
        for i in range(0, steps):
            self.flockstep.c_step(flock1, 10)
        for i in range(0, steps):
            self.flockstep1.c_step(self.flock, 10)

        diff = linalg.norm(self.flock.x - flock1.x) + linalg.norm(self.flock.v - flock1.v)
        self.assertAlmostEquals(diff, 0)

        for i in range(0, steps):
            self.flockstep.step(flock1, 10)
        for i in range(0, steps):
            self.flockstep1.step(self.flock, 10)    

        diff = linalg.norm(self.flock.x - flock1.x) + linalg.norm(self.flock.v - flock1.v)
        self.assertAlmostEquals(diff, 0)

    def test_compare_c_code(self):
        flock1 = deepcopy(self.flock)
        steps = 2
        for i in range(0, steps):
            self.flockstep.c_step(flock1, 10)
        for i in range(0, steps):
            self.flockstep.step(self.flock, 10)
        self.flockstep.noise_adder.eta = 0
        for i in range(0, steps):
            self.flockstep.c_step(flock1, 10)
        for i in range(0, steps):
            self.flockstep.step(self.flock, 10)    
        diff = linalg.norm(self.flock.x - flock1.x) + linalg.norm(self.flock.v - flock1.v)
        self.assertAlmostEquals(diff, 0)

    def setUp(self):
        self.ns = MetricDistanceNeighborSelector(self.R)
        self.fav = OriginalVicsekAverageForceEvaluator()
        self.fint = DummyForceEvaluator()
        self.fvreg = DummyForceEvaluator()
        self.vup = OriginalVicsekVelocityUpdater(self.v)
        self.noise = ScalarNoiseAdder(self.eta)
        self.cvm = ConstantVelocityMagnitudeRandomFlockInitializer(self.v)
        self.flockstep = FlockStep(self.dt,
                                   self.ns,
                                   self.vup,
                                   self.noise,
                                   self.fav,
                                   self.fint,
                                   self.fvreg)
        self.flock = Flock(self.N, self.L, self.seed, self.cvm)

    def test_step(self):
        flock = Flock(2, self.L, self.seed, self.cvm)
        flock.x[0,:] = array([0, 0])
        flock.x[1,:] = flock.x[0,:] + random.rand(2)
        flock.v[0,:] = array([1, 0])
        flock.v[1,:] = flock.v[0,:]
        startpos = array(flock.x[0,:])
        orig = array(flock.v[0,:])
        dist = flock.distance_between_birds(0, 1)
        flockstep = FlockStep(self.dt,
                              self.ns,
                              self.vup,
                              DummyNoiseAdder(),
                              self.fav,
                              self.fint,
                              self.fvreg)
        steps = 100
        for i in range(0, steps):
            flockstep.step(flock)
        v0 = flock.v[0,:]
        f0 = flock.f[0,:]
        v0 = v0/linalg.norm(v0)
        f0 = f0/linalg.norm(f0)
        self.assertAlmostEquals(linalg.norm(v0 - f0), 0)
        self.assertAlmostEquals(linalg.norm(flock.period_sub(flock.x[0,:], startpos)), steps * self.v * self.dt)
        self.assertAlmostEquals(linalg.norm(
                flock.v[0,:] - orig
                ), 0)
        self.assertAlmostEquals(linalg.norm(
                flock.v[1,:] - orig
                ), 0)
        self.assertAlmostEquals(flock.distance_between_birds(0, 1), dist)

        
    def test_dummy_force(self):
        d = DummyForceEvaluator()
        self.assertEquals(linalg.norm(d.term(self.flock, 0, 1)), 0)
        self.assertEquals(linalg.norm(d.shape_sum(self.flock, 0, array([1, 2]))), 0)

    def test_dummy_noise(self):
        noise = DummyNoiseAdder()
        self.assertEquals(linalg.norm(
                noise.get_with_noise(self.flock.v[0,:], RandomState()) - self.flock.v[0,:]),
                          0)

    def test_scalar_noise(self):
        r = RandomState()
        for i in range(0, 100):
            v = array([1, 0])
            v1 = self.noise.get_with_noise(v, r)
            alpha = angle(v1[0], v1[1])
            self.assertTrue(alpha <= self.eta/2 and alpha >= -self.eta/2)

    def test_original_vicsek_average(self):
        ovafe = OriginalVicsekAverageForceEvaluator()
        self.assertAlmostEquals(linalg.norm(ovafe.term(self.flock, 0, 1) - self.flock.v[1, :]), 0)
        self.assertAlmostEquals(linalg.norm(ovafe.shape_sum(self.flock, 0, array([1, 2])) - array([1, 2])), 0)

    def test_original_vicsek_velocity_updater(self):
        self.flock.v[0,:] = array([1, 0])
        self.flock.f[0,:] = array([2, 0])
        self.assertAlmostEquals(linalg.norm(
                self.vup.get_new_velocity(self. flock, 0, self.dt) - array([1, 0])
                ), 0)
        
    def test_metric_distance_neighbor_selector(self):
        flock = Flock(3, 10, 1000, self.cvm)
        flock.x[0,:] = array([1,1])
        flock.x[1,:] = array([2, 2])
        flock.x[2,:] = array([3, 3])
        self.assertEquals(self.ns.get_list_of_neighbors(flock, 0), [1])
        self.assertEquals(self.ns.get_list_of_neighbors(flock, 1), [0, 2])
        self.assertEquals(self.ns.get_list_of_neighbors(flock, 2), [1])
