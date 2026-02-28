import timeit

class Node:
    def __init__(self, segment_id, front=None, back=None):
        self.front = front
        self.back = back
        self.segment_id = segment_id

        # Adding splitter data
        self.splitter_p0 = type('obj', (object,), {'x': 1.0, 'y': 1.0})()
        self.splitter_vec = type('obj', (object,), {'x': 2.0, 'y': 3.0})()

# Create a small tree
node3 = Node(3)
node2 = Node(2)
node1 = Node(1, node2, node3)

class Camera:
    def __init__(self):
        self.pos_2d = type('obj', (object,), {'x': 5.0, 'y': 5.0})()

class TraverserOriginal:
    def __init__(self):
        self.camera = Camera()
        self.pos_2d = self.camera.pos_2d
        self.seg_ids_to_draw = []

    def traverse(self, node):
        if node is None:
            return None

        # Inline is_on_front for accurate comparison of the logic itself
        vec_0_x = self.pos_2d.x - node.splitter_p0.x
        vec_0_y = self.pos_2d.y - node.splitter_p0.y
        vec_1_x = node.splitter_vec.x
        vec_1_y = node.splitter_vec.y

        on_front = vec_0_x * vec_1_y < vec_1_x * vec_0_y

        if on_front:
            self.traverse(node.front)
            self.seg_ids_to_draw.append(node.segment_id)
            self.traverse(node.back)
        else:
            self.traverse(node.back)
            self.seg_ids_to_draw.append(node.segment_id)
            self.traverse(node.front)

class TraverserOptimized:
    def __init__(self):
        self.camera = Camera()
        self.pos_2d = self.camera.pos_2d
        self.seg_ids_to_draw = []

    def traverse(self, node):
        if node is None: return
        self._traverse(node, self.pos_2d.x, self.pos_2d.y)

    def _traverse(self, node, x, y):
        if node is None:
            return

        dx = x - node.splitter_p0.x
        dy = y - node.splitter_p0.y
        vx = node.splitter_vec.x
        vy = node.splitter_vec.y

        if dx * vy < vx * dy:
            self._traverse(node.front, x, y)
            self.seg_ids_to_draw.append(node.segment_id)
            self._traverse(node.back, x, y)
        else:
            self._traverse(node.back, x, y)
            self.seg_ids_to_draw.append(node.segment_id)
            self._traverse(node.front, x, y)

def run_orig():
    t = TraverserOriginal()
    t.traverse(node1)

def run_opt():
    t = TraverserOptimized()
    t.traverse(node1)

print("Original Traverser:", timeit.timeit("run_orig()", globals=globals(), number=100000))
print("Optimized Traverser:", timeit.timeit("run_opt()", globals=globals(), number=100000))
