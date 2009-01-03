from __future__ import with_statement
from __future__ import division
from scipy import *
import speedflock.vis
import copy
from speedflock.calc.c_code import *

class Sampler(object):
    def __call__(self, flock, flockstep):
        pass

class Flock(Sampler):
    def __call__(self, flock, flockstep):
        return copy.deepcopy(flock)

class Phi(Sampler):
    def __call__(self, flock, flockstep):
        sum_of_velocities = sum(flock.v, 0)
        sum_of_norms = sum(sqrt(sum(flock.v**2, 1)))
        return sum_of_velocities / sum_of_norms

class DistancesSampler(Sampler):
    def __call__(self, flock, flockstep):
        edges = flockstep.neighbor_selector.fast_list_of_edges(flock)
        return [flock.distance_between_birds(i, j) for (i, j) in
    edges]
        

class MinFirstNeighborDistance(Sampler):
    def __call__(self, flock, flockstep):
        distance = zeros([1])
        C = CProgram(flock, values = {'distance': distance})
        C.append('''
double distance_sq = L * 2;
for (int i = 0; i < N; i ++) {
for (int j = i + 1; j < N; j ++) {
double new_distance = distance_between_birds_sq(i, j);
if (new_distance < distance_sq)
distance_sq = new_distance;
}
}
*distance = sqrt(distance_sq);
''')
        C.run()
        return distance[0]

class MaxFirstNeighborDistance(Sampler):
    def __call__(self, flock, flockstep):
        distance = zeros([1])
        C = CProgram(flock, values = {'distance': distance})
        C.append('''
double distance_sq = 0;
for (int i = 0; i < N; i ++) {
double min_distance_sq = L * 2;
for (int j = 0; j < N; j ++) {
double new_distance_sq = distance_between_birds_sq(i, j);
if (i != j && new_distance_sq < min_distance_sq)
min_distance_sq = new_distance_sq;
}
if (min_distance_sq > distance_sq)
distance_sq = min_distance_sq;
}
*distance = sqrt(distance_sq);
''')
        C.run()
        return distance[0]

class NumberOfConnectedComponents(Sampler):
    def __call__(self, flock, flockstep):
        return len(ConnectedComponents()(flock, flockstep))

class ConnectedComponents(Sampler):
    def __call__(self, flock, flockstep):
        component = zeros([flock.N], dtype=int) - 1
        C = CProgram(flock, objects = [flockstep.neighbor_selector],
    values = {'component': component})
        flockstep.neighbor_selector.init_code(C)
        with StructuredBlock(C,
                             '''
for (int i = 0; i < N; i ++) {
component[i] = i;
''',
                             '}'):
            with flockstep.neighbor_selector.code(C):
                C.append('''
if (j < i) {
if(component[j] != -1 && component[j] != i) {
int tochange = component[j];
for (int k = 0; k < N; k ++) {
if (component[k] == tochange)
component[k] = i;
}
}
component[j] = i;
}
''')
        C.run()
        components = []
        for c in set(component):
            components.append([i for i in range(0, flock.N) if component[i] == c])
        return components

class ListOfEdges(Sampler):
    def __call__(self, flock, flockstep):
        idx = array([0], dtype='int')
        edgelist = zeros([flock.N * (flock.N - 1) / 2, 2], dtype=int) - 1
        C = CProgram(flock, objects = [flockstep.neighbor_selector],
                     values = {'edgelist_':edgelist, 'idx':idx})
        C.append('''
typedef int edge[2];
edge * edgelist;
edgelist = (edge*)edgelist_;
''')
        flockstep.neighbor_selector.init_code(C)
        with StructuredBlock(C,
                             '''
for (int i = 0; i < N; i ++) {
''',
                             '}'):
            with flockstep.neighbor_selector.code(C):
                C.append('''
if (i < j) {
edgelist[*idx][0] = i;
edgelist[*idx][1] = j;
(*idx) ++;
}
''')
        C.run()
        return edgelist[0:idx[0]]


class CenterOfMass(Sampler):
    def draw(self, canvas):
        canvas.objs.append(Bird(self(), (255, 255, 255), light_radius = 1, dark_radius = 0))

    def __call__(self, flock, flockstep):
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
        return flock.loop_position(r / flock.N)
    


