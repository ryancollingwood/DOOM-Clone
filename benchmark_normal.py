import time
import glm
from glm import vec2, normalize

def draw_normal_original(p0, p1, scale=10):
    p10 = p1 - p0
    normal = normalize(vec2(-p10.y, p10.x))
    n0 = (p0 + p1) * 0.5
    n1 = n0 + normal * scale
    return n0, n1

def benchmark():
    p0 = vec2(0, 0)
    p1 = vec2(10, 10)
    iterations = 1000000

    start_time = time.time()
    for _ in range(iterations):
        n0, n1 = draw_normal_original(p0, p1)
    end_time = time.time()

    print(f"Original draw_normal calculations took: {end_time - start_time:.4f} seconds for {iterations} iterations")

    # Pre-calculated version
    n0_pre = (p0 + p1) * 0.5
    p10 = p1 - p0
    normal = normalize(vec2(-p10.y, p10.x))
    n1_pre = n0_pre + normal * 10

    start_time = time.time()
    for _ in range(iterations):
        # Just access pre-calculated values
        res = (n0_pre, n1_pre)
    end_time = time.time()

    print(f"Pre-calculated access took: {end_time - start_time:.4f} seconds for {iterations} iterations")

if __name__ == "__main__":
    benchmark()
