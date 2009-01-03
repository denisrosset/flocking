from __future__ import with_statement
from __future__ import division
from scipy import *
from speedflock.utility import *

class ForceEvaluator(ComputationObject):
    def __init__(self):
        ComputationObject.__init__(self)
    def term(self, flock, i, j):
        """
        Return the term from bird j acting on bird i.

        All the terms will be added before the sum being submitted
        to shape_sum

        i - current bird
        j - neighbor bird in consideration
        flock - current flock
        """
        pass
    def shape_sum(self, flock, i, s, Nn):
        """
        Shape the sum of terms s acting on bird i.

        i - current bird
        s - sum of all terms
        Nn - number of neighbors
        flock - current flock
        """
        pass
    def add_term_code(self):
        """
        Append the C code for the evaluation to the C code object.

        Must add the term to the variable 'name' where name is the
        name of the force type

        name[0] += ...;
        name[1] += ...;

        i is the current bird, j is the neighbor bird in consideration
        r is the distance between the two birds
        normr, normrsq are the norm of r and the norm of r squared
        """
        pass

    def shape_sum_code(self):
        """
        Append the C code to shape the sum to the C code object.

        Must act directly on the name[2] variable
        """
        pass

class AverageForceEvaluator(ForceEvaluator):
    def __init__(self):
        ForceEvaluator.__init__(self)

class InteractionForceEvaluator(ForceEvaluator):
    def __init__(self):
        ForceEvaluator.__init__(self)

class VelocityForceEvaluator(ForceEvaluator):
    def __init__(self):
        ForceEvaluator.__init__(self)

class OriginalVicsekAverageForceEvaluator(AverageForceEvaluator):
    def __init__(self):
        AverageForceEvaluator.__init__(self)

    def term(self, flock, i, j):
        return flock.v[j,:]

    def shape_sum(self, flock, i, s, Nn):
        return s

    def add_term_code(self, C):
        C.append('''
fav[0] += v[j][0];
fav[1] += v[j][1];
''')

    def shape_sum_code(self, C):
        pass

class VicsekAverageForceEvaluator(AverageForceEvaluator):
    def __init__(self, beta):
        self.beta = beta
        AverageForceEvaluator.__init__(self)
    
    def term(self, flock, i, j):
        return flock.v[j,:]

    def shape_sum(self, flock, i, s, Nn):
        veff = (s + flock.v[i,:]) / (Nn + 1)
        return (veff - flock.v[i,:]) * self.beta

    def add_term_code(self, C):
        C.append('''
fav[0] += v[j][0];
fav[1] += v[j][1];
''')
    def shape_sum_code(self, C):
        # TODO: check following code which version is ok
        C.append('''
{
const double beta = VicsekAverageForceEvaluator_beta;
vector veff;
veff[0] = (%s[0] + v[i][0]) / (Nn + 1);
veff[1] = (%s[1] + v[i][1]) / (Nn + 1);
fav[0] = (veff[0] - v[i][0]) * beta;
fav[1] = (veff[1] - v[i][1]) * beta;
}
''')

class NeighborAverageForceEvaluator(AverageForceEvaluator):
    def __init__(self, beta):
        self.beta = beta
        AverageForceEvaluator.__init__(self)

    def term(self, flock, i, j):
        return flock.v[j,:] - flock.v[i,:]

    def shape_sum(self, flock, i, s, Nn):
        # TODO : should be normalized over number of birds?
        return s * self.beta

    def add_term_code(self, C):
        C.append('''
fav[0] += v[j][0] - v[i][0];
fav[1] += v[j][1] - v[j][1];
''')
    def shape_sum_code(self, C):
        C.append('''
const double beta = NeighborAverageForceEvaluator_beta;
fav[0] *= beta;
fav[1] *= beta;
''')

class DummyAverageForceEvaluator(AverageForceEvaluator):
    def __init__(self):
        AverageForceEvaluator.__init__(self)
    def term(self, flock, i, j):
        return array([0., 0.])
    def shape_sum(self, flock, i, s, Nn):
        return array([0., 0.])
    def add_term_code(self, C):
        C.append('''
fav[0] = 0;
fav[1] = 0;
''')
    def shape_sum_code(self, C):
        pass

class DummyInteractionForceEvaluator(InteractionForceEvaluator):
    def __init__(self):
        InteractionForceEvaluator.__init__(self)
    def term(self, flock, i, j):
        return array([0., 0.])
    def shape_sum(self, flock, i, s, Nn):
        return array([0., 0.])
    def add_term_code(self, C):
        C.append('''
fint[0] = 0;
fint[1] = 0;
''')
    def shape_sum_code(self, C):
        return '' # nothing

