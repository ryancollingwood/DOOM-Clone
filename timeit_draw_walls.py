import timeit

setup_code = """
import random

class DummyModel:
    pass

class DummyWall:
    __slots__ = ['model', 'is_shaded']
    def __init__(self, shaded):
        self.model = DummyModel()
        self.is_shaded = shaded

walls_to_draw = set([DummyWall(random.choice([True, False])) for _ in range(100)])

def draw_model(*args):
    pass

v_zero = 0
shade_tint = 2
screen_tint = 1
"""

old_code = """
for wall in walls_to_draw:
    draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)
"""

# Let's test checking `if wall.is_shaded` versus `shade_tint if wall.is_shaded else screen_tint`
new_code = """
for wall in walls_to_draw:
    if wall.is_shaded:
        draw_model(wall.model, v_zero, 1.0, shade_tint)
    else:
        draw_model(wall.model, v_zero, 1.0, screen_tint)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=1000000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=1000000))
