import sys
from unittest.mock import MagicMock

# Mock dependencies before importing settings or utils
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

import pytest
from utils import cross_2d, is_on_front, is_on_back

def test_cross_2d():
    # Standard orthogonal vectors
    v1 = DummyVec2(1, 0)
    v2 = DummyVec2(0, 1)
    # 1*1 - 0*0 = 1
    assert cross_2d(v1, v2) == 1

    # Negative result
    assert cross_2d(v2, v1) == -1

    # Parallel vectors
    v3 = DummyVec2(2, 0)
    assert cross_2d(v1, v3) == 0

    # Arbitrary vectors
    v4 = DummyVec2(1, 2)
    v5 = DummyVec2(3, 4)
    # 1*4 - 3*2 = 4 - 6 = -2
    assert cross_2d(v4, v5) == -2

def test_is_on_front():
    # is_on_front(v0, v1) returns v0.x * v1.y < v1.x * v0.y
    # which is cross_2d(v0, v1) < 0

    v1 = DummyVec2(1, 0)
    v2 = DummyVec2(0, 1)

    # cross_2d(v1, v2) = 1 (>= 0), so not on front
    assert is_on_front(v1, v2) is False

    # cross_2d(v2, v1) = -1 (< 0), so on front
    assert is_on_front(v2, v1) is True

    # Parallel
    assert is_on_front(v1, v1) is False

def test_is_on_back():
    v1 = DummyVec2(1, 0)
    v2 = DummyVec2(0, 1)

    # is_on_back is not is_on_front
    assert is_on_back(v1, v2) is not is_on_front(v1, v2)
    assert is_on_back(v1, v2) is True
    assert is_on_back(v2, v1) is False
