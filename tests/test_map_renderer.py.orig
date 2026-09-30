import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['pyray'] = MagicMock()
sys.modules['glm'] = MagicMock()
sys.modules['sect'] = MagicMock()
sys.modules['ground'] = MagicMock()
sys.modules['raylib'] = MagicMock()

class DummyVec2:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Mock vec2 inside settings
import settings
settings.vec2 = DummyVec2
settings.ray = MagicMock()
settings.MAP_OFFSET = 10

import pytest
from map_renderer import MapRenderer

class DummyCam:
    pass

class DummyBspBuilder:
    segments = []

class DummyLevelData:
    raw_segments = []

class DummyEngine:
    camera = DummyCam()
    bsp_builder = DummyBspBuilder()
    level_data = DummyLevelData()

def test_remap_array():
    renderer = MapRenderer.__new__(MapRenderer)

    renderer.x_min, renderer.y_min = 0, 0
    renderer.x_max, renderer.y_max = 100, 100
    renderer.x_out_max, renderer.y_out_max = 800, 600
    renderer.dx = 100
    renderer.dy = 100
    renderer.cx = (800 - 10) / 100
    renderer.cy = (600 - 10) / 100
    renderer.ox = 10
    renderer.oy = 10

    arr = [
        (DummyVec2(0, 0), DummyVec2(50, 50)),
        (DummyVec2(100, 100), DummyVec2(100, 0)),
    ]

    remapped = renderer.remap_array(arr)

    assert remapped[0][0].x == pytest.approx(10)
    assert remapped[0][0].y == pytest.approx(10)

    assert remapped[0][1].x == pytest.approx(405)
    assert remapped[0][1].y == pytest.approx(305)

    assert remapped[1][0].x == pytest.approx(800)
    assert remapped[1][0].y == pytest.approx(600)

    assert remapped[1][1].x == pytest.approx(800)
    assert remapped[1][1].y == pytest.approx(10)
