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

import map_renderer
map_renderer.vec2 = DummyVec2

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

    # We use the original MAP_OFFSET from map_renderer since we didn't patch it before import
    MAP_OFFSET = map_renderer.MAP_OFFSET

    renderer.cx = (800 - MAP_OFFSET) / 100
    renderer.cy = (600 - MAP_OFFSET) / 100
    renderer.ox = MAP_OFFSET
    renderer.oy = MAP_OFFSET

    arr = [
        (DummyVec2(0, 0), DummyVec2(50, 50)),
        (DummyVec2(100, 100), DummyVec2(100, 0)),
    ]

    remapped = renderer.remap_array(arr)

    assert remapped[0][0].x == pytest.approx(MAP_OFFSET)
    assert remapped[0][0].y == pytest.approx(MAP_OFFSET)

    assert remapped[0][1].x == pytest.approx(50 * renderer.cx + MAP_OFFSET)
    assert remapped[0][1].y == pytest.approx(50 * renderer.cy + MAP_OFFSET)

    assert remapped[1][0].x == pytest.approx(800)
    assert remapped[1][0].y == pytest.approx(600)

    assert remapped[1][1].x == pytest.approx(800)
    assert remapped[1][1].y == pytest.approx(MAP_OFFSET)
