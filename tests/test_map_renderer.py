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


def test_get_bounds():
    inf = float('inf')

    # Case 1: Empty list
    assert MapRenderer.get_bounds([]) == (inf, inf, -inf, -inf)

    # Case 2: Single segment
    seg1 = (DummyVec2(1, 2), DummyVec2(3, 4))
    assert MapRenderer.get_bounds([seg1]) == (1, 2, 3, 4)

    # Case 3: Multiple segments
    seg2 = (DummyVec2(0, 10), DummyVec2(10, 0))
    seg3 = (DummyVec2(-5, 5), DummyVec2(15, 5))
    # x_min: -5, y_min: 0, x_max: 15, y_max: 10
    assert MapRenderer.get_bounds([seg2, seg3]) == (-5, 0, 15, 10)

    # Case 4: Negative coordinates
    seg4 = (DummyVec2(-10, -20), DummyVec2(-5, -15))
    assert MapRenderer.get_bounds([seg4]) == (-10, -20, -5, -15)

    # Case 5: Identical points
    seg5 = (DummyVec2(7, 7), DummyVec2(7, 7))
    assert MapRenderer.get_bounds([seg5]) == (7, 7, 7, 7)

    # Case 6: Mixed segments
    assert MapRenderer.get_bounds([seg1, seg2, seg3, seg4, seg5]) == (-10, -20, 15, 10)
