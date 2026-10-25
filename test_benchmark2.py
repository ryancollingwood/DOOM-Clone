import timeit
import glm

sector_verts = [(i * 1.5, j * 2.5) for i in range(10) for j in range(10)]
is_floor = False

def original_ceiling():
    tex_coords = [glm.vec2(v) for v in sector_verts]
    tex_coords = [glm.vec2(v.x, -v.y) for v in tex_coords]
    return glm.array(tex_coords)

def inside_conditional():
    tex_coords = [glm.vec2(v) if is_floor else glm.vec2(v[0], -v[1]) for v in sector_verts]
    return glm.array(tex_coords)

def outside_conditional():
    tex_coords = [glm.vec2(v) for v in sector_verts] if is_floor else [glm.vec2(v[0], -v[1]) for v in sector_verts]
    return glm.array(tex_coords)

if __name__ == "__main__":
    n = 10000
    t_orig = timeit.timeit(original_ceiling, number=n)
    t_in = timeit.timeit(inside_conditional, number=n)
    t_out = timeit.timeit(outside_conditional, number=n)
    print(f"Original: {t_orig:.5f}s")
    print(f"Inside:   {t_in:.5f}s")
    print(f"Outside:  {t_out:.5f}s")
