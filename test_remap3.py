import timeit

s1 = """
class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

arr = [(Vec2(i, i), Vec2(i*2, i*2)) for i in range(1000)]
x_min, x_max, y_min, y_max = 0, 1000, 0, 1000
x_out_max, y_out_max = 800, 600
out_min = 50

def remap_array(arr, out_min=50):
    dx = x_max - x_min
    dy = y_max - y_min

    cx = (x_out_max - out_min) / dx if dx else 0
    cy = (y_out_max - out_min) / dy if dy else 0

    ox = out_min - x_min * cx
    oy = out_min - y_min * cy

    return [
        (Vec2(p0.x * cx + ox, p0.y * cy + oy),
         Vec2(p1.x * cx + ox, p1.y * cy + oy))
        for p0, p1 in arr
    ]

remap_array(arr)
"""

s2 = """
class Vec2:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

arr = [(Vec2(i, i), Vec2(i*2, i*2)) for i in range(1000)]
x_min, x_max, y_min, y_max = 0, 1000, 0, 1000
x_out_max, y_out_max = 800, 600
out_min = 50

def remap_array(arr, out_min=50):
    dx = x_max - x_min
    dy = y_max - y_min

    cx = (x_out_max - out_min) / dx if dx else 0
    cy = (y_out_max - out_min) / dy if dy else 0

    ox = out_min - x_min * cx
    oy = out_min - y_min * cy

    return [
        (Vec2(p0.x * cx + ox, p0.y * cy + oy),
         Vec2(p1.x * cx + ox, p1.y * cy + oy))
        for p0, p1 in arr
    ]

remap_array(arr)
"""

print(timeit.timeit(s1, number=10000))
print(timeit.timeit(s2, number=10000))
