import cProfile
from main import App
import raylib.defines
import pyray as ray
import timeit

s1 = """
def update(self):
    self.walls_to_draw.clear()
    self.mid_walls_to_draw.clear()

    # Track processed wall collections to avoid redundant updates
    processed_mid = set()
    processed_other = set()

    for seg_id in self.segment_ids_to_draw:
        # walls
        seg = self.segments[seg_id]

        mid_id = id(seg.mid_wall_models)
        if mid_id not in processed_mid:
            self.mid_walls_to_draw.update(seg.mid_wall_models)
            processed_mid.add(mid_id)

        other_id = id(seg.other_wall_models)
        if other_id not in processed_other:
            self.walls_to_draw.update(seg.other_wall_models)
            processed_other.add(other_id)
"""
