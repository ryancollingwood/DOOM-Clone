import timeit

setup_code = """
class DummyModel:
    pass

class DummyWall:
    def __init__(self, shaded):
        self.model = DummyModel()
        self.is_shaded = shaded

walls_to_draw = [DummyWall(True), DummyWall(False), DummyWall(True)] * 10

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

new_code = """
for wall in walls_to_draw:
    draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)
"""

# Let's see if we can optimize the iteration or conditionals.
# Actually, wall.is_shaded is accessed inside the loop.
# What if we pre-calculate or avoid conditional branching?
