from __future__ import with_statement
from __future__ import division
import unittest
from scipy import *
import sys
sys.path.append('../..')
import flocking.calc

class TestCProgram(unittest.TestCase):
    tags = ['flocking']
    def test_weave(self):
        N = 100
        x_ = random.rand(N, 2)
        support_code = """
typedef double vector[2];
vector * x;
const int N = %d;
void assign(double * a, double * b) {
*a = *b;
}
""" % N
        code = """
x = (vector*)x_;
for (int i = 0; i < N; i ++)
  assign(&x[i][0], &x[i][1]);
return_val = 0;
"""
        flocking.calc.CProgram({'x_': x_}, code, support_code).run()
        for i in range(0, N):
            self.assertEquals(x_[i,0], x_[i, 1])
