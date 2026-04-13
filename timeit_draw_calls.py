import timeit

setup_code = """
import random

class DummyModel:
    pass

class DummyWall:
    __slots__ = ['model', 'is_shaded']
    def __init__(self, is_shaded):
        self.model = DummyModel()
        self.is_shaded = is_shaded

walls_to_draw = set([DummyWall(i % 2 == 0) for i in range(100)])

def draw_model(*args):
    pass

v_zero = 0
shade_tint = 1
screen_tint = 2
draw_model_cached = draw_model
"""

old_code = """
for wall in walls_to_draw:
    draw_model_cached(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)
"""

new_code = """
for wall in walls_to_draw:
    if wall.is_shaded:
        draw_model_cached(wall.model, v_zero, 1.0, shade_tint)
    else:
        draw_model_cached(wall.model, v_zero, 1.0, screen_tint)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000))
