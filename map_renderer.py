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

        # Optimization: Pre-calculate remap coefficients for the default MAP_OFFSET once,
        # saving repeated calculations in remap_vec2, remap_x, and remap_y.
        out_min = MAP_OFFSET
        dx = self.x_max - self.x_min
        dy = self.y_max - self.y_min
        self.dx = dx
        self.dy = dy
        self.cx = (self.x_out_max - out_min) / dx if dx else 0
        self.cy = (self.y_out_max - out_min) / dy if dy else 0
        self.ox = out_min - self.x_min * self.cx
        self.oy = out_min - self.y_min * self.cy

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

        # Optimization: Cache global functions and attributes to local variables.
        # Bypass Python sequence unpacking overhead over custom objects by explicit extraction.
        draw_line_v = ray.draw_line_v
        draw_circle_v = ray.draw_circle_v
        WHITE = ray.WHITE

        # Optimization: Cache self.segments and self.segment_normals to avoid LOAD_ATTR
        # bytecode execution per iteration
        segments = self.segments
        segment_normals = self.segment_normals

        for seg_id in segment_ids:
        # for seg_id in segment_ids[:int(self.counter) % (len(segment_ids) + 1)]:
            p0, p1 = segments[seg_id]
            x0, y0 = p0.x, p0.y
            x1, y1 = p1.x, p1.y
            #
            draw_line_v((x0, y0), (x1, y1), seg_color)

            # Use pre-calculated normals
            n0, n1 = segment_normals[seg_id]
            draw_line_v((n0.x, n0.y), (n1.x, n1.y), seg_color)
            #
            draw_circle_v((x0, y0), 2, WHITE)
            draw_circle_v((x1, y1), 2, WHITE)

    def calc_normal(self, p0, p1, scale=10):
        p10 = p1 - p0
        normal = normalize(vec2(-p10.y, p10.x))
        n0 = (p0 + p1) * 0.5
        n1 = n0 + normal * scale
        return n0, n1

    def draw_raw_segments(self):
        # Optimization: Cache global functions and attributes to local variables.
        # Bypass Python sequence unpacking overhead over custom objects by explicit extraction.
        draw_line_v = ray.draw_line_v
        DARKGRAY = ray.DARKGRAY
        for p0, p1 in self.raw_segments:
            draw_line_v((p0.x, p0.y), (p1.x, p1.y), DARKGRAY)

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
        # Optimization: Use pre-calculated remapping coefficients for the default out_min
        if out_min == MAP_OFFSET:
            return vec2(p.x * self.cx + self.ox, p.y * self.cy + self.oy)

        dx = self.dx
        dy = self.dy
        cx = (self.x_out_max - out_min) / dx if dx else 0
        cy = (self.y_out_max - out_min) / dy if dy else 0
        ox = out_min - self.x_min * cx
        oy = out_min - self.y_min * cy
        return vec2(p.x * cx + ox, p.y * cy + oy)

    def remap_x(self, x, out_min=MAP_OFFSET):
        if out_min == MAP_OFFSET:
            return x * self.cx + self.ox
        out_max = self.x_out_max
        dx = self.dx
        return (x - self.x_min) * (out_max - out_min) / dx if dx else out_min

    def remap_y(self, y, out_min=MAP_OFFSET):
        if out_min == MAP_OFFSET:
            return y * self.cy + self.oy
        out_max = self.y_out_max
        dy = self.dy
        return (y - self.y_min) * (out_max - out_min) / dy if dy else out_min

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
