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
