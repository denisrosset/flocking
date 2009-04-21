import flocking.papers
import flocking.calc
from scipy import *

N = 1000
rho = 2
sim = flocking.papers.vicsek1995ntp.create(N= N, L=sqrt(N/rho), eta=0.1, seed=1000, steps = 1000)
#sim.flockstep.neighbor_selector = flocking.calc.TopologicalDistanceNeighborSelecter(8)
sim = sim.create()
for i in range(0, 1000):
    sim.one_step()
print sim.time_elapsed
