import ast
import copy
from pathlib import Path

from buildhelper.mod_class import ModFinder
from buildhelper.modhelper import FoundModule


class Loader:
    def __init__(self, main: Path) -> None:
        self._main = main
        self._contents = main.read_text()
        self._tree = ast.parse(self._contents)
        self.tree = copy.deepcopy(self._tree)
        self.mods: list[FoundModule] = []
        
    def search_modules(self):
        module_finder = ModFinder()
        module_finder.visit(self.tree)
        
        for mod in module_finder.imports:
            module = FoundModule(
                mod,
                ()
            )
            
            self.mods.append(module)
        