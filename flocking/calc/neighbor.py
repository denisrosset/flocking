from __future__ import with_statement
from __future__ import division

import md5

from scipy import *

from . import flockstep
from . import utility

class NeighborSelector(utility.ParametricObject):
    def update(self, flock,
               force_evaluators):
        for i in range(0, flock.N):
            temp = zeros([len(force_evaluators), 2])
            Nn = 0
            for e in range(0, len(force_evaluators)):
                force_evaluators[e].start(flock, i, temp[e])
            l = self.get_list_of_neighbors(flock, i)
            for j in l:
                r = flock.get_vector_difference(flock.x[i], flock.x[j])
                normrsq = r[0]*r[0] + r[1]*r[1]
                normr = linalg.norm(r)
                for e in range(0, len(force_evaluators)):
                    force_evaluators[e].update(
                        flock, i, j, normr, normrsq, temp[e], Nn)
                Nn += 1
            for e in range(0, len(force_evaluators)):
                force_evaluators[e].end(flock, i, temp[e], Nn)
    def get_list_of_neighbors(self, flock, i):
        """
        Return the list of neighbors of bird i, as a list of
        integers indices.
        """
        pass

class TopologicalDistanceNeighborSelector(NeighborSelector):
    def __init__(self, k):
        NeighborSelector.__init__(self)
        self.parameters = ['k']
        self.k = k
    def get_list_of_neighbors(self, flock, i):
        return sorted([(j, flock.distance_between_birds(i, j))
                       for j in range(0, flock.N) if i != j])[0:self.k]

class TopologicalDistanceCutoffNeighborSelector(NeighborSelector):
    def __init__(self, k, R):
        NeighborSelector.__init__(self)
        self.parameters = ['k', 'R']
        self.k = k
        self.R = R
    def get_list_of_neighbors(self, flock, i):
        l = [(j, flock.distance_between_birds(i, j))
             for j in range(0, flock.N) if i != j]
        return sorted([(j, d) for (j, d) in l if d <= self.R][0:self.k])

class MetricDistanceNeighborSelector(NeighborSelector):
    def __init__(self, R):
        NeighborSelector.__init__(self)
        self.parameters = ['R']
        self.R = R

    def get_list_of_neighbors(self, flock, i):
        assert(flock.L >= self.R)
        return [j for j in range(0, flock.N) if i != j and
                flock.distance_between_birds(i, j) <= R]

class BlockMetricDistanceNeighborSelector(NeighborSelector):
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
        self.parameters = ['R']
        NeighborSelector.__init__(self)

    def get_list_of_neighbors(self, flock, i):
        def block_coord(self, x):
            return int(x / self.R) + 1
        block_x = block_coord(flock.x[i][0])
        block_y = block_coord(flock.x[i][1])
        l = []
        bx = range(block_x - 1, block_x + 2)
        by = range(block_y - 1, block_y + 2)
        for j in range(0, flock.N):
            for dx in [-flock.L, 0, flock.L]:
                for dy in [-flock.L, 0, flock.L]:
                    if (self.block_coord(flock.x[j][0] + dx) in bx and
                        self.block_coord(flock.x[j][1] + dy) in by):
                        if i != j:
                            l.append(j)
        return l
