# Bolt's Journal

* Performance Anti-Pattern: Replacing the walrus operator (`if (val := obj.attr): extend(val)`) with a direct truthiness check (`if obj.attr: extend(obj.attr)`) in hot loops is a de-optimization according to previous instructions, but profiling shows that `if obj.attr: extend(obj.attr)` is actually *faster* when `obj.attr` is a local variable or simple property (due to removing variable assignment overhead). However, wait, memory says: "Performance Anti-Pattern: Replacing the walrus operator (`if (val := obj.attr): extend(val)`) with a direct truthiness check (`if obj.attr: extend(obj.attr)`) in hot loops is a de-optimization. It forces a repeated attribute lookup (`LOAD_ATTR` twice) which is noticeably slower than the local variable assignment and lookup (`STORE_FAST`/`LOAD_FAST`) provided by the walrus operator."

Let's look at MapRenderer.remap_array:
`remap_array` uses a list comprehension:
```python
        return [
            (vec2(p0.x * cx + ox, p0.y * cy + oy),
             vec2(p1.x * cx + ox, p1.y * cy + oy))
            for p0, p1 in arr
        ]
```
Wait, the memory says:
"Performance Optimization: For generating lists with a known fixed size (like generating sequential vertices in `FlatModel.get_outline`), bypassing dynamic list scaling via `.append()` by pre-allocating the array (`[None] * target_len`) and assigning elements directly in a `for` loop eliminates resizing overhead and yields measurable speedups (e.g., ~15%)."

But my test `test_list_comp11.py` showed that caching `glm.vec2` inside the comprehension is faster!
```python
def remap_array_old(arr, cx=1.0, cy=1.0, ox=0.0, oy=0.0):
    return [
        (vec2(p0.x * cx + ox, p0.y * cy + oy),
         vec2(p1.x * cx + ox, p1.y * cy + oy))
        for p0, p1 in arr
    ]

def remap_array_new(arr, cx=1.0, cy=1.0, ox=0.0, oy=0.0):
    vec = glm.vec2
    return [
        (vec(p0.x * cx + ox, p0.y * cy + oy),
         vec(p1.x * cx + ox, p1.y * cy + oy))
        for p0, p1 in arr
    ]
```
Wait, `glm.vec2` is just `vec2` since it's imported as `from data_types import *`, where `vec2 = glm.vec2`.
Let's check `data_types.py`.

* The built-in `min` and `max` function overhead in tight Python loops can be bypassed completely using simple conditional if-else statements or inline ternary operators. Replacing `min(x, y)` with `x if x < y else y` avoids a function call, which in CPython avoids pushing arguments to the stack and entering the C-API. In profiling, `x if x < y else y` runs in ~0.60s per 10 million iterations vs ~2.95s for `min(a, b)` - roughly a 5x speedup. Similar improvements apply to bounding box calculation where we can sort coordinates linearly in one pass.

* Another learning: Avoiding `:=` walrus operator and explicitly checking `if obj.attr:` and then passing `obj.attr` might intuitively seem slower due to the repeated `LOAD_ATTR` instruction, and Memory states that it is a de-optimization. However, testing shows that `if seg.mid_wall_models: mid_extend(seg.mid_wall_models)` executes faster than `if (mid := seg.mid_wall_models): mid_extend(mid)` in multiple runs (~0.75s vs ~0.84s). I will avoid touching it based on the strict memory rule to not treat it as a valid performance optimization, but keep this knowledge.

* Re-evaluating `MapRenderer.remap_array()` and `remap_vec2()`
It uses a list comprehension but does multiple attribute lookups and instantiates `vec2(x, y)` objects repeatedly.
```python
def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
    # ...
    return [
        (vec2(p0.x * cx + ox, p0.y * cy + oy),
         vec2(p1.x * cx + ox, p1.y * cy + oy))
        for p0, p1 in arr
    ]
```
If we alias `vec2` as `vec = vec2`, it runs slightly faster.


* In `remap_array` and other similar functions where we iterate over `vec2` arrays (which are `glm.vec2`), accessing the components by index (`p0[0]`, `p0[1]`) is faster than by attribute (`p0.x`, `p0.y`). The `__getitem__` is implemented in C more efficiently than attribute lookup or property execution. Also, aliasing `glm.vec2` locally in list comprehension improves performance. This lines up with our memory: "When processing coordinate tuples in hot loops, extracting elements via index (e.g., `v[0]`, `v[1]`) to construct a transformed C-extension object like `glm.vec2` is faster than instantiating the wrapper object first and accessing its properties...".

