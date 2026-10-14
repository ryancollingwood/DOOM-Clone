import sys

content = ""
with open("bsp/bsp_builder.py", "r") as f:
    content = f.read()

# Replace the part that's causing issues. I should just use `node.splitter_c` which already exists.
