import flocking.papers
import flocking.calc
from scipy import *

N = 100000
rho = 2
sim = flocking.papers.vicsek1995ntp.create(N, sqrt(N/rho), 2, 100)
#sim.flockstep.neighbor_selector = flocking.calc.TopologicalDistanceNeighborSelecter(8)
sim = sim.create()
for i in range(0, 10):
    sim.one_step()
print sim.time_elapsed
