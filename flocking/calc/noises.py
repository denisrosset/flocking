from __future__ import with_statement
from __future__ import division
from scipy import *

class NoiseAdder(object):
    def get_with_noise(self, v, r):
        """
        Return the velocity with added noise

        v is the velocity without noise
        r is the random generator state to be used
        """
        pass
    def code(self, C):
        """
        Append the C code to the C code object to add noise to the
        current velocity
        
        i is the current bird number
        newv[2] is the new velocity without noise
        v[i][2] is the velocity to update with noise

        rnd is pointer to the current random number in the random
        number array, should be used as *rnd++
        """
        pass
    def code_size_random_array(self, N):
        """
        Return the number of random numbers per step to be generated
        when the C code is used

        N is the number of birds

        Code should be put in braces if new variables are declarated
        """
        pass

class DummyNoiseAdder(NoiseAdder):
    def __init__(self):
        NoiseAdder.__init__(self)
    def get_with_noise(self, v, r):
        return array(v)
    def code(self, C):
        C.append('''
v[i][0] = newv[0];
v[i][1] = newv[1];
''')
    def code_size_random_array(self, N):
        return 0

class ScalarNoiseAdder(NoiseAdder):
    def __init__(self, eta):
        self.eta = eta
        NoiseAdder.__init__(self)
    def get_with_noise(self, v, r):
        vx = v[0]
        vy = v[1]
        with r:
            deltaTheta = (random.random() - 1/2) * pi * 2 * self.eta
        cs = cos(deltaTheta)
        sn = sin(deltaTheta)
        return array([vx * cs - vy * sn,
                      vx * sn + vy * cs])
    def code_size_random_array(self, N):
        if self.eta == 0:
            return 0
        else:
            return N
    def code(self, C):
        if self.eta == 0:
            DummyNoiseAdder().code(C)
            return
        C.append('''
{
double eta = ScalarNoiseAdder_eta;
double angle = (*rnd++ - 0.5) * 2 * M_PI * eta;
double cs = cos(angle), sn = sin(angle);
v[i][0] = cs * newv[0] - sn * newv[1];
v[i][1] = sn * newv[0] + cs * newv[1];
}
''')
