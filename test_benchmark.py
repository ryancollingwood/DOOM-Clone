import timeit
import glm

sector_verts = [(i * 1.5, j * 2.5) for i in range(10) for j in range(10)]

def original_ceiling():
    tex_coords = [glm.vec2(v) for v in sector_verts]
    tex_coords = [glm.vec2(v.x, -v.y) for v in tex_coords]
    return glm.array(tex_coords)

def optimized_ceiling():
    tex_coords = [glm.vec2(v[0], -v[1]) for v in sector_verts]
    return glm.array(tex_coords)

if __name__ == "__main__":
    n = 10000
    t_orig = timeit.timeit(original_ceiling, number=n)
    t_opt = timeit.timeit(optimized_ceiling, number=n)
    print(f"Original: {t_orig:.5f}s")
    print(f"Optimized: {t_opt:.5f}s")
