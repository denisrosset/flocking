import sys
sys.path.append('..')
import flocking.sim
folder = flocking.sim.S3Folder(sys.argv[1])
batch = flocking.sim.Batch.load_from_folder(folder)
flocking.sim.StrideProcessing(int(sys.argv[2]), int(sys.argv[3])).process(batch)
