from __future__ import with_statement
from __future__ import division
from scipy import *

from . import utility

class NoiseAdder(utility.ParametricObject):
    def update(self, v, r):
        """
        Return the velocity with added noise

        v is the velocity without noise
        r is the random number to be used
        """
        pass

class DummyNoiseAdder(NoiseAdder):
    def __init__(self):
        self.parameters = []
        NoiseAdder.__init__(self)
    def get_with_noise(self, v, r):
        pass

class ScalarNoiseAdder(NoiseAdder):
    def __init__(self, eta):
        self.eta = eta
        self.parameters = ['eta']
        NoiseAdder.__init__(self)
    def update(self, v, r):
        vx = v[0]
        vy = v[1]
        angle = (r - 0.5) * pi * 2 * self.eta
        cs = cos(angle)
        sn = sin(angle)
        return array([vx * cs - vy * sn,
                      vx * sn + vy * cs])

class VectorialNoiseAdder(NoiseAdder):
    def __init__(self, eta, v):
        self.eta = eta
        self.v = v
        self.parameters = ['eta', 'v']
        NoiseAdder.__init__(self)
    def update(self, v, r):
        angle = (r - 0.5) * pi * 2
        v[0] = (1 - self.eta) * v[0] + self.eta * self.v * cos(angle)
        v[1] = (1 - self.eta) * v[1] + self.eta * self.v * sin(angle)
