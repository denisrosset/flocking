from sets import ImmutableSet
from scipy import *
import pylab
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
    def get_x_y_from_dict(cls, d):
        x = array(sorted(d.keys()))
        y = zeros(len(d))
        for i in range(0, len(d)):
            y[i] = d[x[i]]
        return (x, y)
    get_x_y_from_dict = classmethod(get_x_y_from_dict)
    def __init__(self,
                 batch,
                 p_vars = None,
                 s_vars = [],
                 c_vars = ['Flock_seed'],
                 filters = [],
                 init_function = None,
                 plot_function = None,
                 save_function = None
                 ):
        
        self.batch = batch
        self.p_vars = set(p_vars) if p_vars is not None else None
        self.s_vars = set(s_vars) if s_vars is not None else None
        self.c_vars = set(c_vars)
        self.filters = set(filters)
        def default_init_function():
            pylab.clf()
            pylab.hold(True)
        def default_plot_function(sims, keys_for_serie):
            list_of_samples = [sim.samples['phi'] for sim in sims]
            dmean = dict([
                    (t, mean([sample[t] for sample in list_of_samples]))
                    for t in list_of_samples[0].keys()])
            (x, ymean) = self.get_x_y_from_dict(dmean)
            pylab.plot(x, ymean, label = ''])
        def default_save_function():
            pylab.legend(loc = 'best')
            pylab.show()
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
            series = self.filter_by(plot_plots, self.s_vars)
            for key_s in sorted(series.keys()):
                serie_plots = series[key_s]
#            for (key_s, serie_plots) in series.items():
                loaded_plots = []
                for (sim, vars) in serie_plots:
                    self.batch.load_sim(sim.hash_key)
                    loaded_plots.append(self.batch.sims[sim.hash_key])
                self.plot_function(loaded_plots, key_s)
            self.save_function(key_p)
