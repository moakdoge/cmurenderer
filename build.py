from pathlib import Path
import buildhelper
from buildhelper.loader import Loader

buildhelper.init(Path(__file__).parent)

main = Loader(
    buildhelper.ROOT / "main.py",
    "engine"
)

contents = main.run()

with open(buildhelper.ROOT / "cmu_bundle.py", "w") as f:
    f.write(contents)