from __future__ import with_statement
from __future__ import division
from .. import utility
from scipy import *

d = 2

##
# Initializes the flock with random bird positions, and random velocities
# with specified norm
class ConstantVelocityMagnitudeRandomFlockInitializer(object):
    def __init__(self, v):
        self.v = v

    ##
    # Initializes a flock
    # @f The flock to be initiliazed
    def initFlock(self, f):
        with f.random_state:
            f.x = random.random([f.N, d]) * f.L
            angles = random.random(f.N) * pi
            f.v = array((cos(angles), sin(angles))).transpose() * self.v

class Flock(object):
    def __init__(self, N, L, seed, flockInitializer):
        self.N = N
        self.L = L
        self.seed = seed
        self.random_state = utility.RandomState(seed)
        self.x = zeros([N, d])
        self.v = zeros([N, d])
        self.f = zeros([N, d])
        flockInitializer.initFlock(self)

    ##
    # @return the normalized position of x in the torus plane
    def loop_position(self, x):
        def loop_coord(a):
            a = a + self.L if a < 0 else a
            a = a - self.L if a > self.L else a
            return a
        return array([loop_coord(x[0]), loop_coord(x[1])])

    ##
    # given two vectors a and b, returns delta such that
    # delta = self.period_sub(a, b)
    # b + delta = a in the torus plane
    # and delta.norm() is minimized
    def period_sub(self, a, b):
        def compsub(a, b):
            d = a - b
            d = d + self.L if d < -self.L/2 else d
            d = d - self.L if d > self.L/2 else d
            return d
        return array([compsub(a[0], b[0]), compsub(a[1], b[1])])

    ##
    # gives the distance between the birds i and j
    # @return the distance
    def distance_between_birds(self, i, j):
        return linalg.norm(self.period_sub(self.x[i,:], self.x[j,:]))

    def phi(self):
        sum_v = linalg.norm(self.v.mean(axis=0))
        individual_norms = sqrt((self.v * self.v).sum(axis = 1))
        return sum_v / mean(individual_norms)
