import sys
from unittest.mock import MagicMock

# Mock dependencies before importing
sys.modules['pyray'] = MagicMock()
sys.modules['glm'] = MagicMock()
sys.modules['sect'] = MagicMock()
sys.modules['ground'] = MagicMock()
sys.modules['raylib'] = MagicMock()
sys.modules['raylib.defines'] = MagicMock()

class DummyVec2:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

import settings
settings.vec2 = DummyVec2
settings.ray = MagicMock()

# Now we can import the engine
from engine import Engine
from main import App

class DummyApp:
    def __init__(self):
        self.dt = 0.016

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
stats.print_stats(30)
