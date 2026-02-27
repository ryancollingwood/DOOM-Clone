
import pytest
from unittest.mock import MagicMock
import sys
import glm

# Mock pyray before importing settings
sys.modules['pyray'] = MagicMock()
sys.modules['raylib'] = MagicMock()
sys.modules['raylib.defines'] = MagicMock()

from data_types import BSPNode, Segment
from bsp.bsp_traverser import BSPTreeTraverser

class MockEngine:
    def __init__(self):
        self.bsp_builder = MagicMock()
        self.bsp_builder.root_node = None
        self.bsp_builder.segments = []
        self.camera = MagicMock()
        self.camera.pos_2d = glm.vec2(0, 0)

def test_traverse_front():
    engine = MockEngine()
    traverser = BSPTreeTraverser(engine)

    root = BSPNode()
    root.splitter_p0 = glm.vec2(5, 0)
    root.splitter_vec = glm.vec2(0, 1) # pointing up
    root.segment_id = 1

    front_node = BSPNode()
    front_node.segment_id = 2
    front_node.splitter_p0 = glm.vec2(10, 0)
    front_node.splitter_vec = glm.vec2(0, 1)
    root.front = front_node

    back_node = BSPNode()
    back_node.segment_id = 3
    back_node.splitter_p0 = glm.vec2(0, 0)
    back_node.splitter_vec = glm.vec2(0, 1)
    root.back = back_node

    traverser.root_node = root

    traverser.pos_2d = glm.vec2(0, 0)
    traverser.update()

    assert traverser.seg_ids_to_draw == [2, 1]

def test_traverse_back_order():
    engine = MockEngine()
    traverser = BSPTreeTraverser(engine)

    root = BSPNode()
    root.splitter_p0 = glm.vec2(5, 0)
    root.splitter_vec = glm.vec2(0, 1) # pointing up
    root.segment_id = 1

    # Front node (2)
    # Splitter at x=12. Viewer (10,0) is LEFT (-2,0) -> Front.
    front_node = BSPNode()
    front_node.segment_id = 2
    front_node.splitter_p0 = glm.vec2(12, 0)
    front_node.splitter_vec = glm.vec2(0, 1)
    root.front = front_node

    # Back node (3)
    # Splitter at x=15. Viewer (10,0) is LEFT (-5,0) -> Front relative to THIS splitter!
    back_node = BSPNode()
    back_node.segment_id = 3
    back_node.splitter_p0 = glm.vec2(15, 0)
    back_node.splitter_vec = glm.vec2(0, 1)
    root.back = back_node

    traverser.root_node = root

    # Viewer is at (10, 0).
    # Root (5, 0). Rel (5, 0). Cross: 5 > 0. Back.
    # Root traversal: traverse(back), traverse(front).

    traverser.pos_2d = glm.vec2(10, 0)
    traverser.update()

    # traverse(back) -> node 3.
    # Rel (-5, 0). Cross < 0. Front.
    # Adds 3.

    # traverse(front) -> node 2.
    # Rel (-2, 0). Cross < 0. Front.
    # Adds 2.

    assert traverser.seg_ids_to_draw == [3, 2]
