try:
#    import multiprocessing as processing
#    import multiprocessing.managers as managers
#except:
    import processing
    import processing.managers
except:
    pass
import Queue
import time
import copy
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
        for key in batch.seeds.iterkeys():
            while not batch[key].finished():
                batch[key].advance_simulation(
                    stop_after_secs = self.timeout)
                batch.save(key)

class StrideProcessing(object):
    def __init__(self, stride, number_of_strides, timeout = 120):
        self.timeout = timeout
        self.stride = stride
        self.number_of_strides = number_of_strides
    def process(self, batch):
        keys = sorted(batch.seeds.keys())
        my_keys = [keys[i] for i in range(0, len(keys))
                   if (i % self.number_of_strides) == self.stride]
        for key in my_keys:
            while not batch[key].finished():
                batch[key].advance_simulation(
                    stop_after_secs = self.timeout)
                batch.save(key)

class ParallelProcessing(object):
    default_port = 50001
    def __init__(self,
                 timeout = 120,
                 address = ('127.0.0.1', 50001),
                 authkey = 'blabla'):
        self.timeout = 120
        self.address = address
        self.authkey = authkey
    def work_for(cls, 
                 address = ('127.0.0.1', 50001),
                 authkey = 'blabla'):
        '''
        Launch a worker process, connecting to the server on the
        address specified.
        '''
        class QueueManager(processing.managers.BaseManager):
            pass
        QueueManager.register('get_processing_queue')
        QueueManager.register('get_finished_queue')
        QueueManager.register('get_timeout')
        m = QueueManager(address = address, authkey = authkey)
        m.connect()
        processing_queue = m.get_processing_queue()
        finished_queue = m.get_finished_queue()
        timeout = m.get_timeout()
        while True:
            sim = processing_queue.get()
            if sim is None:
                break
            sim.advance_simulation(stop_after_secs = timeout)
            finished_queue.put(sim)
            processing_queue.task_done()
    work_for = classmethod(work_for)
    def process(self, batch):
        processing_queue = Queue.Queue()
        finished_queue = Queue.Queue()
        class QueueManager(processing.managers.BaseManager):
            pass
        QueueManager.register('get_processing_queue',
                              callable = lambda: processing_queue)
        QueueManager.register('get_finished_queue',
                              callable = lambda: finished_queue)
        QueueManager.register('get_timeout', callable = lambda: self.timeout)
        m = QueueManager(address = self.address, authkey = self.authkey)
        batch.load_all()

        def put_sim_in_queue(sim, queue):
            sim_copy = copy.deepcopy(sim)
            sim_copy.clear_samples()
            queue.put(sim_copy)

        for sim in batch.sims.itervalues():
            put_sim_in_queue(sim, processing_queue)
        print 'm.start()'
        m.start()
        # the real queue object is now part of the process forked by
        # m.start(), so we need now in this process to get a proxy for
        # the queue
        m1 = QueueManager(address = self.address, authkey =
                         self.authkey)
        m1.connect()
        processing_queue = m1.get_processing_queue()
        finished_queue = m1.get_finished_queue()
        def process_finished_queue():
            while not finished_queue.empty():
                processed_sim = finished_queue.get()
                processed_sim.merge_samples(batch.sims[processed_sim.hash_key])
                batch.sims[processed_sim.hash_key] = processed_sim
                finished_queue.task_done()
                batch.save(processed_sim.hash_key)
                if not processed_sim.finished():
                    put_sim_in_queue(sim, processing_queue)

        while True:
            print '.'
            process_finished_queue()
            if processing_queue.empty():
                processing_queue.join()
                if finished_queue.empty():
                    break
        while processing_queue.empty():
            processing_queue.put(None)
            time.sleep(0.2) # ugly hack to wait for clients to get the None
        m.shutdown()
