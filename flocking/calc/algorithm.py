from __future__ import with_statement
from __future__ import division
from scipy import *
from . import utility

class Algorithm(utility.ParametricObject):
    def update(self, flock, velocity_updater, dt):
        """ Update velocities of birds in flock flock, using
        given velocity_updater. """
        pass

class OriginalVicsekAlgorithm(Algorithm):
    def __init__(self):
        self.parameters = []
        Algorithm.__init__(self)
    def update(self, flock, velocity_updater, dt):
        for i in range(0, flock.N):
            flock.x[i] = flock.get_position_in_original_domain(
                flock.x[i] + flock.v[i] * dt)
            velocity_updater.update(flock, i, dt)

class StandardVicsekAlgorithm(Algorithm):
    def __init__(self):
        self.parameters = []
        Algorithm.__init__(self)
    def update(self, flock, velocity_updater, dt):
        for i in range(0, flock.N):
            velocity_updater.update(flock, i, dt)
            flock.x[i] = flock.get_position_in_original_domain(
                flock.x[i] + flock.v[i] * dt)
