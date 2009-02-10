import numpy
import pynearest
numpy.random.seed(0)
for i in range(0, 100):
    print i
    m = 10
    k = 8
    r = 10
    d = 2
    N = 1001
    x = numpy.random.random([N, d])
    ps = pynearest.PointSet(x, d, m, r)
    axis = i % d
    med = ps.find_median(0, N, axis)
    med1 = numpy.median([p[axis] for p in x])
    assert(med == med1)
    k_nearest = sorted([(ps.distance(0, i), i) for i in range(1, N)])[0:k]
    if False:
        h = ps.HashTable(ps, 0, N)
        pk = h.get_k_table_neighbors(0, k)
        h.refine_k_nearest_neighbors(0, k, pk)
        assert([el[1] for el in pk] == [el[1] for el in k_nearest])
    if True:
        print 'create root'
        ps.create_root()
        print 'process tree'
        ps.process_node(ps.root)
        print 'find neighbors'
#        pk = ps.leaf[0].hash.get_k_table_neighbors(0, k)
#        ps.leaf[0].hash.refine_k_nearest_neighbors(0, k, pk)
#        print [ps.s[el[1]] for el in pk]
#        for i in range(0, N):
#            ps.leaf[i].hash.refine_k_nearest_neighbors(0, k, pk)
        pk = ps.find_k_nearest_neighbors(0, k)
        #print [ps.s[el[1]] for el in pk]
        #print [el[1] for el in k_nearest]
        assert([ps.s[el[1]] for el in pk] == [el[1] for el in k_nearest])
        #assert([el[1] for el in pk] == [el[1] for el in k_nearest])

    if False:
        h = ps.HashTable(ps, 0, N/4)
        h1 = ps.HashTable(ps, N/4, N/2)
        h2 = ps.HashTable(ps, N/2, N)
        pk = h.get_k_table_neighbors(0, k)
        h.refine_k_nearest_neighbors(0, k, pk)
        h1.refine_k_nearest_neighbors(0, k, pk)
        h2.refine_k_nearest_neighbors(0, k, pk)
        print [el[1] for el in pk]
        print [el[1] for el in k_nearest]
        assert([ps.s[el[1]] for el in pk] == [el[1] for el in k_nearest])
