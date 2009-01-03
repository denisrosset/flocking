from __future__ import with_statement
from __future__ import division
from scipy import *
import scipy.weave
import md5
from speedflock.utility import *
from speedflock.calc.flockstep import *
from speedflock.calc.c_code import *

class NeighborSelector(ComputationObject):
    def __init__(self):
        ComputationObject.__init__(self)
        
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

    def init_code(self, C):
        """
        C code executed once per step.

        Reserved variables are M, R, ll_*, block_pointer.
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

    def init_code(self, C):
        if self.fast:
            VicsekNeighborSelector(self.R).init_code(C)

    def code(self, C):
        if self.fast:
            vns_code = VicsekNeighborSelector(self.R).code(None)
            return StructuredBlock(C,
                                   vns_code.enter_code + '''
if (i != j && normrsq <= R*R) {
''',
                                   '}' + vns_code.exit_code)
        return StructuredBlock(C,
                               '''
for (int j = 0; j < N; j ++) {
vector r;
r[0] = comp_sub(x[i][0], x[j][0]);
r[1] = comp_sub(x[i][1], x[j][1]);
double normrsq = r[0]*r[0] + r[1]*r[1];
double normr = sqrt(normrsq);
const double R = %f;

if (i != j && (r[0]*r[0] + r[1]*r[1] <= R*R)) {
''' % self.R,
                               '}}')

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

        # linked list structure
        self.ll_max_size = -1
        self.ll_element = None
        self.ll_next = None
        self.ll_free_element = -1

        self.block_pointer = None
        self.number_of_side_blocks = -1

        self.M = -1
        NeighborSelector.__init__(self)

    def block_coord(self, x):
        return int(x / self.R) + 1

    def init_code(self, C):
        C.append(
'''
const double R = %f;
const int ll_max_size = N * 9;
const int M = ceil(L / R);
int ll_element[ll_max_size], ll_next[ll_max_size], ll_free_element = 0;
int block_pointer[M + 2][M + 2];
for (int i = 0; i < M + 2; i ++) {
for (int j = 0; j < M + 2; j ++) {
block_pointer[i][j] = -1;
}
}
for(int i = 0; i < N; i ++) {
double cx = x[i][0];
double cy = x[i][1];
// for normal x

for (int ix = -1; ix != 2; ix ++) {
for (int iy = -1; iy != 2; iy ++) {

int bx = int((cx + ix * L) / R) + 1;
int by = int((cy + iy * L) / R) + 1;

if (bx >= 0 && bx < M + 2 && by >= 0 && by < M + 2) {
ll_next[ll_free_element] = block_pointer[bx][by];
ll_element[ll_free_element] = i;
block_pointer[bx][by] = ll_free_element;
ll_free_element ++;
}

}
}

}

''' % (self.R))

    def code(self, C):
        return StructuredBlock(C,
                               '''
int block_x = int(x[i][0]/R) + 1, block_y = int(x[i][1]/R) + 1;
for (int bx = block_x - 1; bx < block_x + 2; bx ++) {
for (int by = block_y - 1; by < block_y + 2; by ++) {
int list_index = block_pointer[bx][by];
int start_index = list_index;
while (list_index != -1) {
int j = ll_element[list_index];
if (bx != block_x || by != block_y || j != i) {
vector r;
r[0] = comp_sub(x[i][0], x[j][0]);
r[1] = comp_sub(x[i][1], x[j][1]);
double normrsq = r[0]*r[0] + r[1]*r[1];
double normr = sqrt(normrsq);
''',
                               '''
}
list_index = ll_next[list_index];
}
}
}
''')

    def prepare_neighbors(self, flock):
        # number of blocks to cover the flock space
        self.M = int(ceil(flock.L / self.R))

        # linked list
        self.ll_max_size = flock.N * 9
        self.ll_element = zeros([self.ll_max_size], dtype = int) - 1
        self.ll_next = zeros([self.ll_max_size], dtype = int) - 1
        self.ll_free_element = 0

        self.block_pointer = zeros([self.M + 2, self.M + 2], dtype = int) - 1

        def add_to_block(block_x, block_y, bird_index):
            self.ll_next[self.ll_free_element] = self.block_pointer[block_x][block_y]
            self.ll_element[self.ll_free_element] = bird_index

            self.block_pointer[block_x][block_y] = self.ll_free_element
            self.ll_free_element += 1

        for i in range(0, flock.N):
            # to simplify notation
            L = flock.L
            M = self.M
            R = self.R

            cx = flock.x[i][0]
            cy = flock.x[i][1]

            def add_bird_to_relevant_block(x, y, bird_index):
                bx = int(x / R) + 1
                by = int(y / R) + 1
                if bx >= 0 and bx < M + 2 and by >= 0 and by < M + 2:
                    add_to_block(bx, by, bird_index)
            [add_bird_to_relevant_block(cx + ix, cy + iy, i) for ix in [-L, 0, L] for iy in [-L, 0, L]]

    def get_list_of_neighbors(self, flock, i):
        block_x = self.block_coord(flock.x[i][0])
        block_y = self.block_coord(flock.x[i][1])
        l = []

        for bx in range(block_x - 1, block_x + 2):
            for by in range(block_y - 1, block_y + 2):
                list_index = self.block_pointer[bx][by]
                while list_index != -1:
                    bird_index = self.ll_element[list_index]
                    # bird can be its own neighbor if its shadow copy is in a neighboring block
                    if bx != block_x or by != block_y or i != bird_index:
                        l.append(bird_index)
                    list_index = self.ll_next[list_index]
        return l
