import copy
import cPickle as pickle
import md5
import multiprocessing
import multiprocessing.managers
import os.path
import Queue
import time

from ..externals import S3

class Sim(object):
    ###
    # Initalize the Sim object with the flock and flockstep object given.
    # No copies are being made, the flock object given will be
    # modified by the stepping.
    def __init__(self, flock, flockstep, n_steps, samplers = {},
                 hash_key = None):
        self.samplers = samplers
        self.samples = {}
        for name in self.samplers.keys():
            self.samples[name] = {}
        self.start_flock = copy.deepcopy(flock)
        self.flock = flock
        self.flockstep = flockstep
        if hash_key is None:
            self.hash_key = self.create_hash()
        else:
            self.hash_key = hash_key
        self.step = 0
        self.n_steps = n_steps
        self.sample()
    ###
    # Do a sampling for all the samplers that need to be evaluated for
    # the current step.
    def sample(self):
        for (name, sampler) in self.samplers.items():
            if self.step % sampler[1] == 0:
                self.samples[name][self.step] = sampler[0](self.flock, self.flockstep)
    ###
    # Step for the number of steps supplied.
    def one_step(self):
        self.flockstep.c_step(self.flock)
        self.step += 1
        self.sample()

    def complete_simulation(self):
        '''Complete the simulation, by walking all the steps from the
        current step to the number of steps desired n_steps.'''
        while self.step < self.n_steps:
            self.one_step()
    def finished(self):
        return self.step >= self.n_steps
    def advance_simulation(self, stop_after_secs = 9999999999,
                           stop_after_steps = 9999999999):
        '''Completes the current simulation. Returns if the simulation
        is complete, if the specified timeout occurs (in secs or
        steps).

        Returns True if the simulation is finished'''
        this_adv_step = 0
        start_time = time.time()
        while (self.step < self.n_steps and 
               this_adv_step < stop_after_steps and 
               time.time() - start_time < stop_after_secs):
            self.one_step()
            this_adv_step += 1

    def create_hash(self):
        return md5.md5(pickle.dumps(
                (self.start_flock, self.flockstep))).hexdigest()
    def get_seed(self):
        return Sim(self.start_flock, self.flockstep,
        self.n_steps, self.samplers, self.hash_key)

class Batch(object):
    def __init__(self, sim_list = [], folder = None):
        self.sims = dict([(sim.hash_key, sim) for sim in sim_list])
        self.seeds = dict([(sim.hash_key, sim.get_seed()) for sim in
                           sim_list])
        self.keys = list(self.seeds.keys())
        self.folder = folder
        if self.folder:
            self.folder.save_seeds(self.seeds)
            for sim in self.sims.values():
                self.folder.save(sim)
    def load_sim(self, key):
        self.sims[key] = self.folder.load(key)
    def save_sim(self, key):
        self.folder.save(self.sims[key])
    def load_from_folder(cls, folder):
        seeds = folder.load_seeds().values()
        batch = Batch(seeds, folder)
        return batch
    load_from_folder = classmethod(load_from_folder)

class Processing(object):
    def process(self, batch):
        '''
        Process a whole batch of simulations.
        '''
        pass
class SerialProcessing(object):
    def __init__(self, timeout = 120):
        self.timeout = timeout
    def process(self, batch):
        for key in batch.keys:
            batch.load_sim(key)
            while not batch.sims[key].finished():
                batch.sims[key].advance_simulation(
                    stop_after_secs = self.timeout)
                batch.save_sim(key)

