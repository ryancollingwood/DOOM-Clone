# Bolt's Journal

## 2024-05-23: Redundant Wall Updates in ViewRenderer

### Problem
The `ViewRenderer.update` method iterates over all visible segments to populate `walls_to_draw` (set) and `mid_walls_to_draw` (dict). Due to BSP splitting, a single original wall segment can be split into multiple smaller segments for visibility determination. However, these split segments share the same `wall_model_ids`, `mid_wall_models`, and `other_wall_models` collections (via shallow copy).

As a result, `ViewRenderer.update` repeatedly calls `update()` on the `walls_to_draw` set and `mid_walls_to_draw` dict with the exact same collections for every split segment derived from the same original wall. This is redundant work (hashing and checking for existence).

### Optimization
Use `id()` to track processed wall collections within the frame. Maintain a set of `processed_ids` and skip `update()` calls if the collection has already been processed.

### Impact
- Reduces the complexity of `ViewRenderer.update` from O(N_visible_splits * M_walls) to O(N_visible_raw * M_walls).
- In synthetic benchmarks with high splitting (50 splits per segment), this yielded a ~2x speedup. Real-world gains will depend on scene complexity and BSP depth.

### 2024-05-24: Optimize BSP Tree Traversal using Scalar Caching
**Problem**: The `_traverse` method in `BSPTreeTraverser` is called extremely frequently (hundreds of thousands of times per frame). Inside the loop, vectors are accessed multiple times to compute the cross product (e.g. `node.splitter_p0.x`). This causes significant overhead due to object property lookups in Python.

**Optimization**:
Modified `BSPNode` to store scalar versions of these attributes (`splitter_p0_x`, etc.). `BSPTreeBuilder.split_space` was updated to initialize these scalars.
`BSPTreeTraverser._traverse` was updated to use these scalars, avoiding object lookups inside the tight loop. Additionally, `self.seg_ids_to_draw.append` was passed as a local parameter to avoid the attribute and method lookup.

**Impact**:
Reduced the `test_perf3` 5000-frame (logic only) profile time from 1.50s to 1.36s (~10% performance gain).

### 2024-05-25: Optimize BSP Tree Traversal using Inlining and Node Caching
**Problem**: The `_traverse` method in `BSPTreeTraverser` is the inner loop for determining what gets drawn and is heavily recursive. Calling `if node is None:` constantly added unnecessary call overhead for missing leaf nodes.

**Optimization**:
Modified `BSPTreeTraverser` to inline the `on_front` cross product condition without creating intermediate local variables like `dx`, `dy`. Cached the `node.front` and `node.back` variables, and replaced the base case check with pre-checks (`if front: self._traverse(...)`) to prevent recursing on `None`.

**Impact**:
Using a deep synthetic tree benchmark (100,000 runs), execution time dropped from 85.8 seconds to 73.4 seconds, yielding an approximate 14.4% performance gain on the inner loop.

### 2024-05-26: MapRenderer remap_array Optimization
**Problem**: The `MapRenderer` dynamically translates vector space for map drawing. The function `remap_array` maps every vector through several nested class methods (`remap_vec2`, `remap_x`, `remap_y`). This introduces substantial per-point function call overhead and repeats math.

**Optimization**:
Inlined the coordinate math directly into the `remap_array` loops and calculated scalar constants `cx` and `cy` ahead of time to avoid performing identical divisions for every coordinate in every vector array element.

**Impact**:
Micro-benchmark testing indicated that inlining and caching scalar math for point mapping yields roughly a 30% execution time decrease (time taken dropped from 2.13s to 1.47s for 1000 items in a tight loop).

### 2024-05-27: Optimize `FlatModel.get_indices` with O(1) Dictionary Lookup
**Problem**: The `FlatModel.get_indices` method in `models.py` uses `outline_verts.index((v.x, v.y))` inside a nested loop for every triangle vertex. The `.index()` method on a Python list has O(N) complexity, resulting in roughly O(N_triangles * N_verts) complexity for the method. When triangulating complex sectors, this caused significant slowdowns.

**Optimization**:
Created a pre-computed dictionary mapping vertex coordinate tuples `(x, y)` to their index outside the loop (`{vert: i for i, vert in enumerate(outline_verts)}`). Modified the inner loop to use this dictionary for an O(1) lookup instead.

**Impact**:
In synthetic benchmarking with 1000 outline vertices and 2000 triangles, the execution time over 100 iterations dropped from 11.47 seconds to 0.22 seconds (a ~50x speedup). This significantly accelerates the mesh generation phase for levels with large, complex sector geometry.

### 2024-05-28: Optimize BSPTreeBuilder `split_space` Cross Product
**Problem**: During the building of the BSP tree, `split_space` repeatedly checks segments against splitters using `cross_2d((segment_start - splitter_pos[0]), splitter_vec)`. The `segment_start - splitter_pos[0]` operation instantiates a new `vec2` object for every comparison, and the subsequent `cross_2d` call has function call and attribute lookup overhead.

**Optimization**:
Inlined the `cross_2d` cross product math and vector difference calculations directly in `split_space` to avoid vec2 object creation and reduce function call overhead.
```python
dx = segment_start.x - splitter_pos[0].x
dy = segment_start.y - splitter_pos[0].y
numerator = dx * splitter_vec.y - splitter_vec.x * dy
```

**Impact**:
Micro-benchmarking a synthetic inner loop with identical cross product calculations showed execution time halving from 1.07 seconds to 0.53 seconds for 1,000,000 iterations.
