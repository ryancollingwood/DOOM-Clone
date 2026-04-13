import timeit

setup_code = """
class DummyModel:
    pass

class DummySeg:
    __slots__ = ['mid_wall_models', 'other_wall_models']
    def __init__(self):
        self.mid_wall_models = {1: DummyModel()}
        self.other_wall_models = [DummyModel(), DummyModel()]

segments = [DummySeg() for _ in range(100)]
segment_ids_to_draw = list(range(100))

processed_mid = set()
processed_other = set()

mid_walls_to_draw = {}
walls_to_draw = set()

mid_update = mid_walls_to_draw.update
other_update = walls_to_draw.update
p_mid_add = processed_mid.add
p_other_add = processed_other.add
"""

old_code = """
for seg_id in segment_ids_to_draw:
    seg = segments[seg_id]

    if seg.mid_wall_models:
        mid_id = id(seg.mid_wall_models)
        if mid_id not in processed_mid:
            mid_update(seg.mid_wall_models)
            p_mid_add(mid_id)

    if seg.other_wall_models:
        other_id = id(seg.other_wall_models)
        if other_id not in processed_other:
            other_update(seg.other_wall_models)
            p_other_add(other_id)

processed_mid.clear()
processed_other.clear()
mid_walls_to_draw.clear()
walls_to_draw.clear()
"""

new_code = """
for seg_id in segment_ids_to_draw:
    seg = segments[seg_id]

    if (mid := seg.mid_wall_models):
        mid_id = id(mid)
        if mid_id not in processed_mid:
            mid_update(mid)
            p_mid_add(mid_id)

    if (other := seg.other_wall_models):
        other_id = id(other)
        if other_id not in processed_other:
            other_update(other)
            p_other_add(other_id)

processed_mid.clear()
processed_other.clear()
mid_walls_to_draw.clear()
walls_to_draw.clear()
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000))
