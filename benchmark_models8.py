from settings import *
from models import Models
from data_types import Segment
import pyray as ray

class MockEngine:
    class level_data:
        class settings:
            seed = 0
        sectors = []

class MockModels:
    engine = MockEngine()
    textures = None

# We can run engine profile to see if things crash
