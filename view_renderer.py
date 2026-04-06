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

        # Track processed wall collections to avoid redundant updates
        processed_mid = set()
        processed_other = set()

        # Cache instance attributes and methods to local variables to avoid O(N)
        # LOAD_ATTR bytecode overhead inside the tight update loop.
        segments = self.segments
        mid_update = self.mid_walls_to_draw.update
        other_update = self.walls_to_draw.update
        p_mid_add = processed_mid.add
        p_other_add = processed_other.add

        for seg_id in self.segment_ids_to_draw:
            # walls
            seg = segments[seg_id]

            # Optimization: Check collection truthiness before passing to built-in functions
            # like id() or executing set/dictionary lookups and updates to prevent significant
            # Python function call and hashing overhead for empty data structures.
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
