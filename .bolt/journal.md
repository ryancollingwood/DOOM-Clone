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
