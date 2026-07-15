from settings import *
from models import Models
from data_types import *


class ViewRenderer:
    def __init__(self, engine):
        self.engine = engine
        self.map_renderer = self.engine.map_renderer
        #
        self.segments: list[Segment] = engine.bsp_builder.segments
        self.camera = engine.camera
        self.segment_ids_to_draw = self.engine.bsp_traverser.seg_ids_to_draw
        self.visible_sector_ids = self.engine.bsp_traverser.visible_sector_ids
        self.sectors = self.engine.level_data.sectors
        #
        self.models = Models(engine)
        self.wall_models = self.models.wall_models
        self.flat_models = self.models.flat_models
        #
        # Optimization: use a list instead of a set for walls_to_draw.
        # Deduplication is handled efficiently by tracking processed segment IDs
        # avoiding hashing overhead for potentially thousands of frames.
        self.walls_to_draw = []
        self.mid_walls_to_draw = []
        #
        self.screen_tint = WHITE_COLOR
        #
        # Optimization: Pre-allocate boolean list once per instance to track processed segments
        # avoiding repeated list allocations inside the hot update path.
        self.processed_segs_bool = [False] * self.engine.level_data.seg_id_counter
        self.processed_segs_ids = []

    def update(self):
        self.walls_to_draw.clear()
        self.mid_walls_to_draw.clear()

        # Cache instance attributes and methods to local variables to avoid O(N)
        # LOAD_ATTR bytecode overhead inside the tight update loop.
        segments = self.segments
        mid_extend = self.mid_walls_to_draw.extend
        other_extend = self.walls_to_draw.extend

        processed_segs = self.processed_segs_bool
        processed_ids = self.processed_segs_ids

        # Fast reset
        for i in processed_ids:
            processed_segs[i] = False
        processed_ids.clear()

        processed_ids_append = processed_ids.append
        num_segs = self.engine.level_data.seg_id_counter

        for seg_id in self.segment_ids_to_draw:
            # walls
            seg = segments[seg_id]
            s_id = seg.seg_id

            # Optimization: Flatten conditional nesting to avoid duplicate bytecode
            # execution blocks and nested branch depth, skipping early if already processed.
            # Since segment IDs are guaranteed to be populated by the level builder,
            # we can use them to efficiently skip processing walls for split segments.
            # However, if s_id is somehow None (e.g. newly instantiated without threading ID),
            # fall back to evaluation to ensure no geometry is lost.
            if s_id is not None and s_id < num_segs:
                if processed_segs[s_id]:
                    continue
                processed_segs[s_id] = True
                processed_ids_append(s_id)

            # Optimization: Extract attributes to local variables. The standard assignment
            # evaluates slightly faster than the walrus operator in this extremely hot loop.
            mid = seg.mid_wall_models
            if mid:
                mid_extend(mid)
            other = seg.other_wall_models
            if other:
                other_extend(other)

    def draw(self):
        # Cache screen_tint and pre-calculate shade_tint to avoid O(N) attribute lookups and conditional checks in the inner render loops
        screen_tint = self.screen_tint
        shade_tint = SHADING_DARK_COLOR if self.map_renderer.should_draw else SHADING_COLOR

        # Cache global function and constant into local variables to avoid expensive
        # LOAD_GLOBAL and LOAD_ATTR bytecode overhead inside the tight rendering loop.
        draw_model = ray.draw_model
        v_zero = VEC3_ZERO

        # draw flats
        # Optimization: Loop over visible_sector_ids instead of all sectors to prevent redundant rendering of floors and ceilings
        # Cache flat_models to avoid LOAD_ATTR bytecode overhead inside the high-frequency rendering loop.
        flat_models = self.flat_models
        for sec_id in self.visible_sector_ids:
            #
            floor, ceil = flat_models[sec_id]
            draw_model(ceil.model, v_zero, 1.0, screen_tint)
            draw_model(floor.model, v_zero, 1.0, screen_tint)

        # draw walls
        for wall in self.walls_to_draw:
            # Inline conditional tint expression to avoid variable assignment overhead
            draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)

        # draw portal_mid walls from back to front
        # Reverse list directly
        for wall in reversed(self.mid_walls_to_draw):
            draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)

    def update_screen_tint(self):
        self.screen_tint = (
            DARK_GRAY_COLOR if self.map_renderer.should_draw else WHITE_COLOR
        )
