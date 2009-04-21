from __future__ import with_statement
from __future__ import division
from scipy import *
from . import utility
class ForceEvaluator(utility.ParametricObject):
    def start(self, flock, i, temp):
        '''Start the force evaluation acting on bird i, using
        vector temp as temporary storage'''
        pass
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        '''Update the force evaluation acting on bird i, with
        j as neighbor.

        ForceEvaluator.update will be called for every j neighbor
        of bird i.

        r is the vector between i and j.
        Nn is the index of the current neighbor.
        normr, normrsq are the norm and squared norm of r.
        '''
        pass
    def end(self, flock, i, temp, Nn):
        '''End the force evaluation on bird i, and update its force.'''
        pass

class DummyForceEvaluator(ForceEvaluator):
    def __init__(self):
        ForceEvaluator.__init__(self)
        self.parameters = []
    def start(self, flock, i, temp):
        pass
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        pass
    def end(self, flock, i, temp, Nn):
        pass

class OriginalVicsekAverageForceEvaluator(ForceEvaluator):
    def __init__(self):
        ForceEvaluator.__init__(self)
        self.parameters = []
    def start(self, flock, i, temp):
        temp[0] = 0
        temp[1] = 0
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        temp += flock.v[j]
    def end(self, flock, i, temp, Nn):
        flock.f[i] = (temp + flock.v[j]) / (Nn + 1)

class VicsekAverageForceEvaluator(ForceEvaluator):
    def __init__(self, beta):
        ForceEvaluator.__init__(self)
        self.parameters = ['beta']
        self.beta = beta
    def start(self, flock, i, temp):
        temp[0] = 0
        temp[1] = 0
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        temp += flock.v[j]
    def end(self, flock, i, temp, Nn):
        veff = (temp + flock.v[i]) / (Nn + 1)
        flock.f[i] += (veff - flock.v[i]) * self.beta

class NeighborAverageForceEvaluator(ForceEvaluator):
    def __init__(self, beta):
        ForceEvaluator.__init__(self)
        self.parameters = ['beta']
        self.beta = beta
    def start(self, flock, i, temp):
        temp[0] = 0
        temp[1] = 0
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        temp += flock.v[j] - flock.v[i]
    def end(self, flock, i, temp, Nn):
        flock.f[i] += self.beta * temp

class CruisingRegulatorForceEvaluator(ForceEvaluator):
    def __init__(self, gamma, v):
        ForceEvaluator.__init__(self)
        self.parameters = ['gamma', 'v']
        self.gamma = gamma
        self.v = v
    def start(self, flock, i, temp):
        pass
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        pass
    def end(self, flock, i, temp, Nn):
        vnorm = sqrt(flock.v[i][0] * flock.v[i][0] +
                     flock.v[i][1] * flock.v[i][1])
        factor = self.gamma * (self.v - vnorm) / vnorm
        flock.f[i] += flock.v[i] * factor

class LennardJonesInteractionForceEvaluator(ForceEvaluator):
    def __init__(self, epsilon, sigma, offset):
        ForceEvaluator.__init__(self)
        self.parameters = ['epsilon', 'sigma', 'offset']
        self.epsilon = epsilon
        self.sigma = sigma
        self.offset = offset
    def start(self, flock, i, temp):
        temp[0] = 0
        temp[1] = 0
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        interaction_force = (4 * self.epsilon *
                             ((self.sigma/normr)**12 - (self.sigma/normr)**6) +
                             self.offset)
        temp += interaction_force * r / normr
    def end(self, flock, i, temp, Nn):
        flock.f[i] += temp

class PiecewiseLinearForceEvaluator(ForceEvaluator):
    def __init__(self, Frep, Fattr, r0, r1):
        ForceEvaluator.__init__(self)
        self.parameters = ['Frep', 'Fattr', 'r0', 'r1']
        self.Frep = Frep
        self.Fattr = Fattr
        self.r0 = r0
        self.r1 = r1
    def start(self, flock, i, temp):
        temp[0] = 0
        temp[1] = 1
    def update(self, flock, i, j, r, normr, normrsq, temp, Nn):
        where = max(self.r0, normr)
        where = min(where, self.r1)
        interaction_force = (self.Frep +
                             (self.Fattr - self.Frep) * (where - self.r0))
        temp += interaction_force * r / normr
    def end(self, flock, i, temp, Nn):
        flock.f[i] += temp
