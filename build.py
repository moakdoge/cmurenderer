from pathlib import Path
import buildhelper
from buildhelper.loader import Loader

buildhelper.init(Path(__file__).parent)

main = Loader(buildhelper.ROOT / "main.py")

main.search_modules()