Let's look at MapRenderer again.
`MapRenderer.remap_array`:
```python
    def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
        # ...
        return [
            (vec2(p0.x * cx + ox, p0.y * cy + oy),
             vec2(p1.x * cx + ox, p1.y * cy + oy))
            for p0, p1 in arr
        ]
```
If we change it to:
```python
    def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
        # ...
        vec = vec2 # which maps to glm.vec2
        return [
            (vec(p0[0] * cx + ox, p0[1] * cy + oy),
             vec(p1[0] * cx + ox, p1[1] * cy + oy))
            for p0, p1 in arr
        ]
```
Wait, we just saw that:
```python
def remap_array_old(arr, cx=1.0, cy=1.0, ox=0.0, oy=0.0):
    return [
        (vec2(p0.x * cx + ox, p0.y * cy + oy),
         vec2(p1.x * cx + ox, p1.y * cy + oy))
        for p0, p1 in arr
    ]
```
took 0.85s vs 0.71s for `p0[0]`.

But what about `bsp_builder.py`?
`BSPTreeBuilder.split_space` is called recursively.

* Profiling confirms that using memory pre-allocation instead of dynamic `.extend()` for populating `walls_to_draw` and `mid_walls_to_draw` does not have a measurable benefit.
* Wait! I notice that in `ViewRenderer.update()`, the segment processing uses `try-except` for bounds checking on `s_id`, but we are looking for algorithm improvements or Python loop improvements.

```python
    def update(self):
        self.walls_to_draw.clear()
        self.mid_walls_to_draw.clear()
        # ...
        for seg_id in self.segment_ids_to_draw:
            # walls
            seg = segments[seg_id]
            s_id = seg.seg_id

            try:
                if processed_segs[s_id]:
                    continue
                processed_segs[s_id] = True
                processed_ids_append(s_id)
            except (TypeError, IndexError):
                pass

            if (mid := seg.mid_wall_models):
                mid_extend(mid)
            if (other := seg.other_wall_models):
                other_extend(other)
```

Look at `if (mid := seg.mid_wall_models):`.
Is there a better way to do this? What if we avoid `extend` when it's empty by pre-checking if it's true but bypassing the walrus operator as tested earlier? Memory told us NOT to replace the walrus operator due to the repeated LOAD_ATTR... Wait, actually, the journal says:
"Performance Optimization: When extending lists in hot loops, prepending an empty check (`if items: target_list.extend(items)`) avoids the overhead of `.extend()` when `items` is frequently empty, yielding measurable performance improvements."
And I just confirmed in `test_view_renderer_update6.py` that `if seg.mid_wall_models: mid_extend(seg.mid_wall_models)` is faster than `if (mid := seg.mid_wall_models): mid_extend(mid)`. Wait, but Memory says "Replacing the walrus operator... is a de-optimization". I MUST NOT replace the walrus operator.

Let's look at `ViewRenderer.draw()`.
```python
        # draw walls
        for wall in self.walls_to_draw:
            # Inline conditional tint expression to avoid variable assignment overhead
            draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)

        # draw portal_mid walls from back to front
        # Reverse list directly
        for wall in reversed(self.mid_walls_to_draw):
            draw_model(wall.model, v_zero, 1.0, shade_tint if wall.is_shaded else screen_tint)
```
What if we use a list comprehension or just simple conditional assignment for `tint`? The inline conditional `shade_tint if wall.is_shaded else screen_tint` is already fast.

Let's look at `MapRenderer.remap_array`:
```python
    def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
        # ...
        return [
            (vec2(p0.x * cx + ox, p0.y * cy + oy),
             vec2(p1.x * cx + ox, p1.y * cy + oy))
            for p0, p1 in arr
        ]
```
In our `test_list_comp11.py`, assigning `vec = glm.vec2` inside `remap_array` and using `vec` inside the list comprehension yields a speedup:
```python
    def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
        # ...
        vec = vec2 # which aliases glm.vec2
        return [
            (vec(p0.x * cx + ox, p0.y * cy + oy),
             vec(p1.x * cx + ox, p1.y * cy + oy))
            for p0, p1 in arr
        ]
```
Let's see if there is another bottleneck.


* The `if` chaining for bounding boxes (e.g., `if new_x < -MAX_WORLD_BOUNDARY: ... elif new_x > MAX_WORLD_BOUNDARY: ... else: ...`) is slightly faster than chained inline ternary operators (`new_x if -MAX_WORLD_BOUNDARY <= new_x <= MAX_WORLD_BOUNDARY else (-MAX_WORLD_BOUNDARY if new_x < -MAX_WORLD_BOUNDARY else MAX_WORLD_BOUNDARY)`). ~0.37s vs ~0.43s per 1 million calls.

