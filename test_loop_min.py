import timeit

def method_min():
    MAX_SAFE_DT = 0.1
    for i in range(1000):
        dt = min(0.016, MAX_SAFE_DT)

def method_ternary():
    MAX_SAFE_DT = 0.1
    for i in range(1000):
        dt = 0.016 if 0.016 < MAX_SAFE_DT else MAX_SAFE_DT

print("min", timeit.timeit(method_min, number=10000))
print("ternary", timeit.timeit(method_ternary, number=10000))
