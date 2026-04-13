import timeit

setup_code = """
import math
dx = 10.0
dy = 10.0
dz = 10.0
"""

old_code = """
length = (dx * dx + dy * dy + dz * dz) ** 0.5
"""

new_code = """
length = math.sqrt(dx * dx + dy * dy + dz * dz)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000000))
