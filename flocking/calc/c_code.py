from __future__ import with_statement
from __future__ import division
from scipy import random
import numpy
import scipy
import scipy.weave
import md5
import sys
import os.path
debug = False

class CProgram:
    def __init__(self, flock, n_random_numbers = 0, objects = [], values = {}):
        self.flock = flock
        self.debug = False
        self.openmp = True
        self.n_random_numbers = n_random_numbers
        self.objects = objects
        self.values = values
        self.include_subdirs = []
        self.headers = []
        self.main_code = [
'''
x = (vector*)x_;
v = (vector*)v_;
f = (vector*)f_;
rnd = rnd_;
''']
        self.support_code = [
        '''
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
        ]
    def run(self):
        with self.flock.random_state:
            rnd = random.rand(self.n_random_numbers)
        if self.n_random_numbers == 0:
            rnd = scipy.zeros([1])
        extra_compile_args = ['-Wno-unused-variable', '-fPIC']
        extra_link_args = []
        if self.debug:
            extra_compile_args += ['-Wno-unused-variable', '-ggdb',
                                   '-fPIC', '-O0', '-fno-inline']
        else:
            extra_compile_args += ['-msse2']
            if sys.platform == 'darwin':
                extra_compile_args += ['-fast']
            else:
                extra_compile_args += ['-O3', '-ffast-math',
                                       '-fstrict-aliasing',
                                       '-fomit-frame-pointer',
                                       '-funroll-loops',
                                       '-march=native']
                if self.openmp:
                    extra_compile_args += ['-fopenmp']
                    extra_linker_args += ['-fopenmp']
                else:
                    extra_compile_args += ['-fnoopenmp']
                    extra_linker_args += ['-fnoopenmp']
        globals = self.flock.flock_seed.get_parameters()
        for obj in self.objects:
            globals.update(obj.get_parameters())
        globals['x_'] = self.flock.x
        globals['v_'] = self.flock.v
        globals['f_'] = self.flock.f
        globals['rnd_'] = rnd
        globals.update(self.values)
        # workaround bug in weave.inline, because support_code is not
        # hashed by the compiled code cache
        self.main_code.append('/*' + md5.md5('\n'.join(self.support_code)).hexdigest() + '*/')
        module_directory = os.path.abspath(os.path.dirname(__file__))
        scipy.weave.inline('\n'.join(self.main_code),
                           arg_names = list(globals.keys()),
                           support_code = '\n'.join(self.support_code),
                           global_dict = globals,
                           extra_compile_args = extra_compile_args,
                           extra_link_args = extra_link_args,
                           headers = self.headers,
                           include_dirs = [module_directory + '/' + dir for dir in self.include_subdirs],
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

