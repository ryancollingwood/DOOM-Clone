from settings import *
from random import randrange
from enum import IntEnum, auto
from typing import Union
from texture_id import *


class WallType(IntEnum):
    SOLID = 0
    PORTAL_LO = 1
    PORTAL_MID = 2
    PORTAL_UP = 3


class Sector:
    # Optimization: __slots__ reduces memory footprint from 336 bytes to 72 bytes per instance
    # by preventing the creation of a dynamic __dict__ for thousands of sector allocations.
    __slots__ = ('floor_h', 'ceil_h', 'floor_tex_id', 'ceil_tex_id', 'nested_sector_ids')

    def __init__(self, floor_h=None, ceil_h=None, floor_tex_id=None, ceil_tex_id=None,
                 nested_sector_ids=None):
        #
        self.floor_h: float = floor_h
        self.ceil_h: float = ceil_h
        #
        self.floor_tex_id: int = floor_tex_id
        self.ceil_tex_id: int = ceil_tex_id
        #
        self.nested_sector_ids: list = nested_sector_ids


class Segment:
    # Optimization: __slots__ reduces memory footprint from 336 bytes to 144 bytes per instance.
    # Segments are heavily copied and split during BSP tree construction.
    __slots__ = ('seg_id', 'pos', 'vector', 'avg_pos', 'sector_id', 'back_sector_id', 'low_tex_id', 'mid_tex_id', 'up_tex_id', 'wall_model_ids', 'mid_wall_models', 'other_wall_models', 'has_portal_low', 'has_portal_mid', 'has_portal_up')

    def __init__(self, p0: tuple[float], p1: tuple[float],
                 sector_id=None, back_sector_id=None,
                 low_tex_id=None, mid_tex_id=None, up_tex_id=None, seg_id=None):
        #
        self.seg_id: int = seg_id
        self.pos: tuple[vec2] = vec2(p0), vec2(p1)
        self.vector: vec2 = self.pos[1] - self.pos[0]
        #
        self.avg_pos = (self.pos[0] + self.pos[1]) * 0.5
        #
        self.sector_id: int = sector_id
        self.back_sector_id: int = back_sector_id
        #
        self.low_tex_id: int = low_tex_id
        self.mid_tex_id: int = mid_tex_id
        self.up_tex_id: int = up_tex_id
        #
        self.wall_model_ids: set[int] = set()
        self.mid_wall_models: dict = {}
        self.other_wall_models: list = []
        #
        self.has_portal_low: bool = True
        self.has_portal_mid: bool = True
        self.has_portal_up: bool = True


class BSPNode:
    # Optimization: __slots__ reduces memory footprint from 336 bytes to 112 bytes per instance.
    # BSP tree nodes are heavily allocated and traversed.
    __slots__ = ('front', 'back', 'splitter_p0', 'splitter_p1', 'splitter_vec', 'splitter_p0_x', 'splitter_p0_y', 'splitter_vec_x', 'splitter_vec_y', 'segment_id')

    def __init__(self):
        #
        self.front: BSPNode = None
        self.back: BSPNode = None
        #
        self.splitter_p0: vec2 = None
        self.splitter_p1: vec2 = None
        self.splitter_vec: vec2 = None

        # Unpacked scalar coordinates to avoid vec2 object lookups in tight loop (BSPTreeTraverser)
        self.splitter_p0_x: float = None
        self.splitter_p0_y: float = None
        self.splitter_vec_x: float = None
        self.splitter_vec_y: float = None
        #
        self.segment_id: int = None
