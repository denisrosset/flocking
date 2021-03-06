from __future__ import with_statement
from __future__ import division

import md5
import os

from scipy import *
import scipy.weave

from . import force
from . import utility
from . import c_code

class FlockStep(utility.ParametricObject):
    def __init__(self,
                 dt,
                 neighbor_selector,
                 velocity_updater,
                 position_algorithm,
                 force_evaluators):
        self.dt = dt
        self.neighbor_selector = neighbor_selector
        self.velocity_updater = velocity_updater
        self.position_algorithm = position_algorithm
        self.force_evaluators = force_evaluators
        number_of_C_force_evaluators = 4
        self.c_force_evaluators = (self.force_evaluators +
                                   (number_of_C_force_evaluators - 
                                    len(self.force_evaluators)) *
                                   [force.DummyForceEvaluator()])
    def get_parameters(self):
        d = utility.ParametricObject.get_parameters(self)
        for obj in [self.neighbor_selector,
                    self.velocity_updater,
                    self.position_algorithm] + self.force_evaluators:
            d.update(obj.get_parameters())
        return d
    def c_type(self):
        return 'FlockStep<' + ','.join(
            [
                self.neighbor_selector.c_type(),
                self.velocity_updater.c_type(),
                self.position_algorithm.c_type()] +
            [force_evaluator.c_type() for force_evaluator in self.c_force_evaluators]) + '>'

    def c_params(self):
        def merge(seq):
            merged = []
            for s in seq:
                for x in s:
                    merged.append(x)
            return merged
        return dict([('FlockStep_dt', self.dt)] +
                    self.neighbor_selector.c_params().items() +
                    self.velocity_updater.c_params().items() +
                    self.position_algorithm.c_params().items() +
                    merge([force_evaluator.c_params().items() for
                           force_evaluator in self.force_evaluators]))
    def c_init(self):
        return self.c_type() + '(FlockStep_dt, ' + ', '.join(
            [
                self.neighbor_selector.c_init(),
                self.velocity_updater.c_init(),
                self.position_algorithm.c_init()] +
            [force_evaluator.c_init() for force_evaluator in self.c_force_evaluators]) + ')'

    def step(self, flock, fast = True, debug = False):
        if fast:
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    self.c_type() + ' flockstep = ' + self.c_init() + ';',
                    'flockstep.step(flock);'])
            vars = dict(self.c_params().items() + flock.c_params().items())
            headers = ['flockstep.h']
            c_code.CProgram(vars, code, headers, debug = debug).run()
        else:
            for i in range(0, flock.N):
                flock.f[i][0] = flock.f[i][1] = 0.0
            self.neighbor_selector.update(flock, self.force_evaluators)
            self.position_algorithm.update(flock, self.velocity_updater, self.dt)
