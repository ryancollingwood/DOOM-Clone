from settings import *
from data_types import BSPNode, Segment


class BSPTreeTraverser:
    def __init__(self, engine):
        self.engine = engine
        self.root_node = engine.bsp_builder.root_node
        self.segments = engine.bsp_builder.segments

        self.camera = engine.camera
        self.pos_2d = self.camera.pos_2d
        #
        self.seg_ids_to_draw = []
        self.masked_seg_ids_to_draw = []

    def update(self):
        self.seg_ids_to_draw.clear()
        self.masked_seg_ids_to_draw.clear()
        px, py = self.pos_2d.x, self.pos_2d.y
        self.traverse(self.root_node, px, py)

    def traverse(self, node: BSPNode, px, py):
        if node is None:
            return None

        on_front = (px - node.splitter_p0.x) * node.splitter_vec.y < \
                   node.splitter_vec.x * (py - node.splitter_p0.y)
        #
        if on_front:
            self.traverse(node.front, px, py)
            #
            self.seg_ids_to_draw.append(node.segment_id)
            #
            self.traverse(node.back, px, py)
        else:
            self.traverse(node.back, px, py)
            #
            self.traverse(node.front, px, py)
