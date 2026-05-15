import timeit

setup = """
class Segment:
    __slots__ = ('mid_wall_models', 'other_wall_models', 'sector_id', 'back_sector_id')
    def __init__(self, m, o, s, b):
        self.mid_wall_models = m
        self.other_wall_models = o
        self.sector_id = s
        self.back_sector_id = b

segments = [Segment({'m': i}, [i, i+1], i % 10, (i + 1) % 10) for i in range(1000)]
segment_ids_to_draw = list(range(0, 1000, 2))

class ViewRendererMock:
    def __init__(self):
        self.segments = segments
        self.segment_ids_to_draw = segment_ids_to_draw
        self.mid_walls_to_draw = {}
        self.walls_to_draw = set()

    def update_old(self):
        self.walls_to_draw.clear()
        self.mid_walls_to_draw.clear()

        segments = self.segments
        mid_update = self.mid_walls_to_draw.update
        other_update = self.walls_to_draw.update

        num_segs = 1000
        processed_segs = [False] * num_segs

        for seg_id in self.segment_ids_to_draw:
            seg = segments[seg_id]
            s_id = seg_id

            if s_id is not None and s_id < num_segs:
                if processed_segs[s_id]:
                    continue
                processed_segs[s_id] = True

            if (mid := seg.mid_wall_models):
                mid_update(mid)
            if (other := seg.other_wall_models):
                other_update(other)

    def update_new(self):
        self.walls_to_draw.clear()
        self.mid_walls_to_draw.clear()

        segments = self.segments
        mid_update = self.mid_walls_to_draw.update
        other_update = self.walls_to_draw.update

        num_segs = 1000
        processed_segs = [False] * num_segs

        visible_sector_ids = set()
        v_add = visible_sector_ids.add

        for seg_id in self.segment_ids_to_draw:
            seg = segments[seg_id]
            s_id = seg_id

            v_add(seg.sector_id)
            if seg.back_sector_id is not None:
                v_add(seg.back_sector_id)

            if s_id is not None and s_id < num_segs:
                if processed_segs[s_id]:
                    continue
                processed_segs[s_id] = True

            if (mid := seg.mid_wall_models):
                mid_update(mid)
            if (other := seg.other_wall_models):
                other_update(other)

        self.visible_sector_ids = visible_sector_ids
"""

stmt_old = "r = ViewRendererMock(); r.update_old()"
stmt_new = "r = ViewRendererMock(); r.update_new()"

t_old = timeit.timeit(stmt_old, setup=setup, number=10000)
t_new = timeit.timeit(stmt_new, setup=setup, number=10000)

print(f"Update old: {t_old:.4f}s")
print(f"Update new: {t_new:.4f}s")
