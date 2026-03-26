from settings import *


import numpy as np

def cross_2d(vec_0, vec_1):
    v0_x = vec_0.x if hasattr(vec_0, 'x') else vec_0[0]
    v0_y = vec_0.y if hasattr(vec_0, 'y') else vec_0[1]
    v1_x = vec_1.x if hasattr(vec_1, 'x') else vec_1[0]
    v1_y = vec_1.y if hasattr(vec_1, 'y') else vec_1[1]
    return v0_x * v1_y - v1_x * v0_y


def is_on_front(vec_0, vec_1):
    # whether vec_0 is on the front side relative to vec_1
    v0_x = vec_0.x if hasattr(vec_0, 'x') else vec_0[0]
    v0_y = vec_0.y if hasattr(vec_0, 'y') else vec_0[1]
    v1_x = vec_1.x if hasattr(vec_1, 'x') else vec_1[0]
    v1_y = vec_1.y if hasattr(vec_1, 'y') else vec_1[1]
    return v0_x * v1_y < v1_x * v0_y


def is_on_back(vec_0, vec_1):
    return not is_on_front(vec_0, vec_1)