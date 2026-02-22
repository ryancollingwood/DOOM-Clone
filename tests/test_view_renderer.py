import pytest
from unittest.mock import MagicMock, call
import sys
from data_types import Segment, WallType
from view_renderer import ViewRenderer

@pytest.fixture
def mock_models_class(monkeypatch):
    mock_cls = MagicMock()
    # When ViewRenderer calls Models(engine), it returns an instance
    mock_instance = MagicMock()
    mock_instance.wall_models = []
    mock_instance.flat_models = {}
    mock_cls.return_value = mock_instance

    # Patch Models in view_renderer module
    monkeypatch.setattr("view_renderer.Models", mock_cls)
    return mock_cls

@pytest.fixture
def mock_engine(mock_models_class):
    engine = MagicMock()
    engine.map_renderer = MagicMock()
    engine.map_renderer.should_draw = False
    engine.bsp_builder = MagicMock()
    engine.bsp_builder.segments = []
    engine.camera = MagicMock()
    engine.bsp_traverser = MagicMock()
    engine.bsp_traverser.seg_ids_to_draw = []
    engine.level_data = MagicMock()
    engine.level_data.sectors = {}
    engine.level_data.raw_segments = []
    engine.level_data.sector_segments = {}

    return engine

def test_view_renderer_update_populates_lists(mock_engine):
    # Setup
    seg = Segment((0,0), (1,1))

    # Create mocked walls
    mid_wall = MagicMock()
    mid_wall.wall_type = WallType.PORTAL_MID

    other_wall = MagicMock()
    other_wall.wall_type = WallType.SOLID

    # Add walls to segment directly
    seg.mid_wall_models.append(mid_wall)
    seg.other_wall_models.append(other_wall)

    mock_engine.bsp_builder.segments = [seg]
    mock_engine.bsp_traverser.seg_ids_to_draw = [0]

    renderer = ViewRenderer(mock_engine)

    # Run update
    renderer.update()

    # Assert
    assert renderer.mid_walls_to_draw == [mid_wall]
    assert renderer.walls_to_draw == [other_wall]

def test_view_renderer_update_clears_lists(mock_engine):
    renderer = ViewRenderer(mock_engine)

    # Pre-populate lists
    renderer.mid_walls_to_draw.append(MagicMock())
    renderer.walls_to_draw.append(MagicMock())

    # Set segments to draw to empty
    mock_engine.bsp_traverser.seg_ids_to_draw = []

    # Run update
    renderer.update()

    # Assert
    assert renderer.mid_walls_to_draw == []
    assert renderer.walls_to_draw == []

def test_view_renderer_draw_order(mock_engine):
    renderer = ViewRenderer(mock_engine)

    # Setup walls
    w1 = MagicMock() # back (inserted first)
    w2 = MagicMock() # front (inserted second)

    # Mimic update population
    renderer.mid_walls_to_draw = [w1, w2]

    # Reset mock
    pyray_mock = sys.modules['pyray']
    pyray_mock.draw_model.reset_mock()

    renderer.draw()

    # Check calls
    # walls_to_draw is empty
    # mid_walls_to_draw has [w1, w2]
    # draw iterates reversed(mid_walls_to_draw) -> w2, w1

    calls = pyray_mock.draw_model.call_args_list
    assert len(calls) == 2
    # Verify arguments. calls[0] should be w2
    assert calls[0][0][0] == w2.model
    assert calls[1][0][0] == w1.model
