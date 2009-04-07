import sys
sys.path.append('..')
import flocking.sim
folder = flocking.sim.S3Folder(sys.argv[1])
batch = flocking.sim.Batch.load_from_folder(folder)
print('starting server')x
flocking.sim.ParallelProcessing(address = ('127.0.0.1', 50001)).process(batch)
