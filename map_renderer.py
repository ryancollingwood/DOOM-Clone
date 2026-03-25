from settings import *
import numpy as np


class MapRenderer:
    def __init__(self, engine):
        self.engine = engine
        self.camera = engine.camera
        #
        raw_segments = np.array([seg.pos for seg in self.engine.level_data.raw_segments])
        self.x_min, self.y_min, self.x_max, self.y_max = self.get_bounds(raw_segments)
        #
        self.x_out_max, self.y_out_max = self.get_map_bounds()
        #
        self.raw_segments = self.remap_array(raw_segments)
        #
        self.segments = self.remap_array(
            np.array([seg.pos for seg in self.engine.bsp_builder.segments]))

        # Pre-calculate normals for segments to avoid redundant computation each frame
        self.segment_normals = self.calc_normals(self.segments)

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
        #
        for seg_id in segment_ids:
        # for seg_id in segment_ids[:int(self.counter) % (len(segment_ids) + 1)]:
            p0, p1 = self.segments[seg_id]
            x0, y0 = p0
            x1, y1 = p1
            #
            ray.draw_line_v((float(x0), float(y0)), (float(x1), float(y1)), seg_color)

            # Use pre-calculated normals
            n0, n1 = self.segment_normals[seg_id]
            ray.draw_line_v((float(n0[0]), float(n0[1])), (float(n1[0]), float(n1[1])), seg_color)
            #
            ray.draw_circle_v((float(x0), float(y0)), 2, ray.WHITE)
            ray.draw_circle_v((float(x1), float(y1)), 2, ray.WHITE)

    def calc_normals(self, segments, scale=10):
        if len(segments) == 0:
            return np.array([])
        p0 = segments[:, 0, :]
        p1 = segments[:, 1, :]
        p10 = p1 - p0
        normals = np.empty_like(p10)
        normals[:, 0] = -p10[:, 1]
        normals[:, 1] = p10[:, 0]

        # normalize
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        # Avoid division by zero
        lengths[lengths == 0] = 1.0
        normals = normals / lengths

        n0 = (p0 + p1) * 0.5
        n1 = n0 + normals * scale

        # return as an array of shape (N, 2, 2) where N is number of segments
        return np.stack([n0, n1], axis=1)

    def draw_raw_segments(self):
        for p0, p1 in self.raw_segments:
            x0, y0 = p0
            x1, y1 = p1
            ray.draw_line_v((float(x0), float(y0)), (float(x1), float(y1)), ray.DARKGRAY)

    def remap_array(self, arr: np.ndarray, out_min=MAP_OFFSET):
        if len(arr) == 0:
            return arr

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

        # Vectorized mapping over numpy array
        remapped = np.empty_like(arr)
        remapped[:, :, 0] = arr[:, :, 0] * cx + ox
        remapped[:, :, 1] = arr[:, :, 1] * cy + oy

        return remapped

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
    def get_bounds(segments: np.ndarray):
        inf = float('inf')

        if len(segments) == 0:
            return inf, inf, -inf, -inf

        # Optimization: Use numpy min/max over the whole array
        x_min = np.min(segments[:, :, 0])
        x_max = np.max(segments[:, :, 0])
        y_min = np.min(segments[:, :, 1])
        y_max = np.max(segments[:, :, 1])

        return x_min, y_min, x_max, y_max
