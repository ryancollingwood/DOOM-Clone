import timeit

s4 = """
class Segment:
    def __init__(self, mid, other):
        self.mid_wall_models = mid
        self.other_wall_models = other

mid1 = {1: 'a', 2: 'b'}
mid2 = {3: 'c'}
other1 = {4, 5}
other2 = {6}

segments = [
    Segment(mid1, other1),
    Segment(mid1, other1),
    Segment(mid2, other2),
    Segment(mid1, other1),
    Segment(mid2, other2)
] * 100

segment_ids_to_draw = list(range(len(segments)))

mid_walls_to_draw = {}
walls_to_draw = set()

def update():
    walls_to_draw.clear()
    mid_walls_to_draw.clear()

    processed_mid = set()
    processed_other = set()

    mid_add = processed_mid.add
    other_add = processed_other.add
    mid_update = mid_walls_to_draw.update
    other_update = walls_to_draw.update

    for seg in (segments[seg_id] for seg_id in segment_ids_to_draw):
        mid_id = id(seg.mid_wall_models)
        if mid_id not in processed_mid:
            mid_update(seg.mid_wall_models)
            mid_add(mid_id)

        other_id = id(seg.other_wall_models)
        if other_id not in processed_other:
            other_update(seg.other_wall_models)
            other_add(other_id)

update()
"""

print(timeit.timeit(s4, number=10000))
