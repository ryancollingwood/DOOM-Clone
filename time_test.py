import timeit

def using_extend():
    flat_models = []
    for _ in range(1000):
        flat_models.extend([["a", "b"]])

def using_append():
    flat_models = []
    for _ in range(1000):
        flat_models.append(["a", "b"])

print("using_extend:", timeit.timeit(using_extend, number=10000))
print("using_append:", timeit.timeit(using_append, number=10000))