class ParallelProcessing(object):
    def __init__(self,
                 timeout = 120,
                 address = ('127.0.0.1', 50004),
                 authkey = 'blabla'):
        self.timeout = 120
        self.address = address
        self.authkey = authkey
    def work_for(cls, 
                 address = ('127.0.0.1', 50004),
                 authkey = 'blabla'):
        '''
        Launch a worker process, connecting to the server on the
        address specified.
        '''
        class QueueManager(multiprocessing.managers.BaseManager):
            pass
        QueueManager.register('get_queue')
        m = QueueManager(address = address, authkey = authkey)
        m.connect()
        queue = m.get_queue()
        while not queue.empty():
            (key, folder, timeout) = queue.get()
            sim = folder.load(key)
            while not sim.finished():
                sim.advance_simulation(stop_after_secs = timeout)
                folder.save(sim)
    work_for = classmethod(work_for)
    def process(self, batch):
        queue = Queue.Queue()
        class QueueManager(multiprocessing.managers.BaseManager):
            pass
        QueueManager.register('get_queue', callable = lambda: queue)
        m = QueueManager(address = self.address, authkey =
                         self.authkey)
        [queue.put((key, batch.folder, self.timeout)) for key in batch.keys]
        m.start()
        # the real queue object is now part of the process forked by
        # m.start(), so we need now in this process to get a proxy for
        # the queue

        m1 = QueueManager(address = self.address, authkey =
                         self.authkey)
        m1.connect()
        queue1 = m1.get_queue()
        while not queue1.empty():
            time.sleep(1)
        m.shutdown()

class Folder(object):
    ext = '.pickle'
    seed_file = '_seeds.pickle'
    def save(self, sim):
        pass
    def load(self, key):
        pass
    def load_seeds(self):
        pass

class LocalFolder(Folder):
    def __init__(self, path):
        self.path = path
    def save(self, sim):
        path = os.path.join(self.path, sim.hash_key + self.ext)
        file = open(path, 'wb')
        pickle.dump(sim, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    def load(self, key):
        path = os.path.join(self.path, key + self.ext)
        file = open(path, 'rb')
        obj = pickle.load(file)
        file.close()
        return obj
    def save_seeds(self, seeds):
        path = os.path.join(self.path, self.seed_file)
        file = open(path, 'wb')
        pickle.dump(seeds, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    def load_seeds(self):
        path = os.path.join(self.path, self.seed_file)
        file = open(path, 'rb')
        obj = pickle.load(file)
        file.close()
        return obj
class S3Folder(Folder):
    # How is the data stored on Amazon S3 ?
    # Easy.
    # You have AWS_BUCKET/batch_name/_seed.pickle which is a pickle of
    # a list of simulation seeds
    # and then AWS_BUCKET/batch_name/MD5_HASH.pickle which is the
    # pickle of the current state of the simulation
    bucket = 'speedflock'
    access_key_id = '1BYZG38150N2CF9TY8R2'
    secret_access_key = '9g2GECzSJuS3F6NDv5TqkAgUIGx12ut8Z4NnM6hi'
    def __init__(self, name):
        self.name = name
        self.conn = None

    def _connect(self):
        self.conn = S3.AWSAuthConnection(self.access_key_id,
                                         self.secret_access_key)

    def _close(self):
        pass

    def save(self, sim):
        key = self.name + '/' + sim.hash_key + self.ext
        self._connect()
        res = self.conn.put(self.bucket,
                            key,
                            pickle.dumps(sim, 
                                         pickle.HIGHEST_PROTOCOL))
        self._close()
        if res.http_response.status != 200:
            raise Exception('Cannot store object')

    def load(self, hash_key):
        key = self.name + '/' + hash_key + self.ext
        self._connect()
        res = self.conn.get(self.bucket, key)
        self._close()
        if res.http_response.status != 200:
            raise Exception('Cannot get object')
        return pickle.loads(res.object.data)

    def save_seeds(self, seeds):
        key = self.name + '/' + self.seed_file
        self._connect()
        res = self.conn.put(self.bucket, key,
                            pickle.dumps(seeds, pickle.HIGHEST_PROTOCOL))
        self._close()
        if res.http_response.status != 200:
            raise Exception('Cannot store seeds')

    def load_seeds(self):
        key = self.name + '/' + self.seed_file
        self._connect()
        res = self.conn.get(self.bucket, key)
        self._close()
        if res.http_response.status != 200:
            raise Exception('Cannot get seeds')
        return pickle.loads(res.object.data)
