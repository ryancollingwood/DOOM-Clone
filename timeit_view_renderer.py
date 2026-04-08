import timeit

class DummyWall:
    pass

class DummySeg:
    def __init__(self, mid, other):
        self.mid_wall_models = mid
        self.other_wall_models = other

def setup():
    # simulate segments where most don't have mid walls
    segs = []
    for i in range(1000):
        mid = {1: DummyWall()} if i % 10 == 0 else {}
        other = [DummyWall()] if i % 2 == 0 else []
        segs.append(DummySeg(mid, other))
    return segs

def test_original(segments):
    walls_to_draw = set()
    mid_walls_to_draw = {}

    processed_mid = set()
    processed_other = set()

    mid_update = mid_walls_to_draw.update
    other_update = walls_to_draw.update
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

def test_optimized(segments):
    walls_to_draw = set()
    mid_walls_to_draw = {}

    processed_mid = set()
    processed_other = set()

    mid_update = mid_walls_to_draw.update
    other_update = walls_to_draw.update
    p_mid_add = processed_mid.add
    p_other_add = processed_other.add

    for seg in segments:
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

segs = setup()
print("Original:", timeit.timeit(lambda: test_original(segs), number=10000))
print("Optimized:", timeit.timeit(lambda: test_optimized(segs), number=10000))
