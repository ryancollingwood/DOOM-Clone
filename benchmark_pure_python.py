import time
import math

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

def normalize(v):
    mag = math.sqrt(v.x**2 + v.y**2)
    if mag == 0: return Vec2(0,0)
    return Vec2(v.x / mag, v.y / mag)

def draw_normal_calc(p0, p1, scale=10):
    p10 = p1 - p0
    normal = normalize(Vec2(-p10.y, p10.x))
    n0 = (p0 + p1) * 0.5
    n1 = n0 + normal * scale
    return (n0.x, n0.y), (n1.x, n1.y)

def benchmark():
    p0 = Vec2(0, 0)
    p1 = Vec2(10, 10)
    iterations = 1000000

    start_time = time.time()
    for _ in range(iterations):
        res = draw_normal_calc(p0, p1)
    end_time = time.time()
    calc_time = end_time - start_time
    print(f"Calculations took: {calc_time:.4f}s")

    # Mock pre-calculated
    pre_n0 = (5.0, 5.0)
    pre_n1 = (12.0, -2.0)

    start_time = time.time()
    for _ in range(iterations):
        res = (pre_n0, pre_n1)
    end_time = time.time()
    pre_time = end_time - start_time
    print(f"Pre-calculated took: {pre_time:.4f}s")

    improvement = (calc_time - pre_time) / calc_time * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    benchmark()
