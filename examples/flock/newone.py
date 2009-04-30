import sys
sys.path.append('../..')
from flocking.calc import *
import pygame
from pygame.locals import *
from flocking.vis import *
from flocking.sim import *
import cPickle as pickle
v = 1
dt = 0.01
R = 10
flock_initializer = ConstantVelocityMagnitudeRandomFlockInitializer(v)
N = 70
L = 100
seed = 1000
flockseed = FlockSeed(N, L, seed, flock_initializer)
ns = TopologicalDistanceNeighborSelector(10)
#ns = MetricDistanceNeighborSelector(R)
alg = OriginalVicsekAlgorithm()
eta = 0.1
na = ScalarNoiseAdder(eta)
amax = 100
vup = ConstantVelocityUpdater(na, v, amax)
beta = 1.0
fav = NeighborAverageForceEvaluator(beta)
fint = PiecewiseLinearForceEvaluator(100.0, -1.0, 0.5, 2.0)
flockstep = FlockStep(dt, ns, vup, alg, [fint, fav])
flock = flockseed.create()
print flockstep.c_init()
pygame.init()
pygame.display.init()
canvas = PygameCanvas.create_big_canvas_from_flock(flock)
canvas.init()
canvas.drawers.append(FlockDrawer(flock, flockstep, light_radius = 0.5, dark_radius = 2))
canvas.velocity_factor = 10
canvas.force_factor = 10
colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(0, N)]
flock.color = [(255, 255, 255) for i in range(0, N)]
while True:
    cc = flocking.measure.ConnectedComponents()(flock, flockstep)
    cc = sorted(cc, lambda x, y: len(y) - len(x))
    for i in range(0, len(cc)):
        for j in cc[i]:
           flock.color[j] = colors[i]
    canvas.treat_keyboard()
    canvas.center = flocking.measure.CenterOfMass()(flock, flockstep)
    canvas.draw()
    for i in range(0, 200):
        flockstep.step(flock, debug = True)
