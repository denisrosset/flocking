from __future__ import with_statement
from __future__ import division
from scipy import *
import scipy.linalg
import math
import zlib
import cPickle as pickle
import copy
import subprocess
try:
    import networkx
except:
    pass

from ..calc import c_code

class Sampler(object):
    pass
        
class PeriodicSampler(Sampler):
    def __init__(self, measure, every):
        self.measure = measure
        self.every = every
    def __call__(self, flock, flockstep, step, fast = True):
        if step % self.every == 0:
            return self.measure(flock, flockstep)
        return None

class PeriodicStatisticsSampler(Sampler):
    """Give online standard statistics (mean, variance, skewness, kurtosis) for the system studied.
  
       Formulas are from 
       @article{pebay:fro,
                Author = {Pebay, P.},
                Title = {{Formulas for Robust, One-Pass Parallel Computation of Covariances and Arbitrary-Order Statistical Moments}},
       """
    def __init__(self, measure, sample_every, store_every, skip_first):
        self.measure = measure
        self.sample_every = sample_every
        self.store_every = store_every
        self.skip_first = skip_first
        self.n = 0
        self.m = 0.
        self.M2 = 0.
        self.M3 = 0.
        self.M4 = 0.
    def __call__(self, flock, flockstep, step, fast = True):
        if step < self.skip_first:
            return None
        if step % self.sample_every == 0:
            x = self.measure(flock, flockstep)
            delta = x - self.m
            np = self.n + 1
            mp = self.m + delta/np
            M2p = self.M2 + delta**2 * (np - 1)/np
            M3p = self.M3 + delta**3 * (np - 1)*(np - 2)/np**2 - 3*delta*self.M2/np
            M4p = self.M4 + delta**4 * (np - 1)*(np**2 - 3*np +3)/np**3 + 6*delta**2*self.M2/np**2 - 4*delta*self.M3/np
            self.n = np
            self.m = mp
            self.M2 = M2p
            self.M3 = M3p
            self.M4 = M4p
        if step % self.store_every == 0:
            mean = self.m
            variance = self.M2 / self.n
            skewness = math.sqrt(self.n) * self.M3 / math.sqrt(self.M2**3)
            kurtosis = self.n * self.M4 / self.M2**2 - 3
            return (self.n, mean, variance, skewness, kurtosis)
        else:
            return None
                      

class Measure(object):
    def __call__(self, flock, flockstep, fast = True):
        pass

class Flock(Measure):
    def __call__(self, flock, flockstep, fast = True):
        return copy.deepcopy(flock)

class Phi(Measure):
    def __call__(self, flock, flockstep, fast = True):
        sum_of_velocities = sum(flock.v, 0)
        sum_of_norms = sum(sqrt(sum(flock.v**2, 1)))
        return scipy.linalg.norm(sum_of_velocities) / sum_of_norms

class MeanVelocity(Measure):
    def __call__(self, flock, flockstep, fast = True):
        sum_of_velocities = sum(flock.v, 0)
        sum_of_norms = sum(sqrt(sum(flock.v**2, 1)))
        return sum_of_velocities / sum_of_norms

class MinNearestNeighborDistance(Measure):
    def __call__(self, flock, flockstep, fast = True):
        if fast:
            distance = zeros([1])
            vars = dict(flock.c_params().items() + flockstep.c_params().items() + [('distance', distance)])
            headers = ['sampler.h']
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    '*distance = MinNearestNeighborDistance().compute(flock, ' +
                    flockstep.neighbor_selector.c_init() + ');'])
            c_code.CProgram(vars, code, headers, openmp = False).run()
            return distance[0]
        else:
            return min([min([flock.distance_between_birds(i, j) for i in range(0, flock.N) if i != j]) for j in range(0, flock.N)])


class MaxNearestNeighborDistance(Measure):
    def __call__(self, flock, flockstep, fast = True):
        if fast:
            distance = zeros([1])
            vars = dict(flock.c_params().items() + flockstep.c_params().items() + [('distance', distance)])
            headers = ['sampler.h']
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    '*distance = MaxNearestNeighborDistance().compute(flock, ' +
                    flockstep.neighbor_selector.c_init() + ');'])
            c_code.CProgram(vars, code, headers, openmp = False).run()
            return distance[0]
        else:
            return max([min([flock.distance_between_birds(i, j) for i in range(0, flock.N) if i != j]) for j in range(0, flock.N)])


class MeanNearestNeighborDistance(Measure):
    def __call__(self, flock, flockstep, fast = True):
        if fast:
            distance = zeros([1])
            vars = dict(flock.c_params().items() + flockstep.c_params().items() + [('distance', distance)])
            headers = ['sampler.h']
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    '*distance = MeanNearestNeighborDistance().compute(flock, ' +
                    flockstep.neighbor_selector.c_init() + ');'])
            c_code.CProgram(vars, code, headers, openmp = False).run()
            return distance[0]
        else:
            return mean([min([flock.distance_between_birds(i, j) for i in range(0, flock.N) if i != j]) for j in range(0, flock.N)])

