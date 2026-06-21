import glm
import pyray as ray

try:
    normals = glm.array.from_numbers(glm.float32, 0, 1, 0, 0, 1, 0, 0, 1, 0)
    print(normals.length)
    print(normals.element_type)
    # wait, PyGLM's from_numbers creates an array of floats, which is what ray.ffi.from_buffer("float []", ...) needs.
    print(ray.ffi.from_buffer("float []", normals))
except Exception as e:
    print(f"Error: {e}")

try:
    normal = glm.vec3(0, 1, 0)
    normals2 = glm.array([normal, normal, normal])
    print(normals2.length)
    print(normals2.element_type)
    print(ray.ffi.from_buffer("float []", normals2))
except Exception as e:
    print(f"Error2: {e}")
