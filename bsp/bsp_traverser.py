from settings import *
from data_types import BSPNode, Segment
from utils import is_on_front


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
        self.traverse(self.root_node)

    def traverse(self, node: BSPNode):
        if node:
            self._traverse(node, self.pos_2d.x, self.pos_2d.y, self.seg_ids_to_draw.append)

    def _traverse(self, node: BSPNode, x: float, y: float, append_seg_id):
        # Inline is_on_front logic with scalars and eliminate local variable creation overhead in tight loop
        if (x - node.splitter_p0_x) * node.splitter_vec_y < node.splitter_vec_x * (y - node.splitter_p0_y):
            if node.front is not None: self._traverse(node.front, x, y, append_seg_id)
            #
            append_seg_id(node.segment_id)
            #
            if node.back is not None: self._traverse(node.back, x, y, append_seg_id)
        else:
            if node.back is not None: self._traverse(node.back, x, y, append_seg_id)
            #
            if node.front is not None: self._traverse(node.front, x, y, append_seg_id)
