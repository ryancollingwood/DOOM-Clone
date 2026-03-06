import sys
from unittest.mock import MagicMock

# Mock glm and pyray before importing anything that depends on them
mock_glm = MagicMock()
mock_ray = MagicMock()

# Define a simple vec2 for testing
class MockVec2:
    def __init__(self, x=0, y=None):
        self.x = float(x)
        self.y = float(y if y is not None else x)

mock_glm.vec2 = MockVec2
mock_glm.vec3 = MagicMock()
mock_glm.ivec2 = MagicMock()
mock_glm.radians = lambda x: x # Simple mock for radians

mock_ray.Vector3 = MagicMock()
mock_ray.Vector2 = MagicMock()
mock_ray.Color = MagicMock()

sys.modules['glm'] = mock_glm
sys.modules['pyray'] = mock_ray

import pytest
from utils import cross_2d

def test_cross_2d_orthogonal():
    # Unit vectors on axes
    v0 = MockVec2(1, 0)
    v1 = MockVec2(0, 1)
    # 1*1 - 0*0 = 1
    assert cross_2d(v0, v1) == 1.0

    v0 = MockVec2(0, 1)
    v1 = MockVec2(1, 0)
    # 0*0 - 1*1 = -1
    assert cross_2d(v0, v1) == -1.0

def test_cross_2d_parallel():
    # Identical vectors
    v0 = MockVec2(1, 1)
    v1 = MockVec2(1, 1)
    # 1*1 - 1*1 = 0
    assert cross_2d(v0, v1) == 0.0

    # Opposite vectors
    v0 = MockVec2(1, 1)
    v1 = MockVec2(-1, -1)
    # 1*-1 - 1*-1 = -1 - (-1) = 0
    assert cross_2d(v0, v1) == 0.0

    # Scaled vectors
    v0 = MockVec2(1, 2)
    v1 = MockVec2(3, 6)
    # 1*6 - 2*3 = 6 - 6 = 0
    assert cross_2d(v0, v1) == 0.0

def test_cross_2d_zero():
    v0 = MockVec2(0, 0)
    v1 = MockVec2(5, 5)
    assert cross_2d(v0, v1) == 0.0

    v0 = MockVec2(5, 5)
    v1 = MockVec2(0, 0)
    assert cross_2d(v0, v1) == 0.0

def test_cross_2d_negative():
    v0 = MockVec2(-1, 2)
    v1 = MockVec2(3, -4)
    # (-1 * -4) - (2 * 3) = 4 - 6 = -2
    assert cross_2d(v0, v1) == -2.0

def test_cross_2d_general():
    v0 = MockVec2(1.5, 2.5)
    v1 = MockVec2(4.0, 1.0)
    # 1.5*1.0 - 2.5*4.0 = 1.5 - 10.0 = -8.5
    assert cross_2d(v0, v1) == -8.5
