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

### 2024-05-28: Overhead of `min()` and `max()` Function Calls in Hot Paths
**Problem**: The `WallModel.get_wall_height_data` function calculates sector portal bounds and is executed frequently during mesh generation. It used `min()` and `max()` built-ins to compute limits, introducing noticeable function call overhead for simple numeric comparisons.
**Optimization**: Replaced standard `min()` and `max()` usage with Python ternary operators (e.g., `(bottom, top) if bottom < top else (top, bottom)` and cached `self.wall_type` to a local variable).
**Impact**: Profiling 100,000 runs using `timeit` showed an execution time drop from ~0.148 seconds to ~0.048 seconds, yielding roughly a **3x speedup** on height calculation by avoiding expensive function allocations and repeated lookups.

### 2024-05-29: BSPTreeBuilder split_space Optimization
**Problem**: The `BSPTreeBuilder.split_space` method creates new `vec2` instances to compute vectors and calls external `cross_2d` and `abs` functions inside a tight inner loop (iterating through segments being split). This caused significant Python object allocation and function call overhead, impacting level load times.
**Optimization**: Refactored the calculation to inline mathematical operations (specifically the cross products `numerator` and `denominator`), unpacked segment vector components `(x, y)` to avoid attribute lookup and object allocation overhead, cached list `.append` methods, and removed `abs()` calls using inline conditionals.
**Impact**: Profiling 10,000 executions over 100 segments using `timeit` demonstrated execution times dropping from ~2.53 seconds to ~1.68 seconds, yielding approximately a 33% performance gain during BSP tree building.

### 2024-05-30: Optimize Class Memory using `__slots__`
**Problem**: The `Sector`, `Segment`, and `BSPNode` classes are instantiated frequently during level loading and BSP tree creation. `Segment`s are particularly copied heavily. Python objects dynamically allocate a dictionary (`__dict__`) to store attributes, resulting in significant memory overhead and slight performance slowdowns for object creation.
**Optimization**: Added `__slots__` to the `Sector`, `Segment`, and `BSPNode` classes.
**Impact**: Using `sys.getsizeof`, memory overhead per instance dropped significantly. `Sector`: 336B -> 72B. `Segment`: 336B -> 144B. `BSPNode`: 336B -> 112B. This massively reduces the peak memory footprint during load and BSP construction, making the engine much more memory-efficient. Object creation is also roughly 10% faster.

### 2024-05-31: Optimize `MapRenderer.get_bounds` by unpacking and avoiding chained conditionals
**Problem**: The `MapRenderer.get_bounds` method uses nested inline conditional expressions (e.g. `p0.x if p0.x < x_min else p1.x if p1.x < x_min else x_min`) and repeated attribute accesses (`p0.x`, `p1.x`) to compute map bounds. This introduces attribute lookup overhead and forces multiple identical evaluations of the conditionals for every line segment in the map data.
**Optimization**: Unpacked the vector properties (`p0.x`, `p0.y`, `p1.x`, `p1.y`) into local variables first. Replaced the nested ternary operators with explicit, simple `if` comparisons which compile to more efficient bytecode in this hot path.
**Impact**: Running `timeit` for 10,000 executions over 1,000 line segments showed the execution time drop from ~1.90 seconds down to ~1.47 seconds, achieving roughly a **22% speedup** for bounds calculations by eliminating redundant attribute lookups and complex branching overhead.
### 2024-06-01: ViewRenderer.draw optimization
**Problem**: The `ViewRenderer.draw` method is the core rendering loop called every frame for potentially thousands of objects (walls and flats). It repeatedly looks up global functions and constants (e.g., `ray.draw_model`, `VEC3_ZERO`) and evaluates a conditional `tint = shade_tint if wall.is_shaded else screen_tint` for each wall.
**Optimization**: Cached `ray.draw_model` and `VEC3_ZERO` into local variables inside the `ViewRenderer.draw` method to avoid repeated `LOAD_GLOBAL` and `LOAD_ATTR` bytecode instructions. Inlined the tint conditional directly in the function call. Reversed the dictionary values directly via `reversed(self.mid_walls_to_draw.values())` (supported in Python 3.8+) instead of allocating an intermediate list.
**Impact**: Synthetic `timeit` benchmarks show execution time dropping from ~1.29s to ~0.72s for 10,000 runs, a roughly 40-45% performance improvement in the hot loop.

