import timeit

setup = """
import glm

class MockModel:
    def __init__(self, is_floor):
        self.is_floor = is_floor
        self.sector_verts = [(i * 1.5, j * 2.5) for i in range(10) for j in range(10)]

    def get_tex_coords_orig(self):
        sector_verts = self.sector_verts
        tex_coords = [glm.vec2(v) for v in sector_verts]
        tex_coords = tex_coords if self.is_floor else [glm.vec2(v.x, -v.y) for v in tex_coords]
        return glm.array(tex_coords)

    def get_tex_coords_opt(self):
        sector_verts = self.sector_verts
        tex_coords = [glm.vec2(v) for v in sector_verts] if self.is_floor else [glm.vec2(v[0], -v[1]) for v in sector_verts]
        return glm.array(tex_coords)

model_floor = MockModel(True)
model_ceil = MockModel(False)
"""

if __name__ == "__main__":
    n = 10000

    t_orig_floor = timeit.timeit("model_floor.get_tex_coords_orig()", setup=setup, number=n)
    t_opt_floor = timeit.timeit("model_floor.get_tex_coords_opt()", setup=setup, number=n)

    t_orig_ceil = timeit.timeit("model_ceil.get_tex_coords_orig()", setup=setup, number=n)
    t_opt_ceil = timeit.timeit("model_ceil.get_tex_coords_opt()", setup=setup, number=n)

    print(f"Original Floor: {t_orig_floor:.5f}s")
    print(f"Optimized Floor: {t_opt_floor:.5f}s")
    print(f"Original Ceil: {t_orig_ceil:.5f}s")
    print(f"Optimized Ceil: {t_opt_ceil:.5f}s")
