import timeit

setup_code = """
class DummyModel:
    pass
class FlatModel:
    def __init__(self):
        self.model = DummyModel()

sectors = {i: f'sec_{i}' for i in range(100)}
flat_models = [[FlatModel(), FlatModel()] for _ in range(100)]

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
# Instead of iterating over sectors and using it as index (since flat_models has indices matching sectors keys apparently, but wait, self.flat_models is a list and it's indexed by sec_id. Wait, what if sec_id is just an int?)
for floor, ceil in flat_models:
    draw_model(ceil.model, v_zero, 1.0, screen_tint)
    draw_model(floor.model, v_zero, 1.0, screen_tint)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=100000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=100000))
