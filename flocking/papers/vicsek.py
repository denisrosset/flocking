from __future__ import division

from ..calc import Flock, FlockSeed, FlockStep, ConstantVelocityMagnitudeRandomFlockInitializer
from ..calc import MetricDistanceNeighborSelector, BlockMetricDistanceNeighborSelector
from ..calc import OriginalVicsekAverageForceEvaluator, OriginalVicsekAlgorithm
from ..calc import ScalarNoiseAdder, OriginalVicsekVelocityUpdater
from ..calc import FlockSeed
from ..calc import FlockStep
from ..calc import ConstantVelocityMagnitudeRandomFlockInitializer
from ..sim import SimSeed
import math

class vicsek1995ntp(object):
    @classmethod
    def create(cls, N, L, angle_eta, seed, n_steps = 0, samplers = {}):
        v = 0.03
        dt = 1
        R = 1
        flock_initializer = ConstantVelocityMagnitudeRandomFlockInitializer(v)
        flockseed = FlockSeed(N, L, seed, flock_initializer)
        ns = BlockMetricDistanceNeighborSelector(R)
        alg = OriginalVicsekAlgorithm()
        na = ScalarNoiseAdder(angle_eta/(2*math.pi))
        vup = OriginalVicsekVelocityUpdater(na, v)
        fav = OriginalVicsekAverageForceEvaluator()
        flockstep = FlockStep(dt, ns, vup, alg, [fav])
        return SimSeed(flockseed, flockstep, n_steps, samplers)
    @classmethod
    def create_fig1a(cls, seed = 1000):
        return cls.create(N = 300, L = 7.0, seed = seed, angle_eta = 2.0, n_steps = 0)
