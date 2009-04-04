from __future__ import with_statement
from __future__ import division

import md5
import os

from scipy import *
import scipy.weave

from . import force
from . import utility

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

    def c_step(self, flock):
        support_code = '#include "flockstep.h"'
        main_code = '\n'.join([
                'Flock flock = ' + flock.c_init() + ';',
                self.c_type() + ' flockstep = ' + self.c_init() + ';',
                'flockstep.step(flock);'])
        globals = dict(self.c_params().items() + flock.c_params().items())
        def get_current_module_path():
            return os.path.abspath(os.path.dirname(__file__))
        scipy.weave.inline(main_code,
                           arg_names = list(globals.keys()),
                           support_code = support_code,
                           global_dict = globals,
                           extra_compile_args = ['-fPIC', '-fast', '-msse2', '-Wno-unused-variable', '-Wno-unknown-pragmas'],
                           extra_link_args = ['-read_only_relocs suppress'],
                           include_dirs = [get_current_module_path()],
                           compiler = 'gcc')

    def step(self, flock):
        self.neighbor_selector.update(flock, self.force_evaluators)
        self.position_algorithm.update(flock, self.velocity_updater, self.dt)
