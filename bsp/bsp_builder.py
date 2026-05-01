from settings import *
from data_types import Segment, BSPNode
from copy import copy
import random


class BSPTreeBuilder:
    def __init__(self, engine):
        self.engine = engine
        self.raw_segments = engine.level_data.raw_segments
        #
        self.root_node = BSPNode()
        #
        self.segments = []  # segments created during BSP tree creation
        self.seg_id = 0
        #
        seed = self.engine.level_data.settings['seed']
        random.seed(seed)
        random.shuffle(self.raw_segments)
        #
        self.num_front, self.num_back, self.num_splits = 0, 0, 0
        self.build_bsp_tree(self.root_node, self.raw_segments)
        #
        print('num_front:', self.num_front)
        print('num_back:', self.num_back)
        print('num_splits', self.num_splits)

    def split_space(self, node: BSPNode, input_segments: list[Segment]):
        splitter_seg = input_segments[0]
        splitter_pos = splitter_seg.pos
        splitter_vec = splitter_seg.vector

        node.splitter_vec = splitter_vec
        node.splitter_p0 = splitter_pos[0]
        node.splitter_p1 = splitter_pos[1]

        # Optimization: Cache scalar values to avoid vec2 lookups in BSP traverse loop
        node.splitter_p0_x = splitter_pos[0].x
        node.splitter_p0_y = splitter_pos[0].y
        node.splitter_vec_x = splitter_vec.x
        node.splitter_vec_y = splitter_vec.y

        front_segs, back_segs = [], []

        # Optimization: cache frequently called list.append methods to avoid attribute lookup overhead
        append_front = front_segs.append
        append_back = back_segs.append

        for segment in input_segments[1:]:
            #
            segment_start = segment.pos[0]
            segment_end = segment.pos[1]
            segment_vector = segment.vector

            # Optimization: Inline cross_2d and scalar mathematical evaluation to avoid function call
            # and new object (vec2) creation overheads for each segment in the recursive loop.
            dx = segment_start.x - node.splitter_p0_x
            dy = segment_start.y - node.splitter_p0_y

            numerator = dx * node.splitter_vec_y - node.splitter_vec_x * dy
            denominator = node.splitter_vec_x * segment_vector.y - segment_vector.x * node.splitter_vec_y

            # Optimization: Avoid abs() function call overhead using inline conditional expressions
            abs_denom = denominator if denominator >= 0 else -denominator
            abs_num = numerator if numerator >= 0 else -numerator

            # if the denominator is zero the lines are parallel
            denominator_is_zero = abs_denom < EPS

            # segments are collinear if they are parallel and the numerator is zero
            numerator_is_zero = abs_num < EPS
            #
            if denominator_is_zero and numerator_is_zero:
                append_front(segment)
                continue

            if not denominator_is_zero:
                # intersection is the point on a line segment where the line divides it
                intersection = numerator / denominator

                # segments that are not parallel and t is in (0,1) should be divided
                if 0.0 < intersection < 1.0:
                    self.num_splits += 1
                    #
                    intersection_point = segment_start + intersection * segment_vector

                    r_segment = copy(segment)
                    r_segment.seg_id = segment.seg_id
                    r_segment.pos = segment_start, intersection_point
                    r_segment.vector = r_segment.pos[1] - r_segment.pos[0]
                    #
                    l_segment = copy(segment)
                    l_segment.seg_id = segment.seg_id
                    l_segment.pos = intersection_point, segment_end
                    l_segment.vector = l_segment.pos[1] - l_segment.pos[0]

                    if numerator > 0:
                        l_segment, r_segment = r_segment, l_segment
                    #
                    append_front(r_segment)
                    append_back(l_segment)
                    continue

            if numerator < 0 or (numerator_is_zero and denominator > 0):
                append_front(segment)
            #
            elif numerator > 0 or (numerator_is_zero and denominator < 0):
                append_back(segment)

        self.add_segment(splitter_seg, node)
        return front_segs, back_segs

    def add_segment(self, splitter_seg: Segment, node: BSPNode):
        self.segments.append(splitter_seg)
        node.segment_id = self.seg_id
        #
        self.seg_id += 1

    def build_bsp_tree(self, node: BSPNode, input_segments: list[Segment]):
        if not input_segments:
            return None
        #
        front_segs, back_segs = self.split_space(node, input_segments)

        if back_segs:
            self.num_back += 1
            #
            node.back = BSPNode()
            self.build_bsp_tree(node.back, back_segs)

        if front_segs:
            self.num_front += 1
            #
            node.front = BSPNode()
            self.build_bsp_tree(node.front, front_segs)
