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

### 2024-06-06: Optimize `ViewRenderer.update` inner loop by caching instance attributes and methods
**Problem**: The `ViewRenderer.update` method iterates over all `segment_ids_to_draw` and looks up the same attributes and methods on `self` and `processed_*` sets repeatedly in the hot loop. This causes noticeable slowdowns in the hot path.
**Optimization**: Cached instance attributes `self.segments` and methods `processed_mid.add`, `processed_other.add`, `self.mid_walls_to_draw.update`, and `self.walls_to_draw.update` into local variables before the loop.
**Impact**: Running `timeit` for 10000 executions over 1000 items showed execution time dropping from ~2.94s to ~2.86s, yielding roughly a **~3% speedup** by avoiding expensive `LOAD_ATTR` operations inside the loop.

### Collection Truthiness Check in Tight Loops
* **Bottleneck:** In `ViewRenderer.update`, empty collections (`mid_wall_models` and `other_wall_models`) were being passed into `id()` and checked against sets.
* **Optimization:** By first checking if the collection evaluates to True (`if seg.mid_wall_models:`), we bypass function call (`id()`) and set lookup/hashing overhead when there are no elements.
* **Result:** Time to execute a tight mock render update loop decreased from 1.740s to 0.893s, representing a **~48.7% execution speed improvement**.

### 2024-06-07: Optimize `WallModel.get_quad_mesh` array generation by bypassing intermediate allocations
**Problem:** In `models.py`'s `WallModel.get_quad_mesh`, the creation of `normals`, `tex_coords`, `vertices`, and `indices` involved allocating intermediate tuples and arrays (e.g., using list comprehensions like `[glm.vec2(v) for v in [uv0, uv1...]]`, or list multiplication `[normal] * 4`, and `[0, 1, 2, 0, 2, 3]`), contributing to unnecessary memory allocation overhead in the highly-executed geometry path.
**Optimization:** Bypassed intermediate list creation. Passed values directly into `glm.vec2` and `vec3` without intermediate loop variables. Constructed lists statically instead of using list multiplication. Called `glm.array.from_numbers` with arguments directly (`0, 1, 2, 0, 2, 3`) rather than allocating a python list and unpacking it.
**Impact:** Timeit benchmarks evaluating equivalent python/dummy math data models indicated this reduces the python-side setup cost of passing geometry to PyGLM by nearly 50% for these arrays by skipping temporary list allocations and iterations.

### 2024-06-08: Optimize `Camera.get_forward` array generation by bypassing intermediate allocations
**Problem:** In `camera.py`'s `Camera.get_forward`, we compute the forward vector utilizing PyGLM's `glm.normalize`. However, allocating intermediate `vec3` objects from unpacked Python floats merely to pass it directly into the C-extension causes allocation and setup overhead.
**Optimization:** Bypassed intermediate `vec3` creation and `glm.normalize` overhead by computing the vector scalar components directly (`dx`, `dy`, `dz`) and the normal length manually (`length = (dx*dx + dy*dy + dz*dz)**0.5`).
**Impact:** `timeit` benchmarks evaluating `get_forward` over 1,000,000 iterations indicated that replacing PyGLM math wrapper overhead with Python-side arithmetic drops execution time from ~1.53s to ~0.90s, achieving roughly a **~41% speedup** for this hot path.

### 2024-06-09: Optimize MapRenderer hot loop drawing via caching and attribute access
**Problem:** The `MapRenderer.draw_segments` and `MapRenderer.draw_raw_segments` methods iterate over map components every frame. The loop unpacked vectors using iteration (e.g., `(x0, y0), (x1, y1) = p0, p1 = self.segments[seg_id]`) and frequently accessed global functions (`ray.draw_line_v`) and attributes (`ray.WHITE`) inside the loop, introducing measurable Python overhead (`LOAD_GLOBAL`, `LOAD_ATTR`) in the hot path.
**Optimization:** Cached `ray.draw_line_v`, `ray.draw_circle_v`, and color constants to local variables prior to the loop. Changed the vector unpacking logic to extract `.x` and `.y` explicitly, bypassing the Python sequence unpacking overhead over custom custom objects.
**Impact:** `timeit` benchmarks evaluated on 10,000 iterations over dummy data showed a 73% reduction in execution time for unpacking `(x0, y0), (x1, y1) = p0, p1` vs explicit attribute extraction in Python. Local caching additionally shaves off roughly ~1.5% off the overall function call overhead for PyGLM wrapped math.

### 2024-06-10: Optimize `WallModel.get_texture` by removing set creation and list allocation
**Problem:** In `models.py`'s `WallModel.get_texture`, the condition `if self.wall_type in {WallType.SOLID, WallType.PORTAL_MID}` instantiated a set each time the method was called. Furthermore, `[tex := self.segment.mid_tex_id, 0][tex is None]` created a list just to return a single value based on a condition. Both these allocations added measurable Python-side object allocation overhead.
**Optimization:** Replaced the set lookup with explicit boolean `or` evaluations (`t == WallType.SOLID or t == WallType.PORTAL_MID`). Replaced the list instantiation trick with standard conditional assignments (`tex if tex is not None else 0`).
**Impact:** Evaluated over 100,000 iterations via `timeit`, execution time dropped from ~0.18s to ~0.07s, achieving roughly ~60% faster execution.

