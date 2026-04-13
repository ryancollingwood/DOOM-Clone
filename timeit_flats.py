import timeit

setup_code = """
class DummyModel:
    pass

class DummyWall:
    def __init__(self, model):
        self.model = model

sectors = {0: 'sec0', 1: 'sec1', 2: 'sec2'}
flat_models = [
    [DummyWall('floor0'), DummyWall('ceil0')],
    [DummyWall('floor1'), DummyWall('ceil1')],
    [DummyWall('floor2'), DummyWall('ceil2')]
]

def draw_model(*args):
    pass
v_zero = 0
screen_tint = 1
"""

old_code = """
for sec_id in sectors:
    floor, ceil = flat_models[sec_id]
    draw_model(ceil.model, v_zero, 1.0, screen_tint)
    draw_model(floor.model, v_zero, 1.0, screen_tint)
"""

new_code = """
for floor, ceil in flat_models:
    draw_model(ceil.model, v_zero, 1.0, screen_tint)
    draw_model(floor.model, v_zero, 1.0, screen_tint)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=1000000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=1000000))
