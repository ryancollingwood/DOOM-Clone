import cProfile
import pstats
import pyray as ray
from main import App

app = App()
app.dt = ray.get_frame_time()

def profile_it():
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(100):
        app.engine.update()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats(15)

profile_it()
