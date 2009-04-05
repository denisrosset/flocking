import numpy
import numpy.linalg        

class PointSet:
    ''' Implement efficient nearest-neighbor queries on a
    k-dimensional point set, as per
    M. Vanco and G. Brunnett and Th. Schreiber,
    "A Hashing Strategy for Efficient k -Nearest Neighbors
    Computation"
    '''
    class HashTable:
        def __init__(self, pointset, start, end):
            self.pointset = pointset
            self.size = (end - start)
            self.table = -numpy.ones(self.size, dtype = 'int')
            def calculate_min_max():
                self.minsum = numpy.inf
                self.maxsum = -numpy.inf
                for i in range(start, end):
                    coordsum = sum(pointset.get(i))
                    self.minsum = min(self.minsum, coordsum)
                    self.maxsum = max(self.maxsum, coordsum)
            calculate_min_max()
            self.key = (self.size - 1) / (self.maxsum - self.minsum)
            def add_point(i):
                index = self.index(pointset.get(i))
                self.pointset.next[i] = self.table[index]
                self.table[index] = i
            for i in range(start, end):
                add_point(i)
        def index(self, pt):
            return int((sum(pt) - self.minsum) * self.key)
        def get_k_table_neighbors(self, i, k):
            ''' Get the k elements at the left and right of i in the
            table. '''
            pk = []
            hash_i = self.index(self.pointset.get(i))
            def add_index_to_pk(table_i):
                pt_i = self.table[table_i]
                while pt_i != -1 and len(pk) < k:
                    if pt_i != i:
                        pk.append(pt_i)
                    pt_i = self.pointset.next[pt_i]
            add_index_to_pk(hash_i)
            for j in range(1, self.size):
                if hash_i + j < self.size:
                    add_index_to_pk(hash_i + j)
                if hash_i - j >= 0:
                    add_index_to_pk(hash_i - j)
            assert(len(pk) == k)
            return sorted([(self.pointset.distance(i, j), j) for j in pk])
        def refine_k_nearest_neighbors(self, i, k, pk):
            ''' Takes a list of neighbors of point of index i in
            increasing distance order, and updates the list with
            candidates from the current hashtable. '''
            d = pk[-1][0]
            sumpt = sum(self.pointset.get(i))
            dimfact = numpy.sqrt(self.pointset.dim)
            start = int(
                (sumpt - self.minsum - dimfact * d) * self.key)
            end = int(numpy.ceil(
                    (sumpt - self.minsum + dimfact * d) * self.key)) + 1
            start = max(0, start)
            end = min(self.size, end)
            def add_in_sorted_pk(pt_i):
                ''' Add the selected point pt_i in place in the pk
                array, preserving the order on the list. '''
                if pt_i in [el[1] for el in pk]:
                    return
                dist = self.pointset.distance(pt_i, i)
                place = 0
                for place in range(0, k):
                    if pk[place][0] > dist:
                        break
                for l in reversed(range(place, len(pk) - 1)):
                    pk[l + 1] = pk[l]
                pk[place] = (dist, pt_i)
            for j in range(start, end):
                pt_i = self.table[j]
                while pt_i != -1:
                    dist = self.pointset.distance(pt_i, i)
                    if dist < pk[-1][0] and pt_i != i:
                        add_in_sorted_pk(pt_i)
                    pt_i = self.pointset.next[pt_i]

    class Node:
        def __init__(self):
            self.left = None
            self.right = None
            self.median = None
            self.hash = None
            self.final = None
            self.start = -1
            self.end = -1
            self.bbox = None
            self.axis = -1
        def size(self):
            return self.end - self.start
    def find_k_nearest_neighbors(self, i, k):
        i = list(self.s).index(i)
        pk = self.leaf[i].hash.get_k_table_neighbors(i, k)
        self.leaf[i].hash.refine_k_nearest_neighbors(i, k, pk)
        def search_tree(node):
            def bounding_box_intersect(b1, b2):
                def interval_intersect(i1, i2):
                    return (i1[0] <= i2[0] <= i1[1]) or \
                        (i2[0] <= i1[0] <= i2[1])
                return all([interval_intersect(b1[a], b2[a]) for a in
                            range(0, self.dim)])
            def bounding_box_of_sphere():
                d = pk[-1][0]
                x = self.get(i)
                bbox = [(x[a] - d, x[a] + d) for a in range(0,
                                                            self.dim)]
                return bbox
            if node.hash is not None:
                node.hash.refine_k_nearest_neighbors(i, k, pk)
            else:
                for child in [node.left, node.right]:
                    if bounding_box_intersect(child.bbox,
                                              bounding_box_of_sphere()):
                        search_tree(child)
        search_tree(self.root)
        return pk
    def distance(self, i, j):
        return numpy.linalg.norm(self.get(i) - self.get(j))
    def create_root(self):
        self.root = self.Node()
        self.root.start = 0
        self.root.end = self.N
        self.root.bbox = [self.find_min_max(self.root.start, self.root.end, axis)
                          for axis in range(0, self.dim)]
        self.root.axis = 0
    def process_node(self, node):
        def split_bbox_around_median(bbox, median, axis):
            ''' Split the bounding box bbox around the median on
            the specified axis '''
            left = list(bbox)
            right = list(bbox)
            left[axis] = (left[axis][0], median)
            right[axis] = (median, right[axis][1])
            return (left, right)
        if node.size() >= 2 * self.m:
            node.median = self.find_median(node.start, node.end, node.axis)
            self.place_around_medians(node.median, node.start, node.end, node.axis)
            median_i = int((node.start + node.end) / 2)
            node.final = False
            node.left = self.Node()
            node.right = self.Node()
            (node.left.start, node.left.end) = (node.start, median_i)
            (node.right.start, node.right.end) = (median_i, node.end)
            (node.left.bbox, node.right.bbox) = \
                split_bbox_around_median(node.bbox, node.median, node.axis)
            node.left.axis = (node.axis + 1) % self.dim
            node.right.axis = (node.axis + 1) % self.dim
            self.process_node(node.left)
            self.process_node(node.right)
        else:
            node.final = True
            node.hash = self.HashTable(self, node.start, node.end)
            for i in range(node.start, node.end):
                self.leaf[i] = node
    def get(self, i):
        return self.x[self.s[i]]
    def swap(self, i, j):
        (self.s[i], self.s[j]) = (self.s[j], self.s[i])
    def number_of_points_left_median_right(self, median, start, end, axis):
        ''' Count the elements to the left and the right of the medians.
        Returns a tuple (left, middle, right), where left is the number
        of elements to the left of the median, right is the number of elements
        to the right of the median, and middle is the number of median elements '''
        left = 0
        middle = 0
        right = 0
        for i in range(start, end):
            x = self.get(i)[axis]
            if x < median:
                left += 1
            if x == median:
                middle += 1
            if x > median:
                right += 1
        return (left, middle, right)
    def place_around_medians(self, median, start, end, axis):
        ''' Sort the elements between [start, end[ around the medians '''
        (left, middle, right) = self.number_of_points_left_median_right(
            median, start, end, axis)
        def place_medians():
            median_i = start + left
            for i in range(start, start + left) + range(start + left +
                                                        middle, end):
                x = self.get(i)[axis]
                if x == median:
                    while self.get(median_i)[axis] == median:
                        median_i += 1
                    self.swap(i, median_i)
        def place_left_right_elements():
            left_i = start
            right_i = start + left + middle
            while left_i < start + left:
                if self.get(left_i)[axis] > median:
                    while self.get(right_i)[axis] > median:
                        right_i += 1
                    self.swap(left_i, right_i)
                left_i += 1
        place_medians()
        place_left_right_elements()
    def find_min_max(self, start, end, axis):
        ''' Calculate minimum and maximum values around specified axis for
        the selected range in the specified point set.
        
        Returns (h_min, h_max) as a tuple.
        
        Arguments :
        point_set -- the point set on which the calculations are
        made
        (start, end) -- range of points on which to act (end is
        not included)
        axis -- the axis on which to act
        '''
        h_min = +numpy.inf
        h_max = -numpy.inf
        for i in range(start, end):
            x = self.get(i)[axis]
            h_min = min(h_min, x)
            h_max = max(h_max, x)
        return (h_min, h_max)

    def find_median(self, start, end, axis):
        def interval(x, h_min, h_max):
            ''' Returns the index of the interval where x resides.
            
            [h_min; h_max] is subdivided in r intervals, where
            h_min = x0 <= x < x1 if x is in the interval 0
                    x1 <= x < x2 if x is in the interval 1
                    ...
                x{r-1} <= x <= xr = h_max if x is in the interval r-1
                
                x0, x1, ... xr are equidistant points
            '''
            return min(int((x - h_min) / (h_max - h_min) * self.r), self.r - 1)
        def interval_left(i, h_min, h_max):
            ''' Return the left limit of the ith interval '''
            return i * (h_max - h_min) / self.r + h_min
        def interval_right(i, h_min, h_max):
            ''' Return the right limit of the ith interval '''
            return interval_left(i + 1, h_min, h_max)
        def x_in_interval(x, i, h_min, h_max):
            ''' Test if the point x is in the ith interval '''
            if (i == 0 and x == h_min) or (i == self.r - 1 and x == h_max):
                return True
            return (x >= interval_left(i, h_min, h_max) and
                    x < interval_right(i, h_min, h_max))
        (h_min, h_max) = self.find_min_max(start, end, axis)
        # calculate histogram
        histo = numpy.zeros(self.r, dtype = 'int')
        for i in range(start, end):
            x = self.get(i)[axis]
            histo[interval(x, h_min, h_max)] += 1

        median_index = int((end - start) / 2)
        # find interval on which the median resides
        total = 0
        for i in range(0, self.r):
            if total + histo[i] > median_index:
                break
            total += histo[i]
        histo_i = i
        # find the median inside the interval
        list_of_points = []
        for i in range(start, end):
            x = self.get(i)[axis]
            if x_in_interval(x, histo_i, h_min, h_max):
                list_of_points.append(x)
        list_of_points = sorted(list_of_points)
        median_x = list_of_points[median_index - total]
        return median_x
    def __init__(self, x, dim, m, r):
        self.x = x
        self.N = numpy.size(x, 0)
        self.s = numpy.array(range(0, self.N))
        self.next = -numpy.ones(self.N, dtype = 'int')
        self.leaf = [None for i in range(0, self.N)]
        self.dim = dim
        self.m = m
        self.r = r
