from __future__ import with_statement
from __future__ import division

import md5

from scipy import *
import scipy.weave

from . import flockstep
from . import c_code
from . import utility

fast = True

class NeighborSelector(utility.ParametricObject):
    def prepare_neighbors(self, flock):
        """
        Prepare the data structure used to speed up calculations
        of the nearest neighbors.

        Is called before get_list_of_neighbors is used.

        flock is the current flock
        """
        pass

    def get_list_of_neighbors(self, flock, i):
        """
        Return the list of neighbors of bird i, as a list of
        integers indices.
        """
        pass
    def support_code(self, C):
        """
        C code to declare globals
        """
        pass
    def init_code(self, C):
        """
        C code executed once per step.

        Reserved variables are R
        """
        pass

    def code(self):
        """
        Return the C code for the loop on all neighbors.

        i is defined as the current bird, whereas this code must define
        j as the current neighbor in consideration for computation
        of forces
        
        Code must also define :

        r is the distance between the bird i and j
        normrsq is dot(r, r)
        normr is ||r|| = sqrt(dot(r, r))
        """
        pass

class TopologicalDistanceNeighborSelecter(NeighborSelector):
    def __init__(self, k):
        NeighborSelector.__init__(self)
        self.k = k
    def prepare_neighbors(self, flock):
        pass
    def get_list_of_neighbors(self, flock, i):
        pass
    def support_code(self, C):
        C.append(
            '''
PointSet<2> * neighbor_pointset;
const int neighbor_k = %d;
const int neighbor_m = neighbor_k + 2;
const int neighbor_r = 10;
'''  % (self.k))
    def init_code(self, C):
        C.append(
'''
neighbor_pointset = new PointSet<2>(x, N, neighbor_m, neighbor_r);
neighbor_pointset->init();
''')
    def end_code(self, C):
        C.append(
            '''
delete neighbor_pointset;
''')
    def code(self, C):
        return c_code.StructuredBlock(C,
                                      '''
NeighborList * neighborlist =
    neighbor_pointset->getWrapNeighborListInRealOrder(x[i], neighbor_k + 1, L);
neighborlist->sortFinalResults();
NeighborList::const_iterator neighbor_iterator = neighborlist->begin();
++neighbor_iterator; // first element is myself
for (;
     neighbor_iterator != neighborlist->end();
     ++neighbor_iterator) {
int j = neighbor_iterator->second;
vector r;
r[0] = comp_sub(x[i][0], x[j][0]);
r[1] = comp_sub(x[i][1], x[j][1]);
double normrsq = r[0]*r[0] + r[1]*r[1];
double normr = sqrt(normrsq);
''',
                                      '''
}
delete neighborlist;
''')

class MetricDistanceNeighborSelector(NeighborSelector):
    def __init__(self, R):
        NeighborSelector.__init__(self)
        self.R = R

    def prepare_neighbors(self, flock):
        # this code cannot be used in situations where L < R
        # because of problems with handling boundaries
        # and having several times the same neighbor
        assert(flock.L >= self.R)
        pass

    def get_list_of_neighbors(self, flock, i):
        l = []
        for j in range(0, flock.N):
            if i != j and flock.distance_between_birds(i, j) <= self.R:
                l.append(j)
        return l
    def support_code(self, C):
        VicsekNeighborSelector(self.R).support_code(C)
    def init_code(self, C):
        VicsekNeighborSelector(self.R).init_code(C)
    def end_code(self, C):
        VicsekNeighborSelector(self.R).end_code(C)
    def code(self, C):
        vns_code = VicsekNeighborSelector(self.R).code(None)
        return c_code.StructuredBlock(C,
                                      vns_code.enter_code + '''
if (i != j && normrsq <= neighbor_R*neighbor_R) {
''',
                                      '}' + vns_code.exit_code)

class VicsekNeighborSelector(NeighborSelector):
    #   +-----#-----+-----+-----+---#-+-----+      --- y = -R = L - R
    #   |     #     |     |     |   # |     |
    #   |     #     |     |     |   # |     |
    #   #####################################   +  --- y = 0
    #   |     #     |     |     |   # |     |   |
    #   |     # x   |     |     |   # x     |   |
    #   +-----#-----+-----+-----+---#-+-----+   |
    #   |     #     |  x  | x   |   # |     |   |
    #   |x    #     |    x|    x|   # |     |   |
    #   +-----#-----+-----+-----+---#-+-----+   |  L
    #   |     #     |  x  | x   |   # |     |   |
    #   |     #     |     |     |   # |     |   |
    #   +-----#-----+-----+-----+---#-+-----+   |
    #   |     #   x |     |     |   # |     |   |
    #   #####################################   +  --- y = L
    #   +-----#-----+-----+-----+---#-+-----+      --- y = M * R = M * R - L
    #   |     # x   |     |     |   # |     |
    #   |     #     |     |     |   # |     |
    #   +-----#-----+--x--+-x---+---#-+-----+      --- y = (M + 1) * R = (M + 1) * R - L
    #
    #
    #         +---------------------+
    #                                 +-----+
    #                    L               R
    #
    #         +-----------------------+
    #
    #             M blocks of length M * R
    def __init__(self, R):
        self.R = R
        NeighborSelector.__init__(self)

    def block_coord(self, x):
        return int(x / self.R) + 1
    def support_code(self, C):
        C.append(
            '''
BlockPointSet<2> * neighbor_pointset;
const double neighbor_R = %f;
''' % (self.R))
    def init_code(self, C):
        C.append(
            '''
neighbor_pointset = new BlockPointSet<2>(x, N, neighbor_R, L);
''')
    def end_code(self, C):
        C.append(
            '''
delete neighbor_pointset;
''')
    def code(self, C):
        return c_code.StructuredBlock(C,
                                      '''
int b_i[2], b[2];
neighbor_pointset->getBlockIndex(x[i], b_i);
for (b[0] = b_i[0] - 1; b[0] < b_i[0] + 2; b[0] ++) {
for (b[1] = b_i[1] - 1; b[1] < b_i[1] + 2; b[1] ++) {
BlockPointSet<2>::BlockList * blocklist = neighbor_pointset->get(b);
BlockPointSet<2>::BlockList::const_iterator it = blocklist->begin();
for (; it != blocklist->end(); ++it) {
int j = *it;
if (b[0] != b_i[0] || b[1] != b_i[1] || j != i) {
vector r;
r[0] = comp_sub(x[i][0], x[j][0]);
r[1] = comp_sub(x[i][1], x[j][1]);
double normrsq = r[0]*r[0] + r[1]*r[1];
double normr = sqrt(normrsq);
''',
                                      '''
}
}
}
}
''')

    def prepare_neighbors(self, flock):
        pass

    def get_list_of_neighbors(self, flock, i):
        block_x = self.block_coord(flock.x[i][0])
        block_y = self.block_coord(flock.x[i][1])
        l = []
        bx = range(block_x - 1, block_x + 2)
        by = range(block_y - 1, block_y + 2)
        for j in range(0, flock.N):
            for dx in [-flock.L, 0, flock.L]:
                for dy in [-flock.L, 0, flock.L]:
                    if (self.block_coord(flock.x[j][0] + dx) in bx and
                        self.block_coord(flock.x[j][1] + dy) in by):
                        if dx != 0 or dy != 0 or i != j:
                            l.append(j)
