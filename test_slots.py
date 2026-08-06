import timeit
import sys

class Point1:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Point2:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point1(1, 2)
p2 = Point2(1, 2)

print(sys.getsizeof(p1) + sys.getsizeof(p1.__dict__))
print(sys.getsizeof(p2))

def create_p1():
    return [Point1(i, i) for i in range(1000)]

def create_p2():
    return [Point2(i, i) for i in range(1000)]

print(timeit.timeit(create_p1, number=1000))
print(timeit.timeit(create_p2, number=1000))
