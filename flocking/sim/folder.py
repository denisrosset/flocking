import os.path
import cPickle as pickle
from ..externals import S3

class Folder(object):
    '''Represent a place where simulation and seeds are stored.
    '''
    ext = '.pickle'
    seed_file = '_seeds.pickle'
    def save(self, sim):
        ''' Save specified simulation object in the folder '''
        pass
    def load(self, key):
        ''' Load and return the simulation specified by key '''
        pass
    def load_seeds(self):
        ''' Load and return the list of seeds '''
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
