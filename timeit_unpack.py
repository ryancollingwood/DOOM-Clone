import timeit

setup_code = """
import sys
from unittest.mock import MagicMock
sys.modules['pyray'] = MagicMock()
import glm
segments = [(glm.vec2(i, i), glm.vec2(i+1, i+1)) for i in range(100)]
segment_normals = [(glm.vec2(i, i), glm.vec2(i+1, i+1)) for i in range(100)]
segment_ids = list(range(100))

def draw_line_v(*args): pass
def draw_circle_v(*args): pass
seg_color = 1
WHITE = 2
"""

old_code = """
for seg_id in segment_ids:
    (x0, y0), (x1, y1) = p0, p1 = segments[seg_id]

    draw_line_v((x0, y0), (x1, y1), seg_color)

    n0, n1 = segment_normals[seg_id]
    draw_line_v((n0.x, n0.y), (n1.x, n1.y), seg_color)

    draw_circle_v((x0, y0), 2, WHITE)
    draw_circle_v((x1, y1), 2, WHITE)
"""

new_code = """
dl = draw_line_v
dc = draw_circle_v

for seg_id in segment_ids:
    p0, p1 = segments[seg_id]
    x0, y0 = p0.x, p0.y
    x1, y1 = p1.x, p1.y

    dl((x0, y0), (x1, y1), seg_color)

    n0, n1 = segment_normals[seg_id]
    dl((n0.x, n0.y), (n1.x, n1.y), seg_color)

    dc((x0, y0), 2, WHITE)
    dc((x1, y1), 2, WHITE)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000))
