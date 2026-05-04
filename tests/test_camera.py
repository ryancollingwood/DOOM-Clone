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

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __add__(self, other):
        return DummyVec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        return DummyVec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return DummyVec3(self.x * other, self.y * other, self.z * other)
        return DummyVec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
        else:
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        return self

    @property
    def xz(self):
        return (self.x, self.z)

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

def test_camera_step_methods(mocked_camera_module):
    Camera = mocked_camera_module
    mock_engine = MagicMock()
    mock_engine.app.dt = 0.1
    mock_engine.level_data.settings = {
        'cam_pos': (0, 0, 0),
        'cam_target': (0, 0, -1)
    }
    with patch('camera.CAM_SPEED', 10):
        cam = Camera(mock_engine)
        cam.forward = DummyVec3(1, 0, 0)
        cam.right = DummyVec3(0, 0, 1)
        cam.fake_up = DummyVec3(0, 1, 0)
        cam.speed = 1.0 # 10 * 0.1
        cam.cam_step = DummyVec3(0, 0, 0)

        cam.step_forward()
        assert cam.cam_step.x == 1.0
        assert cam.cam_step.y == 0.0
        assert cam.cam_step.z == 0.0

        cam.cam_step = DummyVec3(0, 0, 0)
        cam.step_back()
        assert cam.cam_step.x == -1.0

        cam.cam_step = DummyVec3(0, 0, 0)
        cam.step_left()
        assert cam.cam_step.z == -1.0

        cam.cam_step = DummyVec3(0, 0, 0)
        cam.step_right()
        assert cam.cam_step.z == 1.0

        cam.cam_step = DummyVec3(0, 0, 0)
        cam.step_up()
        assert cam.cam_step.y == 1.0

        cam.cam_step = DummyVec3(0, 0, 0)
        cam.step_down()
        assert cam.cam_step.y == -1.0

def test_camera_move_integration(mocked_camera_module):
    Camera = mocked_camera_module
    mock_engine = MagicMock()
    mock_engine.level_data.settings = {
        'cam_pos': (0, 0, 0),
        'cam_target': (0, 0, -1)
    }
    cam = Camera(mock_engine)
    cam.pos_3d = DummyVector3(0, 0, 0)
    cam.target = DummyVector3(0, 0, -1)
    cam.cam_step = DummyVec3(1, -2, 3)

    cam.move()

    assert cam.pos_3d.x == 1
    assert cam.pos_3d.y == -2
    assert cam.pos_3d.z == 3
    assert cam.target.x == 1
    assert cam.target.y == -2
    assert cam.target.z == 2 # -1 + 3

    # Boundary tests
    cam.cam_step = DummyVec3(20000, -20000, float('inf'))
    cam.move()
    assert cam.pos_3d.x == 10000.0
    assert cam.pos_3d.y == -10000.0
    assert cam.pos_3d.z == 3 # unchanged because of float('inf')

def test_camera_check_cam_step(mocked_camera_module):
    Camera = mocked_camera_module
    mock_engine = MagicMock()
    mock_engine.level_data.settings = {
        'cam_pos': (0, 0, 0),
        'cam_target': (0, 0, -1)
    }
    with patch('camera.CAM_DIAG_MOVE_CORR', 0.5):
        cam = Camera(mock_engine)

        # No movement
        cam.cam_step = DummyVec3(0, 0, 0)
        cam.check_cam_step()
        assert cam.cam_step.x == 0
        assert cam.cam_step.z == 0

        # Only X movement
        cam.cam_step = DummyVec3(1, 0, 0)
        cam.check_cam_step()
        assert cam.cam_step.x == 1
        assert cam.cam_step.z == 0

        # Only Z movement
        cam.cam_step = DummyVec3(0, 0, 1)
        cam.check_cam_step()
        assert cam.cam_step.x == 0
        assert cam.cam_step.z == 1

        # Diagonal movement
        cam.cam_step = DummyVec3(1, 0, 1)
        cam.check_cam_step()
        assert cam.cam_step.x == 0.5
        assert cam.cam_step.z == 0.5
