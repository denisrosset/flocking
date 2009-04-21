from __future__ import with_statement
import scipy
import numpy
class ParametricObject(object):
    def c_type(self):
        return self.__class__.__name__
    """ An object used in the calculations. Defines a get_parameters
    method that is used to return the relevant simulation parameters
    from the class for analysis. """
    parameters = None
    def get_parameters(self):
        """ Returns a dict of parameters, with key begin the
        classname_membervariable and value the current value of the
        relevant variable """
        d = {}
        classname = self.__class__.__name__
        keys = (self.parameters if self.parameters is not None 
                else self.__dict__.keys())
        for key in keys:
            value = self.__dict__[key]
            if any([isinstance(value, t) for t in [int, float, str]]):
                d[classname + '_' + key] = value
            if isinstance(value, ParametricObject) and not self.__class__.__name__ == 'EvolutionFlockInitializer':
                d.update(value.get_parameters())
        return d
    def c_init(self):
        """ Returns a C++ call to constructor, to construct this object """
        def expr(key, value):
            if isinstance(value, ParametricObject):
                return value.c_init()
            else:
                return self.__class__.__name__ + '_' + key
        s = self.c_type() + '(' + ','.join(
            [expr(key, self.__dict__[key]) for key in self.parameters]) + ')'
        return s
    def c_params(self):
        return self.get_parameters()

##
# encapsulates state for the scipy generator
# usage :
# 
class RandomState(object):
    """ Encapsulate state for the scipy random generator.
    Can be serialized. Not thread-safe. Backups and restores the scipy.random
    state between uses.

    Specifying a 
    >>> from __future__ import with_statement
    >>> import scipy
    >>> r = RandomState(1234)
    >>> with r:
    ...  scipy.random.randint(10)
    ...  scipy.random.randint(10)
    ... 
    3
    6
    >>> r = RandomState(1234)
    >>> 
    """

    def __init__(self, seed = None):
        """
        Construct a RandomState object.
        
        First argument can be a integer or array seed, as used on
        scipy.random.seed(...)

        >>> r = RandomState()
        ...
        >>> r = RandomState(1234)
        ...
        """
        self.seed(seed)

    def seed(self, seed):
        self._backup_scipy_random()
        scipy.random.seed(seed)
        self._release_scipy_random()


    # not thread safe
    def _backup_scipy_random(self):
        self._backup_state = scipy.random.get_state()
        
    def _restore_scipy_random(self):
        scipy.random.set_state(self._backup_state)
        self._backup_state = None

    def _acquire_scipy_random(self):
        self._backup_scipy_random()
        scipy.random.set_state(self._state)
        self._state = None

    def _release_scipy_random(self):
        self._state = scipy.random.get_state()
        self._restore_scipy_random()

    def __enter__(self):
        self._acquire_scipy_random()
        return scipy.random

    def __exit__(self, type, value, traceback):
        self._release_scipy_random()

