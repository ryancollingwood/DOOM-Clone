import timeit

setup_code = """
import sys
from unittest.mock import MagicMock
sys.modules['pyray'] = MagicMock()
sys.modules['glm'] = MagicMock()

class DummyVec2:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

import settings
settings.vec2 = DummyVec2

arr = [(DummyVec2(i, i), DummyVec2(i+1, i+1)) for i in range(1000)]
cx, cy = 1.5, 1.5
ox, oy = 10, 10
vec2 = DummyVec2
"""

old_code = """
[
    (vec2(p0.x * cx + ox, p0.y * cy + oy),
     vec2(p1.x * cx + ox, p1.y * cy + oy))
    for p0, p1 in arr
]
"""

new_code = """
[
    ((p0.x * cx + ox, p0.y * cy + oy),
     (p1.x * cx + ox, p1.y * cy + oy))
    for p0, p1 in arr
]
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000))
