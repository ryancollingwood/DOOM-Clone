import pytest
from unittest.mock import MagicMock
from models import Models, WallType
from data_types import Segment

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.level_data = MagicMock()
    engine.level_data.sectors = {}
    engine.level_data.raw_segments = []
    engine.level_data.sector_segments = {}
    engine.bsp_builder.segments = []
    return engine

def test_add_wall_model_classification(mock_engine, monkeypatch):
    # Mock methods called in __init__ to avoid full initialization
    monkeypatch.setattr(Models, "build_wall_models", MagicMock())
    monkeypatch.setattr(Models, "build_flat_models", MagicMock())

    models = Models(mock_engine)

    # Create a segment
    seg = Segment((0,0), (1,1))

    # Test 1: Add SOLID wall
    solid_wall = MagicMock()
    solid_wall.wall_type = WallType.SOLID

    models.add_wall_model(solid_wall, seg)

    assert seg.other_wall_models == [solid_wall]
    assert seg.mid_wall_models == []
    assert models.wall_models == [solid_wall]

    # Test 2: Add PORTAL_MID wall
    mid_wall = MagicMock()
    mid_wall.wall_type = WallType.PORTAL_MID

    models.add_wall_model(mid_wall, seg)

    assert seg.other_wall_models == [solid_wall]
    assert seg.mid_wall_models == [mid_wall]
    assert models.wall_models == [solid_wall, mid_wall]

    # Test 3: Add PORTAL_LO wall
    lo_wall = MagicMock()
    lo_wall.wall_type = WallType.PORTAL_LO

    models.add_wall_model(lo_wall, seg)

    assert seg.other_wall_models == [solid_wall, lo_wall]
    assert seg.mid_wall_models == [mid_wall]
