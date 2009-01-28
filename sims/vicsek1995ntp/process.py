import sys
sys.path.append('../..')
import flocking.sim
folder = flocking.sim.LocalFolder('/Users/denisrosset/Projects/Uni/Master/2009/sims/vicsek1995ntp/data')
batch = flocking.sim.Batch.load_from_folder(folder)
flocking.sim.ParallelProcessing().process(batch, address = ('75.101.161.126', 50004))
