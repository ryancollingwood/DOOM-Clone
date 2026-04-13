from settings import *
from engine import Engine

class DummyApp:
    def __init__(self):
        self.dt = 0.016

import pyray as ray
ray.init_window(800, 600, 'Test')

app = DummyApp()
engine = Engine(app)

import cProfile
import pstats

pr = cProfile.Profile()
pr.enable()

for i in range(1000):
    engine.update()
    engine.draw_3d()

pr.disable()
stats = pstats.Stats(pr).sort_stats('tottime')
stats.print_stats(20)
