import cProfile
from main import App
import raylib.defines
import pyray as ray

app = App()
profiler = cProfile.Profile()
profiler.enable()
for _ in range(100):
    app.dt = ray.get_frame_time()
    app.engine.update()
    app.engine.draw()
profiler.disable()
profiler.dump_stats("profile.stats")
