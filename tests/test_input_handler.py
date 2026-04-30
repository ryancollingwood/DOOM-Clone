import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before importing the module under test
mock_pyray = MagicMock()
sys.modules['pyray'] = mock_pyray
sys.modules['glm'] = MagicMock()

# Mock KeyboardKey values that are used in input_handler.Key
mock_pyray.KeyboardKey.KEY_W = 87
mock_pyray.KeyboardKey.KEY_S = 83
mock_pyray.KeyboardKey.KEY_A = 65
mock_pyray.KeyboardKey.KEY_D = 68
mock_pyray.KeyboardKey.KEY_Q = 81
mock_pyray.KeyboardKey.KEY_E = 69
mock_pyray.KeyboardKey.KEY_M = 77
mock_pyray.KeyboardKey.KEY_O = 79

import pytest  # noqa: E402
from input_handler import InputHandler, Key  # noqa: E402

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.camera = MagicMock()
    engine.map_renderer = MagicMock()
    engine.map_renderer.should_draw = True
    engine.view_renderer = MagicMock()
    return engine

def test_input_handler_init(mock_engine):
    handler = InputHandler(mock_engine)
    assert handler.engine == mock_engine
    assert handler.camera == mock_engine.camera

@pytest.mark.parametrize("key, method_name", [
    (Key.FORWARD, "step_forward"),
    (Key.BACK, "step_back"),
    (Key.STRAFE_RIGHT, "step_right"),
    (Key.STRAFE_LEFT, "step_left"),
    (Key.UP, "step_up"),
    (Key.DOWN, "step_down"),
])
def test_camera_movement(mock_engine, key, method_name):
    handler = InputHandler(mock_engine)

    # Mock is_key_down to return True only for the specific key
    with patch('input_handler.is_key_down', side_effect=lambda k: k == key):
        with patch('input_handler.is_key_pressed', return_value=False):
            handler.update()

    method = getattr(mock_engine.camera, method_name)
    method.assert_called_once()

def test_map_toggle(mock_engine):
    handler = InputHandler(mock_engine)
    mock_engine.map_renderer.should_draw = True

    # Mock is_key_pressed to return True for MAP key
    with patch('input_handler.is_key_down', return_value=False):
        with patch('input_handler.is_key_pressed', side_effect=lambda k: k == Key.MAP):
            handler.update()

    assert mock_engine.map_renderer.should_draw is False
    mock_engine.view_renderer.update_screen_tint.assert_called_once()

    # Toggle again
    with patch('input_handler.is_key_down', return_value=False):
        with patch('input_handler.is_key_pressed', side_effect=lambda k: k == Key.MAP):
            handler.update()
    assert mock_engine.map_renderer.should_draw is True

def test_screenshot(mock_engine):
    handler = InputHandler(mock_engine)

    # We need to mock 'ray' which comes from 'from settings import *'
    # In input_handler.py, ray is pyray.
    with patch('input_handler.is_key_down', return_value=False):
        with patch('input_handler.is_key_pressed', side_effect=lambda k: k == Key.SCREEN_SHOT):
            with patch('input_handler.ray.take_screenshot') as mock_screenshot:
                handler.update()
                mock_screenshot.assert_called_once_with('screen_shot.png')
