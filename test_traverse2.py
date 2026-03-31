import timeit

s1 = """
class BSPNode:
    __slots__ = ('front', 'back', 'splitter_p0_x', 'splitter_p0_y', 'splitter_vec_x', 'splitter_vec_y', 'segment_id')
    def __init__(self, id):
        self.front = None
        self.back = None
        self.splitter_p0_x = 0
        self.splitter_p0_y = 0
        self.splitter_vec_x = 1
        self.splitter_vec_y = 1
        self.segment_id = id

root = BSPNode(0)
curr = root
for i in range(1, 100):
    curr.front = BSPNode(i)
    curr = curr.front

def traverse(node, x, y, append):
    front = node.front
    back = node.back

    if (x - node.splitter_p0_x) * node.splitter_vec_y < node.splitter_vec_x * (y - node.splitter_p0_y):
        if front is not None: traverse(front, x, y, append)
        append(node.segment_id)
        if back is not None: traverse(back, x, y, append)
    else:
        if back is not None: traverse(back, x, y, append)
        append(node.segment_id)
        if front is not None: traverse(front, x, y, append)
"""

s2 = """
class BSPNode:
    __slots__ = ('front', 'back', 'splitter_p0_x', 'splitter_p0_y', 'splitter_vec_x', 'splitter_vec_y', 'segment_id')
    def __init__(self, id):
        self.front = None
        self.back = None
        self.splitter_p0_x = 0
        self.splitter_p0_y = 0
        self.splitter_vec_x = 1
        self.splitter_vec_y = 1
        self.segment_id = id

root = BSPNode(0)
curr = root
for i in range(1, 100):
    curr.front = BSPNode(i)
    curr = curr.front

def traverse(node, x, y, append):
    if (x - node.splitter_p0_x) * node.splitter_vec_y < node.splitter_vec_x * (y - node.splitter_p0_y):
        if node.front is not None: traverse(node.front, x, y, append)
        append(node.segment_id)
        if node.back is not None: traverse(node.back, x, y, append)
    else:
        if node.back is not None: traverse(node.back, x, y, append)
        append(node.segment_id)
        if node.front is not None: traverse(node.front, x, y, append)
"""

print(timeit.timeit("res=[]; traverse(root, 10, 10, res.append)", setup=s1, number=10000))
print(timeit.timeit("res=[]; traverse(root, 10, 10, res.append)", setup=s2, number=10000))
