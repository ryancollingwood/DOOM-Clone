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
        if node is None:
            return None
        self._traverse(node, self.pos_2d.x, self.pos_2d.y)

    def _traverse(self, node: BSPNode, x: float, y: float):
        if node is None:
            return None

        # Inline is_on_front logic with scalars to avoid vec2 object creation in tight loop
        dx = x - node.splitter_p0.x
        dy = y - node.splitter_p0.y
        vx = node.splitter_vec.x
        vy = node.splitter_vec.y
        on_front = dx * vy < vx * dy

        #
        if on_front:
            self._traverse(node.front, x, y)
            #
            self.seg_ids_to_draw.append(node.segment_id)
            #
            self._traverse(node.back, x, y)
        else:
            self._traverse(node.back, x, y)
            #
            self._traverse(node.front, x, y)
