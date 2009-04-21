from sets import ImmutableSet # TODO: use builtin frozenset
from scipy import *
import pylab
from ..calc import c_code
import cPickle as pickle
import zlib
class ImmutableDict(dict):
    '''
    A hashable dict.
    
    >>> a=[ImmutableDict([('one',1),('three',3)]),ImmutableDict([('two',2),('four' ,4)])]
    >>> b=[ImmutableDict([('two',2),('four' ,4)]),ImmutableDict([('one',1),('three',3)])]
    >>> a.sort(key=lambda d:hash(d))
    >>> b.sort(key=lambda d:hash(d))
    >>> a == b
    True
    
    '''
    def __init__(self,*args,**kwds):
        dict.__init__(self,*args,**kwds)
        self._items=list(self.iteritems())
        self._items.sort()
        self._items=tuple(self._items)
    def __setitem__(self,key,value):
        raise NotImplementedError, "dict is immutable"
    def __delitem__(self,key):
        raise NotImplementedError, "dict is immutable"
    def clear(self):
        raise NotImplementedError, "dict is immutable"
    def setdefault(self,k,default=None):
        raise NotImplementedError, "dict is immutable"
    def popitem(self):
        raise NotImplementedError, "dict is immutable"
    def update(self,other):
        raise NotImplementedError, "dict is immutable"
    def __hash__(self):
        return hash(self._items)


class SplitPlotter:
    ''' Implements a class to plot simulations with some classification'''
    @classmethod
    def get_x_y_from_dict(cls, d):
        x = array(sorted(d.keys()))
        y = zeros(len(d))
        for i in range(0, len(d)):
            y[i] = d[x[i]]
        return (x, y)
    def __init__(self,
                 batch,
                 p_vars = None,
                 s_vars = [],
                 c_vars = ['FlockSeed_seed'],
                 filter = lambda x: True,
                 map_function = lambda x: x,
                 init_function = None,
                 plot_function = None,
                 save_function = None
                 ):
        self.batch = batch
        self.p_vars = set(p_vars) if p_vars is not None else None
        self.s_vars = set(s_vars) if s_vars is not None else None
        self.c_vars = set(c_vars)
        self.filter = filter
        def default_init_function():
            pylab.hold(False)
            pylab.close('all')
            pylab.clf()
            pylab.hold(True)
        def default_plot_function(sims, keys_for_serie):
            list_of_samples = [sim.samples['phi'] for sim in sims]
            dmean = dict([
                    (t, mean([sample[t] for sample in list_of_samples]))
                    for t in list_of_samples[0].keys()])
            (x, ymean) = self.get_x_y_from_dict(dmean)
            pylab.plot(x, ymean, label = '')
        def default_save_function():
            pylab.legend(loc = 'best')
            pylab.show()
        self.map_function = map_function
        self.init_function = init_function if init_function else default_init_function
        self.plot_function = plot_function if plot_function else default_plot_function
        self.save_function = save_function if save_function else default_save_function
    def relevant_vars(self, tuple_of_sim_vars, ignore_vars):
        def filter_dict_of_vars(d):
            return ImmutableDict([
                (k, v) for (k, v) in d.items()
                if k not in ignore_vars])
        list_of_dicts = [filter_dict_of_vars(vars)
                         for (sim, vars) in tuple_of_sim_vars]
        vars = set()
        [vars.update(d.keys()) for d in list_of_dicts]
        return [v for v in vars if
                len(set([(d[v] if d.has_key(v) else None)
                         for d in list_of_dicts])) > 1]

    def filter_by(self, tuples_of_sim_var, filter_vars):
        def filter_dict_of_vars(d):
            return ImmutableDict([
                (k, v) for (k, v) in d.items()
                if k in filter_vars])
        buckets = ImmutableSet([filter_dict_of_vars(vars)
                       for (sim, vars) in tuples_of_sim_var])
        list_of_tuples = dict([(bucket, []) for bucket in buckets])
        for (sim, vars) in tuples_of_sim_var:
            bucket = filter_dict_of_vars(vars)
            list_of_tuples[bucket].append((sim, vars))
        return list_of_tuples
            
    def plot(self):
        self.init_function()
        def values_for_sim(sim):
            return ImmutableDict(
                [(key, value) 
                 for (key, value) in sim.get_parameters().items()
                 if not key in self.c_vars])
        sims = [(sim, values_for_sim(sim)) for sim in self.batch.seeds.values()]
        res_vars = self.relevant_vars(
            sims,
            (self.p_vars if self.p_vars is not None else set()) |
            (self.s_vars if self.s_vars is not None else set()) |
            self.c_vars)
        if len(res_vars) > 0 and self.s_vars is not None and self.p_vars is not None:
            raise Exception
        if self.s_vars is None:
            self.s_vars = res_vars
            res_vars = []
        if self.p_vars is None:
            self.p_vars = res_vars
            res_vars = []
        plots = self.filter_by(sims, self.p_vars)
        for (key_p, plot_plots) in plots.items():
            pylab.title(str(key_p))
            series = self.filter_by(plot_plots, self.s_vars)
            for key_s in sorted(series.keys()):
                serie_plots = series[key_s]
                loaded_plots = []
                for (sim, vars) in serie_plots:
                    if self.filter(sim):
                        loaded_plots.append(self.map_function(self.batch[sim.hash_key]))
                        self.batch.release_memory()
                if len(loaded_plots) > 0:
                    self.plot_function(loaded_plots, key_s)
            self.save_function(key_p)

import random

class InteractionTime:
    def __call__(self, gzipped_adjancency_matrices, average_on = 100, max_delta = None):
        times = sorted(gzipped_adjancency_matrices.keys())
        period = times[1] - times[0]
        if max_delta is None: 
            max_delta = len(times) - average_on + 1
        usable_times = [time for time in times if time < max(times) - max_delta * period]
        used_times = usable_times
        random.shuffle(used_times)
        used_times = used_times[0:average_on]
        values = {}
        for delta in range(0, max_delta):
            values[delta] = 0.0
        for t in used_times:
            current = pickle.loads(zlib.decompress(gzipped_adjancency_matrices[t]))
            for delta in range(0, max_delta):
                future = pickle.loads(zlib.decompress(gzipped_adjancency_matrices[t + period * delta]))
                N = len(current)
                result = zeros([1])
                headers = ['analysis.h']
                vars = {'current': current, 'future': future, 'N': N, 'result': result}
                code = 'InteractionTime().compute(current, future, N, result);'
                c_code.CProgram(vars, code, headers, openmp = False).run()
                values[delta] += result[0]
        for delta in range(0, max_delta):
            values[delta] *= period / average_on
        return values
