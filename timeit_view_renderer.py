import timeit

class Segment:
    def __init__(self, mid, other):
        self.mid_wall_models = mid
        self.other_wall_models = other

segments = []
for i in range(1000):
    if i % 10 == 0:
        segments.append(Segment({1: 'a'}, ['a']))
    else:
        segments.append(Segment({}, []))

def update_old():
    processed_mid = set()
    processed_other = set()
    mid_dict = {}
    other_set = set()
    mid_update = mid_dict.update
    other_update = other_set.update
    p_mid_add = processed_mid.add
    p_other_add = processed_other.add

    for seg in segments:
        mid_id = id(seg.mid_wall_models)
        if mid_id not in processed_mid:
            mid_update(seg.mid_wall_models)
            p_mid_add(mid_id)

        other_id = id(seg.other_wall_models)
        if other_id not in processed_other:
            other_update(seg.other_wall_models)
            p_other_add(other_id)

def update_new():
    processed_mid = set()
    processed_other = set()
    mid_dict = {}
    other_set = set()
    mid_update = mid_dict.update
    other_update = other_set.update
    p_mid_add = processed_mid.add
    p_other_add = processed_other.add

    for seg in segments:
        mid_models = seg.mid_wall_models
        if mid_models:
            mid_id = id(mid_models)
            if mid_id not in processed_mid:
                mid_update(mid_models)
                p_mid_add(mid_id)

        other_models = seg.other_wall_models
        if other_models:
            other_id = id(other_models)
            if other_id not in processed_other:
                other_update(other_models)
                p_other_add(other_id)

print("Old:", timeit.timeit("update_old()", globals=globals(), number=10000))
print("New:", timeit.timeit("update_new()", globals=globals(), number=10000))
