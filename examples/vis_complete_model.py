import sys
import math
import random

import pygame
from pygame.locals import *
import networkx

sys.path.append('..')
import flocking
from flocking.calc import *
from flocking.vis import *
import flocking.measure
def main():
    R = 10

    v = 1
    amax = 0.1
    vup = ConstantVelocityUpdater(v, amax)

    r0 = 0.5
    r1 = 2.0
    Fattr = 100
    Frep = -1
    fint = PiecewiseLinearInteractionForceEvaluator(Fattr, Frep, r0, r1)

    fint = LennardJonesInteractionForceEvaluator(1, 1.98, -1)

    beta = 1
    fav = NeighborAverageForceEvaluator(beta)

    fvreg = DummyVelocityForceEvaluator()

    ns = MetricDistanceNeighborSelector(R)
#    ns = VicsekNeighborSelector(R)
    eta = 0.8
    noise = ScalarNoiseAdder(eta)

    N = 4000
    rho = 0.06
    L = math.sqrt(N/rho)
    seed = 1000
    cvm = ConstantVelocityMagnitudeRandomFlockInitializer(v)
    flock = Flock(N, L, seed, cvm)

    dt = 0.01
    flockstep = FlockStep(dt, ns, vup, noise, fav, fint, fvreg)
    pygame.init()
    pygame.display.init()
    width = int(pygame.display.Info().current_w - 20)
    height = int(pygame.display.Info().current_h - 100)

    canvas = Canvas(array([width, height]), array([L/2, L/2]), height/L, L)
    canvas.drawers.append(FlockDrawer(flock, flockstep))
    colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(0, N)]
    flock.color = [(255, 255, 255) for i in range(0, N)]
    while True:
#            G = networkx.Graph()
#            G.add_edges_from(flockstep.fast_list_of_edges(flock))
#            cc = networkx.connected_components(G)

        cc = flocking.measure.ConnectedComponents()(flock, flockstep)
        cc = sorted(cc, lambda x, y: len(y) - len(x))
        for i in range(0, len(cc)):
            for j in cc[i]:
                flock.color[j] = colors[i]
        canvas.treat_keyboard()
        canvas.center = flocking.measure.CenterOfMass()(flock, flockstep)
        canvas.draw()
        flockstep.c_step(flock, steps = 10)
if __name__ == '__main__': main()