### 2024-06-02: Optimize FlatModel.get_outline with O(N) Dictionary-based Adjacency Graph
**Problem**: The `FlatModel.get_outline` method generates sequential vertices from randomly ordered line segments using a nested list search `if outline[-1] in seg:` inside a `while` loop that iterates until the polygon is closed. For simple shapes this works fine, but it has $O(N^2)$ time complexity. When triangulating complex sectors, this causes massive execution time slowdowns.
**Optimization**: Built a temporary dictionary mapping each vertex to its adjacent neighbors (up to 2 neighbors for a closed path). The `while` loop then traverses this explicit adjacency graph to find the next point in O(1) time per step, reducing the overall time complexity from $O(N^2)$ to $O(N)$.
**Impact**: Synthetic benchmarking using `timeit` for 1,000 segments over 10 iterations showed execution time dropping dramatically from ~2.2081s to ~0.0083s. This yields an incredible speedup for large complex sector layouts, removing a severe bottleneck in mesh generation.

### 2024-06-03: Eliminate `glm` function call and object allocation overhead in `get_quad_mesh`
**Problem**: The `WallModel.get_quad_mesh` method uses PyGLM's `glm.normalize` and `glm.length` functions to compute normals and wall width. However, passing Python tuples/objects (`vec3`) into these C-extensions and instantiating intermediate objects for each wall segment introduces massive Python-side object allocation overhead in the hot geometric building loop.
**Optimization**: Refactored the normal and width logic to directly unpack `x0`, `z0`, `x1`, `z1` into scalars (`dx = x1 - x0`, `dz = z1 - z0`). Instead of `glm.length`, used standard Euclidean distance `(dx*dx + dz*dz)**0.5` and manually normalized the X/Z components using plain arithmetic.
**Impact**: Using `timeit` for 10,000 executions of a 100-segment loop dropped execution time from ~3.14s to ~0.82s, delivering a roughly **~3.8x speedup** for geometric mesh generation by dodging repeated object instantiation.

### 2024-06-04: Optimize MapRenderer.remap_array list construction
**Problem**: The `MapRenderer.remap_array` function processes thousands of map segments per frame. Previously, it iterated over the array of points using a `for` loop and appended new `vec2` instances to an initially empty list. While the `.append` method was cached, the repeated function call overhead inside the loop remained a measurable bottleneck in this hot path.
**Optimization**: Refactored `remap_array` to use a list comprehension. I also tested a vectorized approach using NumPy, but the overhead of marshalling custom `vec2` Python objects into NumPy arrays and back negated the C-level math benefits. A list comprehension provides the best balance of speed and zero-dependency Pythonic readability for the current architecture.
**Impact**: Synthetic benchmarking using `timeit` over 1000 items showed execution time dropping from ~1.36 ms per loop to ~1.20 ms per loop, roughly a 10-12% performance improvement by avoiding `list.append` call overhead during dynamic map processing.

### 2024-06-04: Optimize `MapRenderer.remap_array` by hoisting math and using list comprehensions
**Problem**: `MapRenderer.remap_array` mapped every vector point through nested expressions like `(p0.x - x_min) * cx + out_min`, performing identical multiplications and subtractions (`x_min * cx`) repeatedly. It also built the output array using `.append` in a loop.
**Optimization**: Hoisted the invariant offsets (`ox = out_min - x_min * cx` and `oy = out_min - y_min * cy`) out of the loops, transforming the equation to `p.x * cx + ox`. Replaced the `for` loop and `.append` logic with a list comprehension.
**Impact**: Synthetic benchmarking using `timeit` for mapping 1000 pairs over 10,000 executions showed execution time dropping from ~15.2s to ~10.9s, delivering roughly a **28% speedup** on vector transformation logic.

### 2024-06-05: Optimize Models.build_flat_models by replacing extend with append
**Problem**: The `Models.build_flat_models` function iterated through `sector_segments` and used `self.flat_models.extend([[floor_model, ceil_model]])` to add a list pair to the models array. The `extend` method forces the creation of an intermediate list wrapper and requires iteration over its items to add them.
**Optimization**: Replaced `list.extend([[floor_model, ceil_model]])` with `list.append([floor_model, ceil_model])`.
**Impact**: Running `timeit` for 1,000,000 runs using `l.extend([[f, c]])` vs `l.append([f, c])` dropped execution time from ~0.95s to ~0.50s, yielding roughly a **~47% speedup** for list construction by dodging iteration and intermediate list allocation overhead.
