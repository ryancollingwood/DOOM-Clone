import sys
import pytest
from unittest.mock import MagicMock, patch

class DummyVec3:
    __slots__ = ['x', 'y', 'z']
    def __init__(self, x, y=None, z=None):
        if y is None and z is None:
            self.x = self.y = self.z = float(x)
        else:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def __repr__(self):
        return f"vec3({self.x}, {self.y}, {self.z})"

class DummyVector3:
    __slots__ = ['x', 'y', 'z']
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

@pytest.fixture
def mocked_camera_module():
    # Mocking sys.modules and settings using patches to ensure isolation
    with patch.dict(sys.modules, {
        'pyray': MagicMock(),
        'glm': MagicMock(),
        'sect': MagicMock(),
        'ground': MagicMock(),
        'raylib': MagicMock()
    }):
        import settings
        with patch.multiple(settings, vec3=DummyVec3):
            settings.ray.Vector3 = DummyVector3
            # We must import Camera inside the patch context
            if 'camera' in sys.modules:
                del sys.modules['camera']
            from camera import Camera
            yield Camera

def test_get_forward_normal(mocked_camera_module):
    Camera = mocked_camera_module
    # Create a mock engine to satisfy __init__
    mock_engine = MagicMock()
    mock_engine.level_data.settings = {
        'cam_pos': (0, 0, 0),
        'cam_target': (0, 0, -1)
    }

    cam = Camera(mock_engine)

    # Positive X direction
    cam.pos_3d = DummyVector3(0, 0, 0)
    cam.target = DummyVector3(10, 0, 0)
    forward = cam.get_forward()
    assert forward.x == pytest.approx(1.0)
    assert forward.y == pytest.approx(0.0)
    assert forward.z == pytest.approx(0.0)

    # Diagonal direction
    cam.pos_3d = DummyVector3(1, 1, 1)
    cam.target = DummyVector3(2, 2, 2)
    forward = cam.get_forward()
    # length = sqrt(1^2 + 1^2 + 1^2) = sqrt(3)
    expected = 1.0 / (3.0**0.5)
    assert forward.x == pytest.approx(expected)
    assert forward.y == pytest.approx(expected)
    assert forward.z == pytest.approx(expected)

    # Negative Z direction
    cam.pos_3d = DummyVector3(0, 5, 0)
    cam.target = DummyVector3(0, 5, -5)
    forward = cam.get_forward()
    assert forward.x == pytest.approx(0.0)
    assert forward.y == pytest.approx(0.0)
    assert forward.z == pytest.approx(-1.0)

def test_get_forward_zero_length(mocked_camera_module):
    Camera = mocked_camera_module
    mock_engine = MagicMock()
    mock_engine.level_data.settings = {
        'cam_pos': (0, 0, 0),
        'cam_target': (0, 0, -1)
    }

    cam = Camera(mock_engine)

    # Identical position and target
    cam.pos_3d = DummyVector3(5, 5, 5)
    cam.target = DummyVector3(5, 5, 5)
    forward = cam.get_forward()

    assert forward.x == 0.0
    assert forward.y == 0.0
    assert forward.z == 0.0
    assert isinstance(forward, DummyVec3)
