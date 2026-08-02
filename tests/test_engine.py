import sys
from unittest.mock import MagicMock, call, patch

# Mock dependencies before importing the module under test
sys.modules['pyray'] = MagicMock()
sys.modules['glm'] = MagicMock()
sys.modules['sect'] = MagicMock()
sys.modules['sect.triangulation'] = MagicMock()
sys.modules['ground'] = MagicMock()
sys.modules['ground.base'] = MagicMock()
sys.modules['raylib'] = MagicMock()

import pytest
from engine import Engine
import engine as engine_module

@pytest.fixture
def mock_dependencies():
    with patch('engine.LevelData') as MockLevelData, \
         patch('engine.BSPTreeBuilder') as MockBSPTreeBuilder, \
         patch('engine.Camera') as MockCamera, \
         patch('engine.InputHandler') as MockInputHandler, \
         patch('engine.BSPTreeTraverser') as MockBSPTreeTraverser, \
         patch('engine.MapRenderer') as MockMapRenderer, \
         patch('engine.ViewRenderer') as MockViewRenderer, \
         patch('engine.ray') as mock_ray:
        yield {
            'LevelData': MockLevelData,
            'BSPTreeBuilder': MockBSPTreeBuilder,
            'Camera': MockCamera,
            'InputHandler': MockInputHandler,
            'BSPTreeTraverser': MockBSPTreeTraverser,
            'MapRenderer': MockMapRenderer,
            'ViewRenderer': MockViewRenderer,
            'ray': mock_ray
        }

def test_engine_init(mock_dependencies):
    app = MagicMock()
    engine = Engine(app)

    assert engine.app == app
    mock_dependencies['LevelData'].assert_called_once_with(engine)
    mock_dependencies['BSPTreeBuilder'].assert_called_once_with(engine)
    mock_dependencies['Camera'].assert_called_once_with(engine)
    mock_dependencies['InputHandler'].assert_called_once_with(engine)
    mock_dependencies['BSPTreeTraverser'].assert_called_once_with(engine)
    mock_dependencies['MapRenderer'].assert_called_once_with(engine)
    mock_dependencies['ViewRenderer'].assert_called_once_with(engine)

def test_engine_update(mock_dependencies):
    engine = Engine(MagicMock())
    engine.update()

    engine.camera.pre_update.assert_called_once()
    engine.input_handler.update.assert_called_once()
    engine.camera.update.assert_called_once()
    engine.bsp_traverser.update.assert_called_once()
    engine.view_renderer.update.assert_called_once()

def test_engine_draw_2d_should_draw(mock_dependencies):
    engine = Engine(MagicMock())
    engine.map_renderer.should_draw = True

    engine.draw_2d()

    engine.map_renderer.draw.assert_called_once()
    mock_dependencies['ray'].draw_fps.assert_not_called()

def test_engine_draw_2d_should_not_draw(mock_dependencies):
    engine = Engine(MagicMock())
    engine.map_renderer.should_draw = False

    engine.draw_2d()

    engine.map_renderer.draw.assert_not_called()
    mock_dependencies['ray'].draw_fps.assert_called_once_with(10, 10)

def test_engine_draw_3d(mock_dependencies):
    engine = Engine(MagicMock())

    engine.draw_3d()

    mock_dependencies['ray'].begin_mode_3d.assert_called_once_with(engine.camera.m_cam)
    engine.view_renderer.draw.assert_called_once()
    mock_dependencies['ray'].end_mode_3d.assert_called_once()

def test_engine_draw(mock_dependencies):
    engine = Engine(MagicMock())

    engine.draw_3d = MagicMock()
    engine.draw_2d = MagicMock()

    engine.draw()

    mock_dependencies['ray'].begin_drawing.assert_called_once()
    mock_dependencies['ray'].clear_background.assert_called_once_with(engine_module.BLACK_COLOR)
    engine.draw_3d.assert_called_once()
    engine.draw_2d.assert_called_once()
    mock_dependencies['ray'].end_drawing.assert_called_once()
