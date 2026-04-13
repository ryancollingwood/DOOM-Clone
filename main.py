import raylib.defines
from settings import *
from engine import Engine
import cProfile


class App:
    ray.set_trace_log_level(ray.LOG_ERROR)
    ray.set_config_flags(ray.FLAG_MSAA_4X_HINT)
    #
    ray.init_window(WIN_WIDTH, WIN_HEIGHT, 'BSP Engine')
    #
    ray.hide_cursor()
    ray.disable_cursor()

    def __init__(self, udmf_path=None):
        self.dt = 0.0
        self.engine = Engine(app=self, udmf_path=udmf_path)

    def run(self):
        while not ray.window_should_close():
            self.dt = ray.get_frame_time()
            self.engine.update()
            self.engine.draw()
        #
        ray.close_window()


if __name__ == '__main__':
    import sys
    udmf_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = App(udmf_path=udmf_path)
    app.run()
