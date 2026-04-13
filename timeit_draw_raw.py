import timeit

setup_code = """
class DummyVec2:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
# Actually, p0 and p1 are vec2 objects which can't be unpacked with `(x0, y0) = p0` if they don't support iteration, wait: in the old code `(x0, y0) = p0` means vec2 is iterable?
for p0, p1 in raw_segments:
    x0, y0 = p0.x, p0.y
    x1, y1 = p1.x, p1.y
    draw_line_v((x0, y0), (x1, y1), DARKGRAY)
"""

print("Old:", timeit.timeit("pass", setup=setup_code, number=10000))
# Let's test the iterability of vec2
