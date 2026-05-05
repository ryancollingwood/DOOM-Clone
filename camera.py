import math
from settings import *


class Camera:
    def __init__(self, engine):
        self.app = engine.app
        self.engine = engine
        #
        self.fake_up = vec3(0.0, 1.0, 0.0)
        #
        self.m_cam: ray.Camera3D = self.get_camera()
        #
        self.target: ray.Vector3 = self.m_cam.target
        self.pos_3d: ray.Vector3 = self.m_cam.position
        self.pos_2d: glm.vec2 = vec2(self.pos_3d.x, self.pos_3d.z)
        #
        self.speed = CAM_SPEED
        self.rot_speed = CAM_ROT_SPEED
        self.cam_step = vec3(0)
        #
        self.forward = vec3(0)
        self.right = vec3(0)
        #
        self.pitch = 0.0

    def set_yaw(self):
        m_dx = ray.get_mouse_delta().x
        if not math.isfinite(m_dx):
            return
        delta_yaw = -m_dx * self.rot_speed
        #
        new_target_pos = glm.rotateY(self.forward, delta_yaw)
        self.update_target(new_target_pos)

    def set_pitch(self):
        m_dy = ray.get_mouse_delta().y
        if not math.isfinite(m_dy):
            return
        delta_pitch = -m_dy * self.rot_speed
        self.pitch += delta_pitch
        #
        if not math.isfinite(self.pitch):
            self.pitch = 0.0
            return
        #
        if -PITCH_LIMIT < self.pitch < PITCH_LIMIT:
            new_target_pos = glm.rotate(self.get_forward(), delta_pitch, self.right)
            self.update_target(new_target_pos)
        else:
            # Optimization: Replaced PyGLM's glm.clamp with standard Python max/min functions.
            # Bypassing the C-extension function call overhead yields a measurable execution speedup
            # while remaining more readable than dense ternary expressions.
            self.pitch = max(-PITCH_LIMIT, min(self.pitch, PITCH_LIMIT))

    def update_target(self, new_target_pos: vec3):
        self.target.x = self.pos_3d.x + new_target_pos.x
        self.target.y = self.pos_3d.y + new_target_pos.y
        self.target.z = self.pos_3d.z + new_target_pos.z

    def pre_update(self):
        self.init_cam_step()
        self.update_vectors()

    def update(self):
        self.check_cam_step()
        self.update_pos_2d()
        self.set_yaw()
        self.set_pitch()
        self.move()

    def update_vectors(self):
        self.forward = self.get_forward()
        self.right = cross(self.forward, self.fake_up)

    def get_forward(self) -> glm.vec3:
        # Optimization: Inline scalar math to avoid intermediate object allocation overhead and C-extension function calls.
        dx = self.target.x - self.pos_3d.x
        dy = self.target.y - self.pos_3d.y
        dz = self.target.z - self.pos_3d.z
        length = (dx * dx + dy * dy + dz * dz) ** 0.5
        if length == 0:
            return vec3(0)
        return vec3(dx / length, dy / length, dz / length)

    def init_cam_step(self):
        dt = self.app.dt
        if not math.isfinite(dt) or dt < 0:
            dt = 0
        dt = min(dt, MAX_SAFE_DT)
        #
        self.speed = CAM_SPEED * dt
        self.rot_speed = CAM_ROT_SPEED * dt
        self.cam_step *= 0

    def step_forward(self):
        self.cam_step += self.speed * self.forward

    def step_back(self):
        self.cam_step += -self.speed * self.forward

    def step_left(self):
        self.cam_step += -self.speed * self.right

    def step_right(self):
        self.cam_step += self.speed * self.right

    def step_up(self):
        self.cam_step += self.speed * self.fake_up

    def step_down(self):
        self.cam_step += -self.speed * self.fake_up

    def check_cam_step(self):
        dx, dz = self.cam_step.xz
        if dx and dz:
            self.cam_step *= CAM_DIAG_MOVE_CORR

    def move(self):
        dx, dy, dz = self.cam_step

        # Optimization: Inlining boundary evaluation using standard Python conditional limits
        # avoids PyGLM wrapper function calls (glm.clamp) and function call overhead over move_*
        # methods, eliminating C-extension bridging overhead and improving execution speed.

        if math.isfinite(dx):
            old_x = self.pos_3d.x
            new_x = old_x + dx
            self.pos_3d.x = new_x if -MAX_WORLD_BOUNDARY <= new_x <= MAX_WORLD_BOUNDARY else (-MAX_WORLD_BOUNDARY if new_x < -MAX_WORLD_BOUNDARY else MAX_WORLD_BOUNDARY)
            self.target.x += self.pos_3d.x - old_x

        if math.isfinite(dy):
            old_y = self.pos_3d.y
            new_y = old_y + dy
            self.pos_3d.y = new_y if -MAX_WORLD_BOUNDARY <= new_y <= MAX_WORLD_BOUNDARY else (-MAX_WORLD_BOUNDARY if new_y < -MAX_WORLD_BOUNDARY else MAX_WORLD_BOUNDARY)
            self.target.y += self.pos_3d.y - old_y

        if math.isfinite(dz):
            old_z = self.pos_3d.z
            new_z = old_z + dz
            self.pos_3d.z = new_z if -MAX_WORLD_BOUNDARY <= new_z <= MAX_WORLD_BOUNDARY else (-MAX_WORLD_BOUNDARY if new_z < -MAX_WORLD_BOUNDARY else MAX_WORLD_BOUNDARY)
            self.target.z += self.pos_3d.z - old_z

    def update_pos_2d(self):
        # 2d position on xz plane
        self.pos_2d[0] = self.pos_3d.x
        self.pos_2d[1] = self.pos_3d.z

    def get_camera(self):
        cam = ray.Camera3D(
            self.engine.level_data.settings['cam_pos'],
            self.engine.level_data.settings['cam_target'],
            self.fake_up.to_tuple(),
            FOV_Y_DEG,
            ray.CAMERA_PERSPECTIVE
        )
        return cam
