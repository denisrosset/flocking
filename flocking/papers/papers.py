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
import copy

class vicsek1995ntp(object):
    @classmethod
    def create(cls, eta, seed = 1000, N = None, L = None, rho = None, steps = 0, samplers = {}):
        if N is None:
            N = L * L * rho
        if L is None:
            L = math.sqrt(N/rho)
        if rho is None:
            rho = N/L/L
        v = 0.03
        dt = 1
        R = 1
        flock_initializer = ConstantVelocityMagnitudeRandomFlockInitializer(v)
        flockseed = FlockSeed(N, L, seed, flock_initializer)
        ns = MetricDistanceNeighborSelector(R)
        alg = OriginalVicsekAlgorithm()
        na = ScalarNoiseAdder(eta)
        vup = OriginalVicsekVelocityUpdater(na, v)
        fav = OriginalVicsekAverageForceEvaluator()
        flockstep = FlockStep(dt, ns, vup, alg, [fav])
        return SimSeed(flockseed, flockstep, steps, samplers)
