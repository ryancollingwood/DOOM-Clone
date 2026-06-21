import glm

try:
    arr = glm.array.from_numbers(glm.float32, 1, 2, 3)
    print("from_numbers works!")
except Exception as e:
    print(f"from_numbers failed: {e}")

try:
    arr = glm.array(glm.float32, 1, 2, 3)
    print("glm.array(type, args) works!")
except Exception as e:
    print(f"glm.array(type, args) failed: {e}")

try:
    arr = glm.array([1.0, 2.0, 3.0])
    print("glm.array(list) works!")
except Exception as e:
    print(f"glm.array(list) failed: {e}")
