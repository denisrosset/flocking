### BELOW THIS LINE NOT CONVERTED YET

class VicsekAverageForceEvaluator(AverageForceEvaluator):
    def __init__(self, beta):
        self.beta = beta
        AverageForceEvaluator.__init__(self)
    
    def term(self, flock, i, j):
        return flock.v[j,:]

    def shape_sum(self, flock, i, s, Nn):
        veff = (s + flock.v[i,:]) / (Nn + 1)
        return (veff - flock.v[i,:]) * self.beta

    def add_term_code(self, C, name):
        C.append('vicsek_average_force_add_term(j, %s);' % name)

    def shape_sum_code(self, C, name):
        # TODO: check following code which version is ok
        C.append('vicsek_average_force_shape_term(i, %s, %f, Nn);' % (name, self.beta))

class NeighborAverageForceEvaluator(AverageForceEvaluator):
    def __init__(self, beta):
        self.beta = beta
        AverageForceEvaluator.__init__(self)

    def term(self, flock, i, j):
        return flock.v[j,:] - flock.v[i,:]

    def shape_sum(self, flock, i, s, Nn):
        # TODO : should be normalized over number of birds?
        return s * self.beta

    def add_term_code(self, C, name):
        C.append('neighbor_average_force_add_term(i, j, %s);' % name)

    def shape_sum_code(self, C, name):
        C.append('neighbor_average_force_shape_term(%s, %f);' % (name, self.beta))

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
    def add_term_code(self, C, name):
        pass
    def shape_sum_code(self, C, name):
        C.append('cruising_regulator_force_shape_term(i, %s, %f, %f);' % (name, self.gamma, self.v))

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
    def shape_sum_code(self, C, name):
        pass

class LennardJonesInteractionForceEvaluator(GenericInteractionForceEvaluator):
    def __init__(self, epsilon, sigma, offset):
        self.epsilon = epsilon
        self.sigma = sigma
        self.offset = offset
        GenericInteractionForceEvaluator.__init__(self)
    def interaction_func(self, r):
        return 4 * self.epsilon * ((self.sigma/r)**12 - (self.sigma/r)**6) + self.offset;
    def add_term_code(self, C, name):
        C.append('lennard_jones_interaction_force_add_term(%s, r, normr, normrsq, %f, %f, %f);'
                 % (name, self.epsilon, self.sigma, self.offset))

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
    def add_term_code(self, C, name):
        C.append('piecewise_linear_interaction_force_add_term(%s, r, norm, normrsq, %f, %f, %f, %f);' % (name, self.Frep, self.Fattr, self.r0, self.r1))
        
