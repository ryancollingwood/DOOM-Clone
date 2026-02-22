import sys
from unittest.mock import MagicMock
import pytest

# Mock modules globally before any test imports them
sys.modules['raylib'] = MagicMock()
sys.modules['raylib.defines'] = MagicMock()
sys.modules['pyray'] = MagicMock()
sys.modules['glm'] = MagicMock()
sys.modules['ground'] = MagicMock()
sys.modules['ground.base'] = MagicMock()
sys.modules['sect'] = MagicMock()
sys.modules['sect.triangulation'] = MagicMock()
# sys.modules['texture_id'] = MagicMock() # Use real module

# Mock glm.vec2
class Vec2Mock:
    def __init__(self, x, y=None):
        self.x = x
        self.y = y if y is not None else x
    def __sub__(self, other):
        return Vec2Mock(0, 0)
    def __add__(self, other):
        return Vec2Mock(0, 0)
    def __mul__(self, other):
        return Vec2Mock(0, 0)
    def __truediv__(self, other):
        return Vec2Mock(0, 0)
    def __iter__(self):
        yield self.x
        yield self.y
    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

sys.modules['glm'].vec2 = Vec2Mock

# Mock settings
settings_mock = MagicMock()
settings_mock.WIN_WIDTH = 800
settings_mock.WIN_HEIGHT = 600
settings_mock.VEC3_ZERO = MagicMock()
settings_mock.WHITE_COLOR = MagicMock()
settings_mock.BLACK_COLOR = MagicMock()
settings_mock.DARK_GRAY_COLOR = MagicMock()
settings_mock.SHADING_COLOR = MagicMock()
settings_mock.SHADING_DARK_COLOR = MagicMock()
settings_mock.EPS = 1e-4
settings_mock.vec2 = Vec2Mock
settings_mock.ray = sys.modules['pyray']
sys.modules['settings'] = settings_mock