class NumberOfConnectedComponents(Measure):
    def __call__(self, flock, flockstep, fast = True):
        return len(ConnectedComponents()(flock, flockstep))

class CompactAdjacencyMatrix(Measure):
    def __call__(self, flock, flockstep, fast = True):
        if fast:
            c_size = (flock.N * flock.N + 700) // 8
            matrix = zeros([c_size], dtype = 'uint8')
            vars = dict(flock.c_params().items() + flockstep.c_params().items() + [('matrix', matrix)])
            headers = ['sampler.h']
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    'CompactAdjacencyMatrix().compute(flock, ' +
                    flockstep.neighbor_selector.c_init() + ', (unsigned char *)matrix);'])
            c_code.CProgram(vars, code, headers, openmp = False).run()
            return zlib.compress(pickle.dumps(matrix, 2))
        else:
            raise 'No pure python version'

class ConnectedComponents(Measure):
    def __call__(self, flock, flockstep, fast = True):
        if fast:
            colors = zeros([flock.N], dtype='int')
            vars = dict(flock.c_params().items() + flockstep.c_params().items() + [('colors', colors)])
            headers = ['sampler.h']
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    'ColorComponents().compute(flock, ' +
                    flockstep.neighbor_selector.c_init() + ', colors);'])
            c_code.CProgram(vars, code, headers, openmp = False).run()
            color_set = set(colors)
            components = []
            for color in color_set:
                components.append([i for i in range(0, flock.N) if colors[i] == color])
            return components
        else:
            return networkx.strongly_connected_components(Graph()(flock, flockstep, step, False))


class ListOfEdges(Measure):
    def __call__(self, flock, flockstep, fast = True):
        if fast:
            idx = array([0], dtype='int')
            edgelist = zeros([flock.N * (flock.N - 1), 2], dtype=int) - 1
            vars = dict(flock.c_params().items() + flockstep.c_params().items() + [('idx', idx), ('edgelist', edgelist)])
            headers = ['sampler.h']
            code = '\n'.join([
                    'Flock flock = ' + flock.c_init() + ';',
                    '*idx = ListOfEdges().compute(flock, ' +
                    flockstep.neighbor_selector.c_init() + ', (edge *)edgelist);'])
            c_code.CProgram(vars, code, headers, openmp = False).run()
            return edgelist[0:idx[0]]
        else:
            edgelist = []
            for i in range(0, flock.N):
                neighbor_list = flockstep.neighbor_selector.get_list_of_neighbors(flock, i)
                edgelist += [(i, j) for j in neighbor_list]
            return edgelist

class Graph(Measure):
    def __call__(self, flock, flockstep, fast = True):
        list_of_edges = ListOfEdges()(flock, flockstep, step, fast)
        G = networkx.DiGraph()
        G.add_nodes_from(range(0, flock.N))
        G.add_edges_from(list_of_edges)
        return G

class CenterOfMass(Measure):
    def draw(self, canvas):
        canvas.objs.append(Bird(self(), (255, 255, 255), light_radius = 1, dark_radius = 0))
    def __call__(self, flock, flockstep, fast = True):
        n_divs = 10
        cm_candidates = [array([x, y])
                         for x in arange(0, flock.L, flock.L / n_divs)
                         for y in arange(0, flock.L, flock.L / n_divs)]
        cm_with_value = [(self.value_to_min(flock, cm), cm) for cm in cm_candidates]
        best_cm = min(cm_with_value)[1]
        return self.refine_cm(flock, best_cm)
    def value_to_min(self, flock, cm_candidate):
        center = array([flock.L / 2, flock.L / 2])
        return sum((fmod(flock.x - cm_candidate + center, flock.L) - center)**2)
    def refine_cm(self, flock, cm):
        r = zeros([2])
        for i in range(0, flock.N):
            x0 = flock.x[i][0]
            x1 = x0 + flock.L if x0 < cm[0] else x0 - flock.L
            x1 = x0 if abs(x0 - cm[0]) < abs(x1 - cm[0]) else x1
            y0 = flock.x[i][1]
            y1 = y0 + flock.L if y0 < cm[1] else y0 - flock.L
            y1 = y0 if abs(y0 - cm[1]) < abs(y1 - cm[1]) else y1
            r += array([x1, y1])
        return flock.get_position_in_original_domain(r / flock.N)

class FormPE(Measure):
    def __call__(self, flock, flockstep, fast = True):
        exe = os.path.abspath(os.path.dirname(__file__) + '/../C/bin/alpha.exe')
        hull = subprocess.Popen('', executable = exe, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
        hull.communicate
