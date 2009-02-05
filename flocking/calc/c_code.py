from __future__ import with_statement
from __future__ import division
from scipy import random
import numpy
import scipy
import scipy.weave
import md5
import sys
debug = False

class CProgram(list):
    def __init__(self, flock, n_random_numbers = 0, objects = [], values = {}):
        self.flock = flock
        self.n_random_numbers = n_random_numbers
        self.objects = objects
        self.values = values
        self.append(
'''
x = (vector*)x_;
v = (vector*)v_;
f = (vector*)f_;
rnd = rnd_;
''')
    def support_code(self):
        return '''
typedef double vector[2];
vector * __restrict__ x, * __restrict__ v, * __restrict__ f;
double * __restrict__ rnd;
const int N = %d;
const double L = %f;

double inline
comp_sub(double a, double b)
{
double d = a - b;
d = d < -L/2 ? d + L : d;
d = d > L/2 ? d - L : d;
return d;
}

double inline
loop_coord(double a)
{
a = a < 0 ? a + L : a;
a = a > L ? a - L : a;
return a;
}

double inline
distance_between_birds_sq(int i, int j)
{
double dx = comp_sub(x[i][0], x[j][0]);
double dy = comp_sub(x[i][1], x[j][1]);
return dx * dx + dy * dy;
}

double inline
distance_between_birds(int i, int j)
{
return sqrt(distance_between_birds_sq(i, j));
}
''' % (self.flock.N, self.flock.L)
    def run(self):
        with self.flock.random_state:
            rnd = random.rand(self.n_random_numbers)
        if self.n_random_numbers == 0:
            rnd = scipy.zeros([1])
        global debug
        flags = ['-Wno-unused-variable', '-fPIC']
        
        if not debug:
            flags += ['-msse2']
            if sys.platform == 'darwin':
                flags += ['-fast']
            else:
                flags += ['-O3', '-ffast-math', '-fstrict-aliasing', '-fomit-frame-pointer']
        else:
            flags += ['-Wno-unused-variable', '-ggdb', '-fPIC', '-O0']

        globals = self.flock.flock_seed.get_parameters()
        for obj in self.objects:
            globals.update(obj.get_parameters())
        globals['x_'] = self.flock.x
        globals['v_'] = self.flock.v
        globals['f_'] = self.flock.f
        globals['rnd_'] = rnd
        globals.update(self.values)
        support_code = self.support_code()
        # workaround bug, support_code is not hashed
        self.append('/*' + md5.md5(support_code).hexdigest() + '*/')
        scipy.weave.inline('\n'.join(self),
                           arg_names = list(globals.keys()),
                           support_code = support_code,
                           global_dict = globals,
                           extra_compile_args = flags,
                           compiler = 'gcc')

class StructuredBlock(object):
    def __init__(self, program, enter_code, exit_code):
        self.enter_code = enter_code
        self.exit_code = exit_code
        self.program = program
    def __enter__(self):
        self.program.append(self.enter_code)
    def __exit__(self, type, value, traceback):
        self.program.append(self.exit_code)

