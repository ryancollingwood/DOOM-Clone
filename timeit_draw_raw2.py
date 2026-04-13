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
    def __iter__(self):
        yield self.x
        yield self.y

raw_segments = [(DummyVec2(i, i), DummyVec2(i+1, i+1)) for i in range(1000)]
def draw_line_v(*args): pass
DARKGRAY = 1
"""

old_code = """
for p0, p1 in raw_segments:
    (x0, y0), (x1, y1) = p0, p1
    draw_line_v((x0, y0), (x1, y1), DARKGRAY)
"""

new_code = """
dl = draw_line_v
for p0, p1 in raw_segments:
    dl((p0.x, p0.y), (p1.x, p1.y), DARKGRAY)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000))
