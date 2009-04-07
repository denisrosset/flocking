import sys
sys.path.append('../..')
import flocking.sim
folder = flocking.sim.S3Folder(sys.argv[1])
batch = flocking.sim.Batch.load_from_folder(folder)
flocking.sim.ParallelProcessing(address = ('174.129.223.214', 50000)).process(batch)
