from __future__ import division

from ..calc import Flock, FlockSeed, FlockStep, ConstantVelocityMagnitudeRandomFlockInitializer
from ..calc import MetricDistanceNeighborSelector, VicsekNeighborSelector
from ..calc import DummyInteractionForceEvaluator
from ..calc import OriginalVicsekAverageForceEvaluator, DummyVelocityForceEvaluator
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
        ns = MetricDistanceNeighborSelector(R)
        vup = OriginalVicsekVelocityUpdater(v)
        na = ScalarNoiseAdder(angle_eta/(2*math.pi))
        fav = OriginalVicsekAverageForceEvaluator()
        fint = DummyInteractionForceEvaluator()
        fvreg = DummyVelocityForceEvaluator()
        flockstep = FlockStep(dt, ns, vup, na, fav, fint, fvreg)
        return SimSeed(flockseed, flockstep, n_steps, samplers)
    @classmethod
    def create_fig1a(cls, seed = 1000):
        return cls.create(N = 300, L = 7.0, seed = seed, angle_eta = 2.0, n_steps = 0)
