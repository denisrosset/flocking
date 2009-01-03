from __future__ import with_statement
from __future__ import division
import unittest
from scipy import *
import scipy.weave
from speedflock import *

class TestWeave(unittest.TestCase):
    tags = ['speedflock']
    def test_weave(self):
        x_ = random.rand(10, 2)
        v_ = random.rand(10, 2)
        f_ = random.rand(10, 2)
        rnd_ = random.rand(10)
        N = 10
        support_code = """
typedef double vector[2];
vector * x;
vector * v;
vector * f;
double * rnd;
const int N = %d;
void assign(double * a, double * b) {
*a = *b;
}
""" % N
        code = """
x = (vector*)x_;
v = (vector*)v_;
f = (vector*)f_;
rnd = rnd_;
for (int i = 0; i < N; i ++)
  assign(&x[i][0], &x[i][1]);
return_val = 0;
"""
        err = scipy.weave.inline(code, ['x_', 'v_', 'f_', 'rnd_'],
                                 support_code = support_code,
                                 extra_compile_args=['-Wno-unused-variable'],
                                 compiler = 'gcc')
        for i in range(0, N):
            self.assertEquals(x_[i,0], x_[i, 1])
