import timeit

setup_code = """
class DummyVec2:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

segments = [(DummyVec2(i, i), DummyVec2(i+1, i+1)) for i in range(100)]
segment_normals = [(DummyVec2(i, i), DummyVec2(i+1, i+1)) for i in range(100)]
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

print("Old:", timeit.timeit("pass", setup=setup_code, number=10000))
# Let's test if unpacking `(x0, y0) = p0` actually works for the real segments objects which are vec2 (they don't in my mock without __iter__, wait, previously I saw `(x0, y0), (x1, y1) = p0, p1 = self.segments[seg_id]` in MapRenderer.draw_segments which implies they are iterable. But MapRenderer.remap_array returns tuples of vec2! Oh wait, `remap_array` returns `[(vec2(...), vec2(...)), ...]`. Wait, can `vec2` be unpacked? Yes, PyGLM's `vec2` is iterable.
