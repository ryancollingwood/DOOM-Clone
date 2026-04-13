import timeit

setup_code = """
class BSPNode:
    def __init__(self, depth):
        self.segment_id = depth
        self.splitter_p0_x = 0
        self.splitter_p0_y = 0
        self.splitter_vec_x = 1
        self.splitter_vec_y = 1
        if depth > 0:
            self.front = BSPNode(depth - 1)
            self.back = BSPNode(depth - 1)
        else:
            self.front = None
            self.back = None

root_node = BSPNode(10)
x, y = 10, 10
res = []
append_seg_id = res.append

def old_traverse(node, x, y, append_seg_id):
    front = node.front
    back = node.back

    on_front = (x - node.splitter_p0_x) * node.splitter_vec_y < node.splitter_vec_x * (y - node.splitter_p0_y)

    if on_front:
        if front: old_traverse(front, x, y, append_seg_id)
        append_seg_id(node.segment_id)
        if back: old_traverse(back, x, y, append_seg_id)
    else:
        if back: old_traverse(back, x, y, append_seg_id)
        append_seg_id(node.segment_id)
        if front: old_traverse(front, x, y, append_seg_id)

def new_traverse(node, x, y, append_seg_id):
    on_front = (x - node.splitter_p0_x) * node.splitter_vec_y < node.splitter_vec_x * (y - node.splitter_p0_y)

    if on_front:
        if (front := node.front): new_traverse(front, x, y, append_seg_id)
        append_seg_id(node.segment_id)
        if (back := node.back): new_traverse(back, x, y, append_seg_id)
    else:
        if (back := node.back): new_traverse(back, x, y, append_seg_id)
        append_seg_id(node.segment_id)
        if (front := node.front): new_traverse(front, x, y, append_seg_id)
"""

old_code = """
res.clear()
old_traverse(root_node, x, y, append_seg_id)
"""

new_code = """
res.clear()
new_traverse(root_node, x, y, append_seg_id)
"""

print("Old:", timeit.timeit(old_code, setup=setup_code, number=10000))
print("New:", timeit.timeit(new_code, setup=setup_code, number=10000))
