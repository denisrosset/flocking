import flocking.papers
import flocking.calc
from scipy import *


sim = flocking.papers.vicsek1995ntp.create_fig1a().create()
for i in range(0, 1000):
    sim.one_step()
print sim.time_elapsed