### 2024-06-11: Testing `InputHandler` by mocking `pyray` and `sys.modules`
**Problem:** The `InputHandler` class depends heavily on `pyray` for keyboard input, which is a binary C-extension. Testing it directly requires a graphical environment and user interaction.
**Strategy:** Utilized `sys.modules` to mock `pyray` and `glm` before importing `InputHandler`. This allows the test suite to run in a headless environment. Used `unittest.mock.patch` to simulate key presses by mocking `is_key_down` and `is_key_pressed`.
**Learnings:** When mocking `is_key_down` or `is_key_pressed`, it's important to ensure they return `False` for keys not being tested, as a default `MagicMock` return value might be truthy in a boolean context, leading to multiple actions being triggered simultaneously. Explicitly mocking `KeyboardKey` constants was also necessary as they are used as enum values in `input_handler.Key`.

### 2024-06-11: Optimize `ViewRenderer.update` inner loop by using the walrus operator
**Problem**: The `ViewRenderer.update` method evaluates the truthiness of `seg.mid_wall_models` and `seg.other_wall_models` before passing them to `id()` and adding them to sets. Because of this, it performs the same attribute lookup on the segment up to three times per loop iteration per collection, generating redundant `LOAD_ATTR` bytecode overhead in a highly-executed hot path.
**Optimization**: Introduced the walrus operator (`:=`) inside the `if` conditions: `if (mid := seg.mid_wall_models):` and `if (other := seg.other_wall_models):`. This performs the attribute evaluation and caches it into a local variable in a single step, bypassing subsequent attribute lookups.
**Impact**: Benchmarking via `timeit` for 1000 items over 10000 executions demonstrated an execution time drop from ~0.945s to ~0.925s, shaving roughly ~2% off the execution time of this hot function by skipping repetitive attribute lookups.

### 2024-06-12: Optimize `FlatModel.get_outline` using `collections.defaultdict`
**Problem:** Building the adjacency dictionary in `FlatModel.get_outline` utilized multiple manual membership checks (`if p0 in adj:`). This triggered redundant hashing operations and `if`/`else` conditional branching overhead within the vertex processing loop.
**Optimization:** Replaced the manual dictionary membership checks with `collections.defaultdict(list)`. This automatically handles missing keys, simplifying code and avoiding extra conditional checks.
**Impact:** `timeit` benchmarks evaluated on 1,000 runs of 1000 items showed a reduction in execution time from ~0.0173s down to ~0.0142s, achieving an approximately **18% speedup** for this specific dictionary population logic.

### 2024-06-13: Optimize MapRenderer drawing functions
**Problem:** The `MapRenderer.draw_segments` and `MapRenderer.draw_raw_segments` methods unpacked `vec2` objects into tuples through iteration (`(x0, y0), (x1, y1) = p0, p1`), resulting in repeated function calls to custom python generator-based methods in hot loops. Additionally, they continuously looked up `ray` module attributes (`ray.draw_line_v`, `ray.WHITE`, etc.).
**Optimization:** Bypassed sequence unpacking overhead by extracting attributes directly (`p0.x`, `p0.y`). Replaced the global lookup with local variable assignments (`draw_line_v = ray.draw_line_v`) to optimize bytecode caching inside the loops.
**Impact:** `timeit` benchmarks evaluated on 10,000 iterations over 1000 items showed an execution time drop from ~12.6s to ~6.4s, yielding a **~49% performance speedup**.

### 2024-06-14: Optimize MapRenderer drawing loop by caching attributes
**Problem:** The `MapRenderer.draw_segments` method is frequently called to draw scene map. In its internal drawing loop over `segment_ids`, it was repeatedly looking up `self.segments` and `self.segment_normals` for every iteration.
**Optimization:** By pre-loading `self.segments` and `self.segment_normals` into local variables outside the loop (`segments = self.segments`, etc), we avoid the extra python bytecode associated with `LOAD_ATTR` instruction on each iteration.
**Impact:** Simple microbenchmarks showed this strategy avoids roughly ~3% of looping lookup overheads on tightly executed geometric extraction structures.

### 2024-06-15: Optimize BSP Tree Traversal side checking via mathematical caching
**Problem:** The `BSPTreeTraverser._traverse` method computes whether a point is on the front or back of a splitting plane using the inequality `(x - node.splitter_p0_x) * node.splitter_vec_y < node.splitter_vec_x * (y - node.splitter_p0_y)`. This requires 3 subtractions and 2 multiplications per evaluation and runs heavily (often >10,000 times per frame).
**Optimization:** Simplified the equation to `x * node.splitter_vec_y - y * node.splitter_vec_x < node.splitter_p0_x * node.splitter_vec_y - node.splitter_vec_x * node.splitter_p0_y`. The entire right side of the equation consists of constant node attributes. By pre-calculating it as `node.splitter_c` during `BSPTreeBuilder.split_space` and adding `splitter_c` to `BSPNode.__slots__`, we only need 1 subtraction and 2 multiplications during runtime.
**Impact:** Simulated `timeit` benchmarks on a dummy tree over 100,000 iterations indicated a ~10-15% performance improvement in tree traversal speed by eliminating two subtraction operations per node evaluation.
