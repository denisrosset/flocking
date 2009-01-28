from __future__ import with_statement
from __future__ import division
from scipy import *

from . import utility
class VelocityUpdater(utility.ParametricObject):
    def get_new_velocity(self, flock, i, dt):
        """
        Return the new velocity of bird i, without modifying the
        actual value in the flock object.

        flock is the flock object holding all the flock data
        i is the current bird number
        dt is the time interval for the integration
        """
        pass
    def code(self, C):
        """
        Append the C code for the velocity update to the C code object

        In the C code :
        
        newv[2] is the new velocity to return, is garbage before
        the code is exectued
        i is the current bird number

        Please enclose the code in { } braces if you declare new variables
        """
        pass

class OriginalVicsekVelocityUpdater(VelocityUpdater):
    def __init__(self, v):
        self.v = v
        VelocityUpdater.__init__(self)
    def get_new_velocity(self, flock, i, dt):
        a = flock.v[i,:] + flock.f[i,:]
        new_v = a / linalg.norm(a) * self.v
        return new_v
    def code(self, C):
        C.append('''
{
newv[0] = v[i][0] + f[i][0];
newv[1] = v[i][1] + f[i][1];
double vv = %f;
double factor = vv/sqrt(newv[0]*newv[0] + newv[1]*newv[1]);
newv[0] *= factor;
newv[1] *= factor;
}
''' % (self.v))

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
        C.append('''
{
double vv = %f;
double amax = %f;
newv[0] = v[i][0] + f[i][0] * dt;
newv[1] = v[i][1] + f[i][1] * dt;
double normnewv = sqrt(newv[0]*newv[0] + newv[1]*newv[1]);
newv[0] /= normnewv * vv;
newv[1] /= normnewv * vv;
vector diff;
diff[0] = newv[0] - v[i][0];
diff[1] = newv[1] - v[i][1];
double normdiffsq = diff[0]*diff[0] + diff[1]*diff[1];
if (normdiffsq > vv * vv * amax * amax)
{
double factor = vv * amax / sqrt(normdiffsq);
diff[0] *= factor;
diff[1] *= factor;
newv[0] = v[i][0] + diff[0];
newv[1] = v[i][1] + diff[1];
}
}
''' % (self.v, self.amax))

class VariableVmaxVelocityUpdater(VelocityUpdater):
    def __init__(self, v, amax):
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
        C.append('''
{
double vmax = %f;
double amax = %f;
double normvsq = v[i][0] * v[i][0] + v[i][1] * v[i][1];
newv[0] = v[i][0] + f[i][0] * dt;
newv[1] = v[i][1] + f[i][1] * dt;
double normnewvsq = newv[0] * newv[0] + newv[1] * newv[1];
if (normnewvsq > vmax * vmax)
{
double normnewv = sqrt(normnewvsq);
newv[0] *= vmax / normnewv;
newv[1] *= vmax / normnewv;
}
vector diff;
diff[0] = newv[0] - v[i][0];
diff[1] = newv[1] - v[i][1];
double normdiffsq = diff[0]*diff[0] + diff[1]*diff[1];
if (normdiffsq > normvsq * amax * amax)
{
double factor = amax * sqrt(normvsq / normdiffsq);
diff[0] *= factor;
diff[1] *= factor;
newv[0] = v[i][0] + diff[0];
newv[1] = v[i][1] + diff[1];
}
}
''' % (self.vmax, self.amax))

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
        C.append('''
{
double vmin = %f;
double vmax = %f;
double amax = %f;
double normvsq = v[i][0] * v[i][0] + v[i][1] * v[i][1];
newv[0] = v[i][0] + f[i][0] * dt;
newv[1] = v[i][1] + f[i][1] * dt;
double normnewvsq = newv[0] * newv[0] + newv[1] * newv[1];
if (normnewvsq > vmax * vmax)
{
double normnewv = sqrt(normnewvsq);
newv[0] *= vmax / normnewv;
newv[1] *= vmax / normnewv;
} else if (normnewvsq < vmin * vmin)
{
double normnewv = sqrt(normnewvsq);
newv[0] *= vmin / normnewv;
newv[1] *= vmin / normnewv;
}

vector diff;
diff[0] = newv[0] - v[i][0];
diff[1] = newv[1] - v[i][1];
double normdiffsq = diff[0]*diff[0] + diff[1]*diff[1];
if (normdiffsq > normvsq * amax * amax)
{
double factor = amax * sqrt(normvsq / normdiffsq);
diff[0] *= factor;
diff[1] *= factor;
newv[0] = v[i][0] + diff[0];
newv[1] = v[i][1] + diff[1];
}
}
''' % (self.vmin, self.vmax, self.amax))
