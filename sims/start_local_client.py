import sys
sys.path.append('..')
import flocking.sim
flocking.sim.ParallelProcessing.work_for(address = ('127.0.0.1', 50000))
