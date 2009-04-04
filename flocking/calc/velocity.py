from __future__ import with_statement
from __future__ import division
from scipy import *

from . import utility
class VelocityUpdater(utility.ParametricObject):
    def __init__(self, noise_adder):
        self.noise_adder = noise_adder
        utility.ParametricObject.__init__(self)
    def c_type(self):
        return self.__class__.__name__ + '<' + self.noise_adder.c_type() + '>'
    def update(self, flock, i, dt):
        """
        Update the  velocity of bird i

        flock is the flock object holding all the flock data
        i is the current bird number
        dt is the time interval for the integration
        """
        pass
    

class OriginalVicsekVelocityUpdater(VelocityUpdater):
    def __init__(self, noise_adder, v):
        self.v = v
        self.parameters = ['noise_adder', 'v']
        VelocityUpdater.__init__(self, noise_adder)
    def update(self, flock, i, dt):
        newv = flock.f[i]
        with flock.random_state:
            noise_adder.update(newv, random.rand())
        flock.v[i] = newv * self.v / linalg.norm(newv)

### BELOW THIS LINE NOT TRANSLATED
class ConstantVelocityUpdater(VelocityUpdater):
    def __init__(self, v, amax):
        self.v = v
        self.amax = amax
        VelocityUpdater.__init__(self)
    def get_new_velocity(self, flock, i, dt):
        newv = flock.v[i,:] + flock.f[i,:] * dt
        newv = newv / linalg.norm(newv) * self.v
        diff = newv - flock.v[i,:]
        if linalg.norm(diff) > self.v * self.amax:
            diff = diff / linalg.norm(diff) * self.v * self.amax
            newv = flock.v[i,:] + diff
        return newv
    def code(self, C):
        C.append('constant_velocity_update(i, newv, %f, %f, dt);' % (self.v, self.amax))

class VariableVmaxVelocityUpdater(VelocityUpdater):
    def __init__(self, vmax, amax):
        self.vmax = vmax
        self.amax = amax
        VelocityUpdater.__init__(self)
    def get_new_velocity(self, flock, i, dt):
        newv = flock.v[i,:] + flock.f[i,:] * dt
        if linalg.norm(newv) > self.vmax:
            newv = newv / linalg.norm(newv) * self.vmax
        diff = newv - flock.v[i,:]
        if linalg.norm(diff) > linalg.norm(flock.v[i,:]) * self.amax:
            diff = diff / linalg.norm(diff) * linalg.norm(flock.v[i,:]) * self.amax
            newv = flock.v[i,:] + diff
        return newv
    def code(self, C):
        C.append('variable_vmax_velocity_update(i, newv, %f, %f, dt);' % (self.vmax, self.amax))

class VariableVminVmaxVelocityUpdater(VelocityUpdater):
    def __init__(self, vmin, vmax, amax):
        self.vmin = vmin
        self.vmax = vmax
        self.amax = amax
        VelocityUpdater.__init__(self)
    def get_new_velocity(self, flock, i, dt):
        newv = flock.v[i,:] + flock.f[i,:] * dt
        if linalg.norm(newv) > self.vmax:
            newv = newv / linalg.norm(newv) * self.vmax
        elif linalg.norm(newv) < self.vmin:
            newv = newv / linalg.norm(newv) * self.vmin
        diff = newv - flock.v[i,:]
        if linalg.norm(diff) > linalg.norm(flock.v[i,:]) * self.amax:
            diff = diff / linalg.norm(diff) * linalg.norm(flock.v[i,:]) * self.amax
            newv = flock.v[i,:] + diff
        return newv
    def code(self, C):
        C.append('variable_vmax_velocity_update(i, newv, %f, %f, %f, dt);' % (self.vmin, self.vmax, self.amax))
