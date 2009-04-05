from __future__ import with_statement
from __future__ import division
from . import utility
from scipy import *

d = 2

##
# Initializes the flock with random bird positions, and random velocities
# with specified norm
class ConstantVelocityMagnitudeRandomFlockInitializer(utility.ParametricObject):
    def __init__(self, v):
        self.v = v

    ##
    # Initializes a flock
    # @f The flock to be initiliazed
    def init_flock(self, f):
        with f.random_state:
            f.x = random.random([f.N, d]) * f.L
            angles = random.random(f.N) * pi * 2
            f.v = array((cos(angles), sin(angles))).transpose() * self.v

class FlockSeed(utility.ParametricObject):
    def __init__(self, N, L, seed, flock_initializer):
        self.N = N
        self.L = L
        self.seed = seed
        self.flock_initializer = flock_initializer
    def create(self):
        random_state = utility.RandomState(self.seed)
        flock = Flock(self.N, self.L, random_state, self)
        self.flock_initializer.init_flock(flock)
        return flock
    def get_parameters(self):
        d = utility.ParametricObject.get_parameters(self)
        d.update(self.flock_initializer.get_parameters())
        return d

class Flock(object):
    def __init__(self, N, L, random_state, flock_seed):
        self.N = N
        self.L = L
        self.random_state = random_state
        self.flock_seed = flock_seed
        self.x = zeros([N, d])
        self.v = zeros([N, d])
        self.f = zeros([N, d])

    def get_parameters(self):
        return self.flock_initializer.get_parameters()
    
    def get_coordinate_in_original_domain(self, a):
            a = a + self.L if a < 0 else a
            a = a - self.L if a > self.L else a
            return a
    def get_position_in_original_domain(self, x):
        ''' Return the normalized position of x in the torus
        topology. Works only if a is not far from the normalized position
        (max distance L in one coordinate).'''
        return array([self.get_coordinate_in_original_domain(x[0]),
                      self.get_coordinate_in_original_domain(x[1])])
    def get_coordinate_difference(self, a, b):
        d = a - b
        d = d + self.L if d < -self.L/2 else d
        d = d - self.L if d > self.L/2 else d
        return d
    def get_vector_difference(self, a, b):
        ''' Given two vectors a and b, returns delta such that
        delta = self.period_sub(a, b)
        b + delta = a in the torus plane
        and delta.norm() is minimized.

        Valid only for a and b normalized before hand. '''
        return array([self.get_coordinate_difference(a[0], b[0]),
                      self.get_coordinate_difference(a[1], b[1])])

    ##
    # gives the distance between the birds i and j
    # @return the distance
    def distance_between_birds(self, i, j):
        return linalg.norm(self.get_vector_difference(self.x[i,:], self.x[j,:]))
    def c_params(self):
        with self.random_state:
            rnd = random.rand(self.N)
        return {'Flock_x': self.x, 'Flock_v': self.v, 'Flock_f': self.f,
                'Flock_N': self.N, 'Flock_L': self.L, 'Flock_rnd': rnd}
    def c_init(self):
        return '''
Flock((vector*)Flock_x, (vector*)Flock_v, (vector*)Flock_f,
      Flock_rnd, Flock_N, Flock_L)
'''
