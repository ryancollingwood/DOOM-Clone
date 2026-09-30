import timeit
import glm

class MockSectorVert:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self):
        return 2

    def __getitem__(self, idx):
        if idx == 0: return self.x
        if idx == 1: return self.y
        raise IndexError

# Generate dummy sector verts
sector_verts = [glm.vec2(i * 1.5, j * 2.5) for i in range(10) for j in range(10)]

def original_floor():
    tex_coords = [glm.vec2(v) for v in sector_verts]
    tex_coords = tex_coords
    return glm.array(tex_coords)

def original_ceiling():
    tex_coords = [glm.vec2(v) for v in sector_verts]
    tex_coords = [glm.vec2(v.x, -v.y) for v in tex_coords]
    return glm.array(tex_coords)

def optimized_floor():
    tex_coords = [glm.vec2(v) for v in sector_verts]
    return glm.array(tex_coords)

def optimized_ceiling():
    tex_coords = [glm.vec2(v.x, -v.y) for v in sector_verts]
    return glm.array(tex_coords)

if __name__ == "__main__":
    n = 10000

    t_orig_floor = timeit.timeit(original_floor, number=n)
    t_orig_ceil = timeit.timeit(original_ceiling, number=n)

    t_opt_floor = timeit.timeit(optimized_floor, number=n)
    t_opt_ceil = timeit.timeit(optimized_ceiling, number=n)

    print(f"Original Floor: {t_orig_floor:.5f}s")
    print(f"Original Ceil:  {t_orig_ceil:.5f}s")
    print(f"Optimized Floor: {t_opt_floor:.5f}s")
    print(f"Optimized Ceil:  {t_opt_ceil:.5f}s")
