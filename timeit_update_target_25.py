import timeit
import glm
import math

class DummyCam:
    def __init__(self):
        self.cam_step = glm.vec3(1.0, 2.0, 3.0)
        self.pos_3d = glm.vec3(1.0, 2.0, 3.0)
        self.target = glm.vec3(4.0, 5.0, 6.0)
        self.MAX_BOUND = 10000.0

    def move_orig(self):
        dx, dy, dz = self.cam_step
        self.move_x(dx)
        self.move_y(dy)
        self.move_z(dz)

    def move_x(self, dx):
        if not math.isfinite(dx):
            return
        old_x = self.pos_3d.x
        self.pos_3d.x = glm.clamp(old_x + dx, -self.MAX_BOUND, self.MAX_BOUND)
        self.target.x += self.pos_3d.x - old_x

    def move_y(self, dy):
        if not math.isfinite(dy):
            return
        old_y = self.pos_3d.y
        self.pos_3d.y = glm.clamp(old_y + dy, -self.MAX_BOUND, self.MAX_BOUND)
        self.target.y += self.pos_3d.y - old_y

    def move_z(self, dz):
        if not math.isfinite(dz):
            return
        old_z = self.pos_3d.z
        self.pos_3d.z = glm.clamp(old_z + dz, -self.MAX_BOUND, self.MAX_BOUND)
        self.target.z += self.pos_3d.z - old_z

    def move_opt(self):
        dx, dy, dz = self.cam_step
        self.move_x_opt(dx)
        self.move_y_opt(dy)
        self.move_z_opt(dz)

    def move_x_opt(self, dx):
        if not math.isfinite(dx):
            return
        old_x = self.pos_3d.x
        self.pos_3d.x = max(-self.MAX_BOUND, min(old_x + dx, self.MAX_BOUND))
        self.target.x += self.pos_3d.x - old_x

    def move_y_opt(self, dy):
        if not math.isfinite(dy):
            return
        old_y = self.pos_3d.y
        self.pos_3d.y = max(-self.MAX_BOUND, min(old_y + dy, self.MAX_BOUND))
        self.target.y += self.pos_3d.y - old_y

    def move_z_opt(self, dz):
        if not math.isfinite(dz):
            return
        old_z = self.pos_3d.z
        self.pos_3d.z = max(-self.MAX_BOUND, min(old_z + dz, self.MAX_BOUND))
        self.target.z += self.pos_3d.z - old_z

cam = DummyCam()

print("orig:", timeit.timeit(cam.move_orig, number=1000000))
print("opt:", timeit.timeit(cam.move_opt, number=1000000))
