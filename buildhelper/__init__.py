from pathlib import Path


ROOT: Path


def init(root: Path):
    global root
    ROOT = root