* What about `BSPNode` caching during traversal?
In `bsp/bsp_traverser.py`:
```python
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
```

Wait! In `MapRenderer.remap_array`:
```python
        return [
            (vec2(p0.x * cx + ox, p0.y * cy + oy),
             vec2(p1.x * cx + ox, p1.y * cy + oy))
            for p0, p1 in arr
        ]
```
Wait, my test `test_remap_array.py` proved that modifying it to:
```python
    def remap_array(self, arr: list[tuple[vec2]], out_min=MAP_OFFSET):
        # ...
        vec = vec2
        return [
            (vec(p0[0] * cx + ox, p0[1] * cy + oy),
             vec(p1[0] * cx + ox, p1[1] * cy + oy))
            for p0, p1 in arr
        ]
```
speeds up `remap_array` by ~25-30% (~0.85s to ~0.65s). And it's very clean and readable. Is there anything better?
Let's look at `MapRenderer.remap_vec2`, `remap_x`, `remap_y`.

* The speedup comes directly from `vec = glm.vec2` instead of `vec = vec2` or calling `vec2()`. The wrapper `vec2` in `data_types.py` might be adding overhead if it's a function or just an alias. Actually in `data_types.py` it's `from settings import *`, and in `settings.py` there is `import pyglm as glm`, `vec2 = glm.vec2`. So `vec2` IS `glm.vec2`. Then why is `vec = glm.vec2` faster in my test? Ah, in my test script `test_remap_array_index3.py`, I explicitly defined `def vec2(x, y): return glm.vec2(x, y)` which has a Python function call overhead! But in the real engine, `vec2 = glm.vec2`.
So my test is flawed.

Let's test it properly with `vec2 = glm.vec2`.

* The speedup of `p0[0]` over `p0.x` is real but modest (~3.5% speedup in the comprehension loop).

* Let's revisit `ViewRenderer.update` as it's a hot path.
```python
        for seg_id in self.segment_ids_to_draw:
            # walls
            seg = segments[seg_id]
            s_id = seg.seg_id

            try:
                if processed_segs[s_id]:
                    continue
                processed_segs[s_id] = True
                processed_ids_append(s_id)
            except (TypeError, IndexError):
                pass
```
Is there any optimization here? Since `segment_ids_to_draw` can contain multiple walls for the same `s_id`, the check is necessary.

* What about the BSP traverser loop?
```python
        # Optimization: Mathematically simplified the cross product inequality and cached
        # the constant right side (`node.splitter_c`) during tree building. This drops 2 subtractions
        # per traversal node evaluation in the hot path.
        if x * node.splitter_vec_y - y * node.splitter_vec_x < node.splitter_c:
```

What if we look at `MapRenderer.get_bounds`?
```python
    @staticmethod
    def get_bounds(segments: list[tuple[vec2]]):
        inf = float('inf')
        if not segments:
            return inf, inf, -inf, -inf
        x_min, y_min, x_max, y_max = inf, inf, -inf, -inf

        # Optimization: Unpack vec2 attributes into local variables and use simple
        # 'if' branches instead of chained nested ternary operators to avoid
        # repeated attribute lookups and complex branching overhead.
        for p0, p1 in segments:
            p0x, p0y = p0.x, p0.y
            p1x, p1y = p1.x, p1.y

            if p0x < x_min: x_min = p0x
            if p1x < x_min: x_min = p1x
            if p0x > x_max: x_max = p0x
            if p1x > x_max: x_max = p1x

            if p0y < y_min: y_min = p0y
            if p1y < y_min: y_min = p1y
            if p0y > y_max: y_max = p0y
            if p1y > y_max: y_max = p1y

        return x_min, y_min, x_max, y_max
```
Wait, we tested this earlier in `test_bounds.py` and `test_bounds2.py` and found that a single conditional check comparing `p0x < p1x` cuts down the `x_min` and `x_max` comparisons by half!
```python
            if p0x < p1x:
                if p0x < x_min: x_min = p0x
                if p1x > x_max: x_max = p1x
            else:
                if p1x < x_min: x_min = p1x
                if p0x > x_max: x_max = p0x
```
This is explicitly in the memory: "Performance Optimization: When calculating bounding boxes from line segments (e.g., in `MapRenderer.get_bounds`), comparing the segment's coordinates against each other first (e.g., `p0.x < p1.x`) before comparing against the global min/max reduces the total number of conditional checks required per segment, yielding measurable execution speedups."

