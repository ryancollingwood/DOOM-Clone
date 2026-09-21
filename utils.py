import os
from settings import *


def cross_2d(vec_0: vec2, vec_1: vec2):
    return vec_0.x * vec_1.y - vec_1.x * vec_0.y


def is_on_front(vec_0: vec2, vec_1: vec2):
    # whether vec_0 is on the front side relative to vec_1
    return vec_0.x * vec_1.y < vec_1.x * vec_0.y


def is_on_back(vec_0: vec2, vec_1: vec2):
    return not is_on_front(vec_0, vec_1)

def list_level_files():
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    levels_dir = os.path.join(utils_dir, 'levels')

    if not os.path.isdir(levels_dir):
        return []

    files = [f for f in os.listdir(levels_dir) if os.path.isfile(os.path.join(levels_dir, f))]
    return sorted(files)


def list_texture_files():
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(utils_dir, 'assets')

    if not os.path.isdir(assets_dir):
        return []

    texture_files = []
    for root, _, files in os.walk(assets_dir):
        for file in files:
            texture_files.append(file)

    return sorted(texture_files)
