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
        self.main_code = [
'''
x = (vector*)x_;
v = (vector*)v_;
f = (vector*)f_;
rnd = rnd_;
''']
        self.support_code = [
        '''
const int N = %d;
const double L = %f;
#include "c_code.h"

''' % (self.flock.N, self.flock.L)
        ]
    def run(self):
        def compile_args():
            args = ['-Wno-unused-variable', '-fPIC']
            if self.debug:
                args += ['-ggdb', '-O0', '-fno-inline']
            else:
                args += ['-msse2']
                if sys.platform == 'darwin':
                    args += ['-fast']
                else:
                    args += ['-O3', '-ffast-math', '-fstrict-aliasing',
                             '-fomit-frame-pointer', '-funroll-loops',
                             '-march=native']
                    args += ['-fopenmp' if self.openmp else '-fnoopenmp']
            return args
        def linker_args():
            if not self.debug and sys.platform != 'darwin':
                return ['-fopenmp' if self.openmp else '-fnoopenmp']
            return []
        with self.flock.random_state:
            rnd = random.rand(self.flock.N)
        globals = {} # self.flock.flock_seed.get_parameters()
        headers = []
        for obj in self.objects:
            #globals.update(obj.get_parameters())
            if hasattr(obj, 'headers'):
                headers += obj.headers()
        for header in headers:
            self.support_code.insert(1, '#include "%s"' % header)
        globals['x_'] = self.flock.x
        globals['v_'] = self.flock.v
        globals['f_'] = self.flock.f
        globals['rnd_'] = rnd
        globals.update(self.values)
        # workaround bug in weave.inline, because support_code is not
        # hashed by the compiled code cache
        self.main_code.append('/*' + md5.md5('\n'.join(self.support_code)).hexdigest() + '*/')
        def get_current_module_path():
            return os.path.abspath(os.path.dirname(__file__))
        scipy.weave.inline('\n'.join(self.main_code),
                           arg_names = list(globals.keys()),
                           support_code = '\n'.join(self.support_code),
                           global_dict = globals,
                           extra_compile_args = compile_args(),
                           extra_link_args = linker_args(),
                           include_dirs = [get_current_module_path()],
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

