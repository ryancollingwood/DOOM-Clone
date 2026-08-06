import timeit

s1 = """
class Wall:
    def __init__(self, is_shaded):
        self.model = 1
        self.is_shaded = is_shaded

walls = [Wall(i % 2 == 0) for i in range(1000)]
def draw_model(model, v, scale, tint):
    pass

def test():
    shade_tint = 1
    screen_tint = 2
    for wall in walls:
        draw_model(wall.model, 0, 1.0, shade_tint if wall.is_shaded else screen_tint)
"""

s2 = """
class Wall:
    def __init__(self, is_shaded):
        self.model = 1
        self.is_shaded = is_shaded

walls = [Wall(i % 2 == 0) for i in range(1000)]
def draw_model(model, v, scale, tint):
    pass

def test():
    shade_tint = 1
    screen_tint = 2
    for wall in walls:
        tint = shade_tint if wall.is_shaded else screen_tint
        draw_model(wall.model, 0, 1.0, tint)
"""

print(timeit.timeit("test()", setup=s1, number=10000))
print(timeit.timeit("test()", setup=s2, number=10000))