Ah! Memory already suggested this. Is it already implemented? Let's check `MapRenderer.get_bounds` in `map_renderer.py`.


* OK, the `get_bounds` optimization is mentioned in memory but hasn't been implemented in this code base! The current code still uses the unoptimized sequential comparison instead of comparing the segment coordinates first. Wait, the memory states: "Performance Optimization: When calculating bounding boxes from line segments (e.g., in `MapRenderer.get_bounds`), comparing the segment's coordinates against each other first (e.g., `p0.x < p1.x`) before comparing against the global min/max reduces the total number of conditional checks required per segment, yielding measurable execution speedups." This means I SHOULD implement this optimization. However, wait, wait, wait. The system prompt says "Your mission is to identify and implement **ONE** small performance improvement that makes the application measurably faster or more memory-efficient." Let's find out if there's anything else that I can do that has a bigger impact.

* What about `ViewRenderer.update()` empty array check?
```python
        for seg_id in self.segment_ids_to_draw:
            # walls
            seg = segments[seg_id]
            s_id = seg.seg_id
            ...
            if (mid := seg.mid_wall_models):
                mid_extend(mid)
            if (other := seg.other_wall_models):
                other_extend(other)
```
Memory specifically says:
"Performance Anti-Pattern: Replacing the walrus operator (`if (val := obj.attr): extend(val)`) with a direct truthiness check (`if obj.attr: extend(obj.attr)`) in hot loops is a de-optimization. It forces a repeated attribute lookup (`LOAD_ATTR` twice) which is noticeably slower than the local variable assignment and lookup (`STORE_FAST`/`LOAD_FAST`) provided by the walrus operator."
So I MUST NOT optimize that part by removing the walrus operator.

Let's look at `camera.py`:
```python
    def init_cam_step(self):
        dt = self.app.dt
        if not math.isfinite(dt) or dt < 0:
            dt = 0
        # Optimization: Standard min() function calls introduce noticeable overhead in Python hot loops.
        # Replacing them with inline ternary operators avoids function call overhead and is significantly faster.
        dt = dt if dt < MAX_SAFE_DT else MAX_SAFE_DT
        #
        self.speed = CAM_SPEED * dt
```
And `move()`:
```python
        if math.isfinite(dx):
            old_x = self.pos_3d.x
            new_x = old_x + dx
            self.pos_3d.x = new_x if -MAX_WORLD_BOUNDARY <= new_x <= MAX_WORLD_BOUNDARY else (-MAX_WORLD_BOUNDARY if new_x < -MAX_WORLD_BOUNDARY else MAX_WORLD_BOUNDARY)
            self.target.x += self.pos_3d.x - old_x
```
As measured in `test_min5.py`, an inline `if` statement block is slightly faster than chained inline ternary operators for clamping bounds:
```python
        if math.isfinite(dx):
            old_x = self.pos_3d.x
            new_x = old_x + dx
            if new_x < -MAX_WORLD_BOUNDARY:
                self.pos_3d.x = -MAX_WORLD_BOUNDARY
            elif new_x > MAX_WORLD_BOUNDARY:
                self.pos_3d.x = MAX_WORLD_BOUNDARY
            else:
                self.pos_3d.x = new_x
            self.target.x += self.pos_3d.x - old_x
```
But `camera.py` `move` is only called once per frame (100 times in the profile run), it's not a hot path.

Let's look at `bsp_traverser.py`:
```python
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
```
This is called 6200 times in 100 frames.

Wait! What about the `MapRenderer.get_bounds` suggestion? It's explicitly stated in memory. Let's do that optimization!

* If a test failure occurs during a full suite run, it's due to state pollution from globally mocked dependencies in PyTest. Running tests individually using `pytest <test_file.py>` confirms that no actual regressions exist, which aligns perfectly with memory: "Running the full test suite at once (e.g., `pytest tests/`) can result in false positive failures due to state pollution from globally mocked dependencies (like `pyray`). If test failures occur during a suite run, verify them by running the individual test files separately."

* Performance Optimization: When calculating bounding boxes from line segments (e.g., in `MapRenderer.get_bounds`), comparing the segment's coordinates against each other first (e.g., `p0.x < p1.x`) before comparing against the global min/max reduces the total number of conditional checks required per segment from 4 to 3 on average, yielding measurable execution speedups.
