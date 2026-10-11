#!/bin/bash
export PYTHONPATH=.
xvfb-run pytest tests/test_input_handler.py
xvfb-run pytest tests/test_map_renderer.py
xvfb-run pytest tests/test_camera.py
xvfb-run pytest tests/test_engine.py
xvfb-run pytest tests/test_utils.py