class DummyVelocityForceEvaluator(VelocityForceEvaluator):
    def __init__(self):
        VelocityForceEvaluator.__init__(self)
    def term(self, flock, i, j):
        return array([0., 0.])
    def shape_sum(self, flock, i, s, Nn):
        return array([0., 0.])
    def add_term_code(self, C):
        C.append('''
fvreg[0] = 0;
fvreg[1] = 0;
''')
    def shape_sum_code(self, C):
        pass

class CruisingRegulatorForceEvaluator(VelocityForceEvaluator):
    def __init__(self, v, gamma):
        self.v = v
        self.gamma = gamma
        VelocityForceEvaluator.__init__(self)
    def term(self, flock, i, j):
        return array([0., 0.])
    def shape_sum(self, flock, i, s, Nn):
        vnorm = linalg.norm(flock.v[i,:])
        return self.gamma * (self.v - vnorm) * flock.v[i,:] / vnorm
    def add_term_code(self, C):
        pass
    def shape_sum_code(self, C):
        C.append('''
{
double vnorm = sqrt(v[i][0]*v[i][0] + v[i][1]*v[i][1]);
const double gamma = CruisingRegulatorForceEvaluator_gamma;
const double vv = CruisingRegulatorForceEvaluator_v;
double factor = gamma * (vv - vnorm) / vnorm;
fvreg[0] = v[i][0] * factor;
fvreg[1] = v[i][1] * factor;
}
''')

class GenericInteractionForceEvaluator(InteractionForceEvaluator):
    def __init__(self):
        InteractionForceEvaluator.__init__(self)
    def interaction_func(self, r):
        return 0
    def interaction_func_code(self):
        '''
        Must evaluate int_func, that is the magnitude and sign of
        the interaction force.
        '''
        pass
    def term(self, flock, i, j):
        r = flock.period_sub(flock.x[i,:], flock.x[j,:]) # x_i - x_j
        normr = linalg.norm(r)
        return self.interaction_func(normr) * r / normr
    def shape_sum(self, flock, i, s, Nn):
        return s
    def add_term_code(self, C):
        C.append('''
{
double int_func = 0;
''' + self.interaction_func_code() + '''
fint[0] += int_func * r[0] / normr;
fint[1] += int_func * r[1] / normr;
}
''')
    def shape_sum_code(self, C):
        pass

class LennardJonesInteractionForceEvaluator(GenericInteractionForceEvaluator):
    def __init__(self, epsilon, sigma, offset):
        self.epsilon = epsilon
        self.sigma = sigma
        self.offset = offset
        GenericInteractionForceEvaluator.__init__(self)
    def interaction_func(self, r):
        return 4 * self.epsilon * ((self.sigma/r)**12 - (self.sigma/r)**6) + self.offset;
    def interaction_func_code(self):
        return '''
{
const double epsilon = LennardJonesInteractionForceEvaluator_epsilon;
const double sigma = LennardJonesInteractionForceEvaluator_sigma;
const double offset = LennardJonesInteractionForceEvaluator_offset;
double sigma_over_d_2 = sigma*sigma/normrsq;
double sigma_over_d_4 = sigma_over_d_2*sigma_over_d_2;
double sigma_over_d_6 = sigma_over_d_2*sigma_over_d_4;
double sigma_over_d_12 = sigma_over_d_6*sigma_over_d_6;
int_func = 4 * epsilon * (sigma_over_d_12 - sigma_over_d_6) + offset;
}
'''

class PiecewiseLinearInteractionForceEvaluator(GenericInteractionForceEvaluator):
    def __init__(self, Frep, Fattr, r0, r1):
        self.Frep = Frep
        self.Fattr = Fattr
        self.r0 = r0
        self.r1 = r1
        GenericInteractionForceEvaluator.__init__(self)
    def interaction_func(self, r):
        where = min(self.r1, max(self.r0, r))
        return (self.Frep + (self.Fattr - self.Frep) * 
                (where - self.r0) / (self.r1 - self.r0))
    def interaction_func_code(self):
        return '''
{
const double Frep = PiecewiseLinearInteractionForceEvaluator_Frep;
const double Fattr = PiecewiseLinearInteractionForceEvaluator_Fattr;
const double r0 = PiecewiseLinearInteractionForceEvaluator_r0;
const double r1 = PiecewiseLinearInteractionForceEvaluator_r1;
double where = normr < r0 ? r0 : normr;
where = normr > r1 ? r1 : normr;
int_func = Frep + (Fattr - Frep) * (where - r0) / (r1 - r0);
}
'''
