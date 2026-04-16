from settings import *


class MapRenderer:
    def __init__(self, engine):
        self.engine = engine
        self.camera = engine.camera
        #
        raw_segments = [seg.pos for seg in self.engine.level_data.raw_segments]
        self.x_min, self.y_min, self.x_max, self.y_max = self.get_bounds(raw_segments)
        #
        self.x_out_max, self.y_out_max = self.get_map_bounds()
        #
        self.raw_segments = self.remap_array(raw_segments)
        #
        self.segments = self.remap_array(
            [seg.pos for seg in self.engine.bsp_builder.segments])

        # Pre-calculate normals for segments to avoid redundant computation each frame
        self.segment_normals = [self.calc_normal(p0, p1) for p0, p1 in self.segments]

        self.counter = 0.0
        #
        self.should_draw = False

    def get_map_bounds(self):
        dx = self.x_max - self.x_min
        dy = self.y_max - self.y_min
        #
        delta = min(MAP_WIDTH / dx, MAP_HEIGHT / dy)
        x_out_max = delta * dx
        y_out_max = delta * dy
        return x_out_max, y_out_max

    def draw(self):
        self.draw_raw_segments()
        self.draw_segments()
        self.draw_player()
        self.counter += 0.0025

    def draw_player(self, dist=100):
        x0, y0 = p0 = self.remap_vec2(self.camera.pos_2d)
        x1, y1 = p0 + self.camera.forward.xz * dist
        #
        ray.draw_line_v((x0, y0), (x1, y1), ray.WHITE)
        ray.draw_circle_v((x0, y0), 10, ray.GREEN)

    def draw_segments(self, seg_color=ray.ORANGE):
        segment_ids = self.engine.bsp_traverser.seg_ids_to_draw

        # Optimization: Cache global functions and attributes to local variables
        # to avoid repeated LOAD_GLOBAL/LOAD_ATTR bytecode instructions in the hot loop.
        draw_line = ray.draw_line_v
        draw_circle = ray.draw_circle_v
        color_white = ray.WHITE

        #
        for seg_id in segment_ids:
        # for seg_id in segment_ids[:int(self.counter) % (len(segment_ids) + 1)]:
            # Optimization: Extract .x and .y directly rather than using generator-based sequence
            # unpacking like `(x0, y0), (x1, y1) = p0, p1` which incurs significant iterator overhead.
            p0, p1 = self.segments[seg_id]
            p0_tup = (p0.x, p0.y)
            p1_tup = (p1.x, p1.y)
            #
            draw_line(p0_tup, p1_tup, seg_color)

            # Use pre-calculated normals
            n0, n1 = self.segment_normals[seg_id]
            draw_line((n0.x, n0.y), (n1.x, n1.y), seg_color)
            #
            draw_circle(p0_tup, 2, color_white)
            draw_circle(p1_tup, 2, color_white)

    def calc_normal(self, p0, p1, scale=10):
        p10 = p1 - p0
        normal = normalize(vec2(-p10.y, p10.x))
        n0 = (p0 + p1) * 0.5
        n1 = n0 + normal * scale
        return n0, n1

    def draw_raw_segments(self):
        # Optimization: Cache global functions and attributes to avoid LOAD_GLOBAL/LOAD_ATTR overhead
        draw_line = ray.draw_line_v
        color_darkgray = ray.DARKGRAY

        for p0, p1 in self.raw_segments:
            # Optimization: Extract attributes directly rather than using sequence unpacking
            draw_line((p0.x, p0.y), (p1.x, p1.y), color_darkgray)

    def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
        # Optimization: Pre-calculate constants to avoid repeated math
        x_min, x_max = self.x_min, self.x_max
        y_min, y_max = self.y_min, self.y_max

        # Prevent division by zero if bounds are equal
        dx = x_max - x_min
        dy = y_max - y_min

        cx = (self.x_out_max - out_min) / dx if dx else 0
        cy = (self.y_out_max - out_min) / dy if dy else 0

        # Optimization: Calculate offset constants once to avoid repeating subtraction and multiplication for every point
        ox = out_min - x_min * cx
        oy = out_min - y_min * cy

        # Optimization: Use list comprehensions for faster list construction without the overhead of `.append()` in a loop.
        return [
            (vec2(p0.x * cx + ox, p0.y * cy + oy),
             vec2(p1.x * cx + ox, p1.y * cy + oy))
            for p0, p1 in arr
        ]

    def remap_vec2(self, p: vec2, out_min=MAP_OFFSET):
        x = (p.x - self.x_min) * (self.x_out_max - out_min) / (self.x_max - self.x_min) + out_min
        y = (p.y - self.y_min) * (self.y_out_max - out_min) / (self.y_max - self.y_min) + out_min
        return vec2(x, y)

    def remap_x(self, x, out_min=MAP_OFFSET):
        out_max = self.x_out_max
        return (x - self.x_min) * (out_max - out_min) / (self.x_max - self.x_min) + out_min

    def remap_y(self, y, out_min=MAP_OFFSET):
        out_max = self.y_out_max
        return (y - self.y_min) * (out_max - out_min) / (self.y_max - self.y_min) + out_min

    @staticmethod
    def get_bounds(segments: list[tuple[vec2]]):
        inf = float('inf')

        if not segments:
            return inf, inf, -inf, -inf

        x_min, y_min, x_max, y_max = inf, inf, -inf, -inf

        # Optimization: Unpack vec2 attributes into local variables and use simple
        # 'if' branches instead of chained nested ternary operators to avoid
        # repeated attribute lookups and complex branching overhead.
        for p0, p1 in segments:
            p0x, p0y = p0.x, p0.y
            p1x, p1y = p1.x, p1.y

            if p0x < x_min: x_min = p0x
            if p1x < x_min: x_min = p1x
            if p0x > x_max: x_max = p0x
            if p1x > x_max: x_max = p1x

            if p0y < y_min: y_min = p0y
            if p1y < y_min: y_min = p1y
            if p0y > y_max: y_max = p0y
            if p1y > y_max: y_max = p1y

        return x_min, y_min, x_max, y_max
