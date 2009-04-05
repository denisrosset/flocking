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
    def __init__(self, vars, code, headers, openmp = True, debug = False):
        self.vars = vars
        self.code = code
        self.headers = headers
        self.debug = debug
        self.openmp = openmp
    def run(self):
        def compile_args():
            args = ['-Wno-unused-variable', '-fPIC', '-Wno-unknown-pragmas']
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
            if sys.platform == 'darwin':
                return ['-read_only_relocs suppress']
            return []
        def get_current_module_path():
            return os.path.abspath(os.path.dirname(__file__) + '/../C')
        support_code = ''
        for header in self.headers:
            support_code += '#include "%s"\n' % header

        scipy.weave.inline(self.code,
                           arg_names = list(self.vars.keys()),
                           support_code = support_code,
                           global_dict = self.vars,
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

