from settings import *
from data_types import BSPNode


class BSPTreeTraverser:
    def __init__(self, engine):
        self.engine = engine
        self.root_node = engine.bsp_builder.root_node
        self.segments = engine.bsp_builder.segments

        self.camera = engine.camera
        self.pos_2d = self.camera.pos_2d
        #
        self.seg_ids_to_draw = []
        # Optimization: Using a pre-allocated boolean list to track processed sector IDs
        # avoids the expensive hashing overhead of Python sets in the tight traversal loops.
        self.visible_sector_ids = []
        self.num_sectors = len(engine.level_data.sectors)
        self.visible_sector_bool = [False] * self.num_sectors
        self.masked_seg_ids_to_draw = []

    def update(self):
        self.seg_ids_to_draw.clear()
        self.masked_seg_ids_to_draw.clear()

        # Fast reset of boolean array using previously visible IDs
        bool_arr = self.visible_sector_bool
        for i in self.visible_sector_ids:
            bool_arr[i] = False
        self.visible_sector_ids.clear()

        self.traverse(self.root_node)

    def traverse(self, node: BSPNode):
        if node:
            self._traverse(node, self.pos_2d.x, self.pos_2d.y, self.seg_ids_to_draw.append, self.visible_sector_bool, self.visible_sector_ids.append)

    def _traverse(self, node: BSPNode, x: float, y: float, append_seg_id, visible_bool, visible_ids_append):
        # Inline is_on_front logic with scalars to avoid vec2 object creation in tight loop
        # Cache node.front and node.back to avoid repeated attribute lookups
        front = node.front
        back = node.back

        # Optimization: Mathematically simplified the cross product inequality and cached
        # the constant right side (`node.splitter_c`) during tree building. This drops 2 subtractions
        # per traversal node evaluation in the hot path.
        if x * node.splitter_vec_y - y * node.splitter_vec_x < node.splitter_c:
            if front:
                self._traverse(front, x, y, append_seg_id, visible_bool, visible_ids_append)
            # Optimization: Track sectors of traversed nodes to ensure all flats
            # in the BSP sub-tree are drawn, even if walls are culled.
            # Inlined tracking logic to bypass function call wrapper overhead.
            sec_id = node.sector_id
            if not visible_bool[sec_id]:
                visible_bool[sec_id] = True
                visible_ids_append(sec_id)

            back_sec_id = node.back_sector_id
            if back_sec_id is not None and not visible_bool[back_sec_id]:
                visible_bool[back_sec_id] = True
                visible_ids_append(back_sec_id)

            append_seg_id(node.segment_id)
            #
            if back:
                self._traverse(back, x, y, append_seg_id, visible_bool, visible_ids_append)
        else:
            if back:
                self._traverse(back, x, y, append_seg_id, visible_bool, visible_ids_append)
            #
            if front:
                self._traverse(front, x, y, append_seg_id, visible_bool, visible_ids_append)
