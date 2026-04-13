import timeit

setup_code = """
class DummyWall:
    pass

mid_walls_to_draw = {i: DummyWall() for i in range(100)}
def draw_model(*args): pass
v_zero = 0
shade_tint = 1
screen_tint = 2
"""

old_code = """
for wall in reversed(mid_walls_to_draw.values()):
    draw_model(wall, v_zero, 1.0, screen_tint)
"""

new_code = """
# wait, reversed(dict.values()) is already O(N).
pass
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=100000))
