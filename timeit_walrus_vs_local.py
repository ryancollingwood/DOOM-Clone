import timeit

setup_code = """
class SegSlots:
    __slots__ = ['mid_wall_models', 'other_wall_models']
    def __init__(self, mid, other):
        self.mid_wall_models = mid
        self.other_wall_models = other

segs_slots = [SegSlots([], [1]) for _ in range(900)] + [SegSlots([1], [1]) for _ in range(100)]
"""

test_walrus = """
mid_walls = []
other_walls = []
mid_extend = mid_walls.extend
other_extend = other_walls.extend

for seg in segs_slots:
    if (mid := seg.mid_wall_models):
        mid_extend(mid)
    if (other := seg.other_wall_models):
        other_extend(other)
"""

test_local = """
mid_walls = []
other_walls = []
mid_extend = mid_walls.extend
other_extend = other_walls.extend

for seg in segs_slots:
    mid = seg.mid_wall_models
    if mid: mid_extend(mid)
    other = seg.other_wall_models
    if other: other_extend(other)
"""

print(f"Walrus: {timeit.timeit(test_walrus, setup=setup_code, number=100000):.4f}")
print(f"Local: {timeit.timeit(test_local, setup=setup_code, number=100000):.4f}")
