from __future__ import with_statement
from __future__ import division

import md5

from scipy import *
import scipy.weave

from . import forces
from . import c_code

class FlockStep(object):
    def __init__(self,
                 dt,
                 neighbor_selector,
                 velocity_updater,
                 noise_adder,
                 fav_evaluator,
                 fint_evaluator,
                 fvreg_evaluator):
        self.dt = dt
        self.neighbor_selector = neighbor_selector
        self.velocity_updater = velocity_updater
        self.noise_adder = noise_adder
        self.fav_evaluator = fav_evaluator
        self.fint_evaluator = fint_evaluator
        self.fvreg_evaluator = fvreg_evaluator

    def c_step(self, flock, steps = 1):
        # available variables in C/C++ code :
        # type vector is double[2]
        # 
        # (x[i][0], x[i][1]) is the position of bird i
        # (v[i][0], v[i][1]) is the velocity of bird i
        # (f[i][0], f[i][1]) is the force acting of bird i
        #
        # N is the number of birds
        # rnd is a pointer to the current random number
        #     random numbers are generated is python code to
        #     have consistency between the c and python code
        # L is the width/height of periodic cell
        # dt is the time step
        #
        # comp_sub(a, b) is the distance between two point a and b on
        # the circle mathbb{R}/L*mathbb{Z}
        #
        # loop_coord(a) is the canonical position of a on the interval
        # [0, L]. a could be anywhere on the interval [-L, 2*L]
        #
        # i is the current bird position
        assert(isinstance(self.fav_evaluator, forces.AverageForceEvaluator))
        assert(isinstance(self.fint_evaluator, forces.InteractionForceEvaluator))
        assert(isinstance(self.fvreg_evaluator, forces.VelocityForceEvaluator))
        C = c_code.CProgram(flock, 
                            n_random_numbers = self.noise_adder.
                            code_size_random_array(flock.N) * steps,
                            objects = [self.neighbor_selector,
                                       self.velocity_updater,
                                       self.noise_adder,
                                       self.fav_evaluator,
                                       self.fint_evaluator,
                                       self.fvreg_evaluator]
                            )
        C.append('const double dt = %f;' % self.dt)
        with c_code.StructuredBlock(C,
                             'for(int step = 0; step < %d; step ++) {' % steps,
                             '}'):
            self.neighbor_selector.init_code(C)
            with c_code.StructuredBlock(C,
                                        '''
for (int i = 0; i < N; i ++) {
vector fvreg = {0, 0};
vector fav = {0, 0};
vector fint = {0, 0};
int Nn = 0;
f[i][0] = f[i][1] = 0;''',
                                        '''
f[i][0] = fav[0] + fvreg[0] + fint[0];
f[i][1] = fav[1] + fvreg[1] + fint[1];
}'''
                                        ):
                with self.neighbor_selector.code(C):
                    self.fav_evaluator.add_term_code(C)
                    self.fint_evaluator.add_term_code(C)
                    self.fvreg_evaluator.add_term_code(C)
                self.fav_evaluator.shape_sum_code(C)
                self.fint_evaluator.shape_sum_code(C)
                self.fvreg_evaluator.shape_sum_code(C)
            with c_code.StructuredBlock(C,
                                 '''
for (int i = 0; i < N; i ++) {
double newv[2];
''',
                                 '}'):
                self.velocity_updater.code(C)
                self.noise_adder.code(C)
            C.append('''
for (int i = 0; i < N; i ++) {
x[i][0] = loop_coord(x[i][0] + v[i][0] * dt);
x[i][1] = loop_coord(x[i][1] + v[i][1] * dt);
}''')
        C.run()

    def step(self, flock, steps = 1):
        for i in range(0, steps):
            self.step_forces(flock)
            self.step_velocities(flock)
            self.step_positions(flock)

    def step_forces(self, flock):
        self.neighbor_selector.prepare_neighbors(flock)
        for i in range(0, flock.N):
            fint = array([0., 0.])
            fav = array([0., 0.])
            fvreg = array([0., 0.])
            ll = self.neighbor_selector.get_list_of_neighbors(flock, i)
            Nn = len(ll)
            for j in ll:
                fint = fint + self.fint_evaluator.term(flock, i, j)
                fav = fav + self.fav_evaluator.term(flock, i, j)
                fvreg = fvreg + self.fvreg_evaluator.term(flock, i, j)
            flock.f[i,:] = (self.fint_evaluator.shape_sum(flock, i, fint, Nn) +
                            self.fav_evaluator.shape_sum(flock, i, fav, Nn) +
                            self.fvreg_evaluator.shape_sum(flock, i, fvreg, Nn))

    def step_velocities(self, flock):
        for i in range(0, flock.N):
            flock.v[i, :] = self.noise_adder.get_with_noise(
                self.velocity_updater.get_new_velocity(flock, i, self.dt),
                flock.random_state)

    def step_positions(self, flock):
        for i in range(0, flock.N):
            flock.x[i, :] = flock.loop_position(
                flock.x[i, :] + flock.v[i, :] * self.dt)
