from settings import *
from models import Models, WallModel
from data_types import *


class ViewRenderer:
    def __init__(self, engine):
        self.engine = engine
        self.map_renderer = self.engine.map_renderer
        #
        self.segments: list[Segment] = engine.bsp_builder.segments
        self.camera = engine.camera
        self.segment_ids_to_draw = self.engine.bsp_traverser.seg_ids_to_draw
        self.sectors = self.engine.level_data.sectors
        #
        self.models = Models(engine)
        self.wall_models = self.models.wall_models
        self.flat_models = self.models.flat_models
        #
        self.walls_to_draw = set()
        self.mid_walls_to_draw = {}  # as ordered set
        #
        self.screen_tint = WHITE_COLOR

    def update(self):
        self.walls_to_draw.clear()
        self.mid_walls_to_draw.clear()

        # Cache instance attributes and methods to local variables to avoid O(N)
        # LOAD_ATTR bytecode overhead inside the tight update loop.
        segments = self.segments
        mid_update = self.mid_walls_to_draw.update
        other_update = self.walls_to_draw.update

        # Track processed segments by their unique original ID to avoid redundant updates
        processed_segs = set()
        p_segs_add = processed_segs.add

        for seg_id in self.segment_ids_to_draw:
            # walls
            seg = segments[seg_id]
            s_id = seg.seg_id

            # Since segment IDs are guaranteed to be populated by the level builder,
            # we can use them to efficiently skip processing walls for split segments.
            # However, if s_id is somehow None (e.g. newly instantiated without threading ID),
            # fall back to object id() mapping to ensure no geometry is lost.
            if s_id is not None:
                if s_id not in processed_segs:
                    if (mid := seg.mid_wall_models):
                        mid_update(mid)
                    if (other := seg.other_wall_models):
                        other_update(other)
                    p_segs_add(s_id)
            else:
                if (mid := seg.mid_wall_models):
                    mid_update(mid)
                if (other := seg.other_wall_models):
                    other_update(other)

    def draw(self):
        # Cache screen_tint and pre-calculate shade_tint to avoid O(N) attribute lookups and conditional checks in the inner render loops
        screen_tint = self.screen_tint
        shade_tint = SHADING_DARK_COLOR if self.map_renderer.should_draw else SHADING_COLOR

        # Cache global function and constant into local variables to avoid expensive
        # LOAD_GLOBAL and LOAD_ATTR bytecode overhead inside the tight rendering loop.
        draw_model = ray.draw_model
        v_zero = VEC3_ZERO

        # draw flats
        for sec_id in self.sectors:
            #
            floor, ceil = self.flat_models[sec_id]
            draw_model(ceil.model, v_zero, 1.0, screen_tint)
            draw_model(floor.model, v_zero, 1.0, screen_tint)

        # draw walls
        for wall in self.walls_to_draw:
            # Inline conditional tint expression to avoid variable assignment overhead
            draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)

        # draw portal_mid walls from back to front
        # Reverse dict values directly (supported in Python 3.8+)
        for wall in reversed(self.mid_walls_to_draw.values()):
            draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)

    def update_screen_tint(self):
        self.screen_tint = (
            DARK_GRAY_COLOR if self.map_renderer.should_draw else WHITE_COLOR
        )
