import md5
import resource
import time
class SimSeed(object):
    '''Immutable.'''
    def __init__(self, flockseed, flockstep, n_steps, samplers = {}):
        self.flockseed = flockseed
        self.flockstep = flockstep
        self.n_steps = n_steps
        self.samplers = samplers
        self.hash_key = self.calculate_hash_key()
    def create(self):
        flock = self.flockseed.create()
        samples = {}
        for name in self.samplers.keys():
            samples[name] = {}
        sim = Sim(simseed = self,
                  flock = flock,
                  flockstep = self.flockstep,
                  step = 0,
                  n_steps = self.n_steps,
                  time_elapsed = 0,
                  hash_key = self.hash_key,
                  samplers = self.samplers,
                  samples = samples)
        sim.sample()
        return sim
    def calculate_hash_key(self):
        parameters = self.flockseed.get_parameters()
        parameters.update(self.flockstep.get_parameters())
        list = sorted(parameters.items())
        return md5.md5(str(list)).hexdigest()
    def get_parameters(self):
        d = {}
        d.update(self.flockstep.get_parameters())
        d.update(self.flockseed.get_parameters())
        return d

class Sim(object):
    ###
    # Initalize the Sim object with the flock and flockstep object given.
    # No copies are being made, the flock object given will be
    # modified by the stepping.
    def __init__(self,
                 simseed,
                 flock,
                 flockstep, 
                 step,
                 n_steps,
                 time_elapsed,
                 hash_key,
                 samplers = {},
                 samples = {}):
        self.simseed = simseed
        self.flock = flock
        self.flockstep = flockstep
        self.step = step
        self.n_steps = n_steps
        self.time_elapsed = 0
        self.hash_key = hash_key
        self.samplers = samplers
        self.samples = samples
    def clear_samples(self):
        for name in self.samplers.keys():
            self.samples[name] = {}
    def merge_samples(self, previous_sim):
        for name in self.samplers.keys():
            self.samples[name].update(previous_sim.samples[name])
    ###
    # Do a sampling for all the samplers that need to be evaluated for
    # the current step.
    def sample(self):
        for (name, sampler) in self.samplers.items():
            result = sampler(self.flock, self.flockstep, self.step)
            if result is not None:
                self.samples[name][self.step] = result
    def get_parameters(self):
        return self.simseed.get_parameters()
    ###
    # Step for the number of steps supplied.
    def one_step(self, fast = True):
        start = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        self.flockstep.step(self.flock, fast)
        end = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        self.time_elapsed += end - start
        self.step += 1
        self.sample()

    def complete_simulation(self):
        '''Complete the simulation, by walking all the steps from the
        current step to the number of steps desired n_steps.'''
        while self.step < self.n_steps:
            self.one_step()
    def finished(self):
        '''Return the state of completion of current simulation'''
        return self.step >= self.n_steps
    def advance_simulation(self, stop_after_secs = None,
                           stop_after_steps = None):
        '''Completes the current simulation. Returns if the simulation
        is complete, if the specified timeout occurs (in secs or
        steps).

        Returns True if the simulation is finished'''
        this_adv_step = 0
        start_time = time.time()
        while (self.step <= self.n_steps and
               (not stop_after_steps or  this_adv_step < stop_after_steps) and 
               (not stop_after_secs or time.time() - start_time < stop_after_secs)):
            self.one_step()
            this_adv_step += 1

class Batch(object):
    @classmethod
    def create_from_seeds(cls, list_of_seeds, folder):
        seeds = dict([(seed.hash_key, seed) for seed in list_of_seeds])
        sims = {}
        batch = Batch(seeds, sims, folder)
        batch.save_all()
        return batch
    @classmethod
    def load_from_folder(cls, folder):
        seeds = folder.load_seeds()
        sims = {}
        batch = Batch(seeds, sims, folder)
        return batch

    def release_memory(self):
        self.sims = {}
    def __getitem__(self, key):
        return self.load(key)

    def __init__(self, seeds = {}, sims = {}, folder = None):
        self.folder = folder
        self.sims = sims
        self.seeds = seeds

    def save_all(self):
        ''' Save all the loaded sims and seeds '''
        self.folder.save_seeds(self.seeds)
        for key in self.sims.iterkeys():
            self.save(key)
    def load_all(self):
        ''' Load all the sims in the folder, and create sims from
        seed for unsaved ones '''
        for key in self.seeds.iterkeys():
            self.load(key)
    def save(self, key):
        ''' Save the specified seed '''
        self.folder.save(self.sims[key])
    def load(self, key):
        if self.sims.has_key(key):
            return self.sims[key]
        sim = None
        try:
            print 'loading', key
            sim = self.folder.load(key)
        except:
            print 'creating', key
            sim = self.seeds[key].create()
        self.sims[key] = sim
        return sim
    def extend_n_steps(self, key, n_steps):
        self.seeds[key].n_steps = n_steps
        self[key].n_steps = n_steps
        self.save(key)
