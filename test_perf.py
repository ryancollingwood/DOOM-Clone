import timeit

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

class Node:
    def __init__(self):
        self.splitter_p0 = Vec2(1.0, 1.0)
        self.splitter_vec = Vec2(2.0, 3.0)
        self.front = None
        self.back = None
        self.segment_id = 1

pos_2d = Vec2(5.0, 5.0)

def is_on_front(vec_0, vec_1):
    return vec_0.x * vec_1.y < vec_1.x * vec_0.y

node = Node()

def test_original():
    on_front = is_on_front(pos_2d - node.splitter_p0, node.splitter_vec)

def test_optimized(x, y):
    dx = x - node.splitter_p0.x
    dy = y - node.splitter_p0.y
    vx = node.splitter_vec.x
    vy = node.splitter_vec.y
    on_front = dx * vy < vx * dy

print("Original:", timeit.timeit("test_original()", globals=globals(), number=1000000))
print("Optimized:", timeit.timeit("test_optimized(pos_2d.x, pos_2d.y)", globals=globals(), number=1000000))
