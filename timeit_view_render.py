import timeit

setup_code = """
sectors = {i: f'sec{i}' for i in range(100)}
flat_models = [[i, i] for i in range(100)]
def draw(*args): pass
v_zero = 0
screen_tint = 1
"""

old_code = """
for sec_id in sectors:
    floor, ceil = flat_models[sec_id]
    draw(ceil, v_zero, 1.0, screen_tint)
    draw(floor, v_zero, 1.0, screen_tint)
"""

new_code = """
for floor, ceil in flat_models:
    draw(ceil, v_zero, 1.0, screen_tint)
    draw(floor, v_zero, 1.0, screen_tint)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=1000000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=1000000))
