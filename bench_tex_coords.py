import timeit
import glm

sector_verts = [(1.0, 2.0)] * 1000

def old_way(is_floor):
    tex_coords = [glm.vec2(v) for v in sector_verts]
    tex_coords = tex_coords if is_floor else [glm.vec2(v[0], -v[1]) for v in tex_coords]
    return tex_coords

def new_way(is_floor):
    if is_floor:
        return [glm.vec2(v[0], v[1]) for v in sector_verts]
    else:
        return [glm.vec2(v[0], -v[1]) for v in sector_verts]

print("old floor:", timeit.timeit("old_way(True)", globals=globals(), number=1000))
print("new floor:", timeit.timeit("new_way(True)", globals=globals(), number=1000))

print("old ceil:", timeit.timeit("old_way(False)", globals=globals(), number=1000))
print("new ceil:", timeit.timeit("new_way(False)", globals=globals(), number=1000))
