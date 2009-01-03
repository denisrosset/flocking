from __future__ import with_statement
from scipy import *
from copy import *
import unittest, flock

class TestRandomState(unittest.TestCase):
    tags = ['flock']
    default_seed = 12345
    another_seed = 34567

    def setUp(self):
        self.r = flock.RandomState(self.default_seed)

    def tearDown(self):
        pass

    def assertGeneratorSameNumber(self, r1, r2):
        with r1:
            x1 = random.rand()
        with r2:
            x2 = random.rand()
        self.assertEqual(x1, x2)

    def test_copy_state(self):
        r_copy = copy(self.r)
        self.assertGeneratorSameNumber(self.r, r_copy)

    def test_seed(self):
        r_copy = speedflock.RandomState()
        r_copy.seed(self.default_seed)
        self.assertGeneratorSameNumber(self.r, r_copy)

    def test_scipy_compatibility(self):
        random.seed(self.another_seed)
        x1 = random.rand()
        
        random.seed(self.another_seed)
        with self.r:
            y1 = random.rand()
        x2 = random.rand()

        self.r.seed(self.default_seed)
        with self.r:
            y2 = random.rand()

        self.assertEqual(x1, x2)
        self.assertEqual(y1, y2)

    def test_double_acquire(self):
        self.r._acquire_scipy_random()
        self.assertRaises(Exception, self.r._acquire_scipy_random)

    def test_double_release(self):
        self.r._acquire_scipy_random()
        self.r._release_scipy_random()
        self.assertRaises(Exception, self.r._release_scipy_random)
