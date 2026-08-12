from pathlib import Path


ROOT: Path = Path()


def init(root: Path):
    global ROOT
    ROOT = root