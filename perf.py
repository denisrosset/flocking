import flocking.papers
import flocking.calc
from scipy import *

sim = flocking.papers.vicsek1995ntp.create_fig1a()
#sim.flockstep.neighbor_selector = flocking.calc.TopologicalDistanceNeighborSelecter(8)
sim.flockseed.N = 4000
sim = sim.create()
for i in range(0, 100):
    sim.one_step()
print sim.time_elapsed
