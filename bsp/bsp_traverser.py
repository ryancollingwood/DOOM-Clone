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
        self._traverse(self.root_node, self.pos_2d.x, self.pos_2d.y)

    def traverse(self, node: BSPNode):
        """Deprecated: Use _traverse(node, x, y) for better performance."""
        self._traverse(node, self.pos_2d.x, self.pos_2d.y)

    def _traverse(self, node: BSPNode, pos_x: float, pos_y: float):
        if node is None:
            return None

        # Inline logic equivalent to:
        # on_front = is_on_front(self.pos_2d - node.splitter_p0, node.splitter_vec)
        on_front = (pos_x - node.splitter_p0.x) * node.splitter_vec.y < node.splitter_vec.x * (pos_y - node.splitter_p0.y)
        #
        if on_front:
            self._traverse(node.front, pos_x, pos_y)
            #
            self.seg_ids_to_draw.append(node.segment_id)
            #
            self._traverse(node.back, pos_x, pos_y)
        else:
            self._traverse(node.back, pos_x, pos_y)
            #
            self._traverse(node.front, pos_x, pos_y)
