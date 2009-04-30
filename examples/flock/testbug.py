import sys
sys.path.append('../..')
from flocking.calc import *
import pygame
from pygame.locals import *
from flocking.vis import *
from flocking.sim import *
import cPickle as pickle

sim = pickle.load(open('sim'))
sim.one_step()
