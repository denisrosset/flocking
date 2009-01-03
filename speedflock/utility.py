from __future__ import with_statement
import scipy


class ComputationObject(object):
    def __init__(self):
        self.fast = True

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

