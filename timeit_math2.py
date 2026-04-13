import timeit

setup_code = """
import math
import pyray as ray
import glm

def setup():
    return [glm.vec2(0, -bottom) for bottom in range(100)]
"""

old_code = """
[glm.vec2(0, -bottom) for bottom in range(100)]
"""

new_code = """
[glm.vec2(0, -bottom) for bottom in range(100)]
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=100000))
# print("New:", timeit.timeit(new_code, setup=setup_code, number=100000))
