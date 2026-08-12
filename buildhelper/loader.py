import ast
import copy
from pathlib import Path
from typing import Optional

from buildhelper.mod_class import ModFinder
from buildhelper.modhelper import FoundModule


class Loader:
    def __init__(self, 
                 main: Path,
                 core_lib: str,
                 *,
                 ignore_packages: Optional[list[str]] = None
        ) -> None:
        self.main = main
        self.core = core_lib
        self._core_mod = FoundModule(core_lib, ())
        self._contents = main.read_text()
        self._tree: ast.Module
        self.tree: ast.Module 
        self.ignore = ignore_packages or []
        self.mods: list[FoundModule] = []

        
    def generate_tree(self):
        self._tree: ast.Module = ast.parse(self._contents)
        self.tree: ast.Module = copy.deepcopy(self._tree)
        
    def run(self) -> str:
        '''Returns a fixed source'''
        self.generate_tree()
        
        #create and combine scripts
        self.search_core_modules()
        self.combine_modules()
        
        #find essentials
        self.search_builtins()
    
        #strip imports
        self.strip_modules()
        
        #re-add mods
        self.tree = [
            *self.generate_mods(), 
            *self.tree.body
        ] # type: ignore
        
        return self.generate_source()
        
        
    def generate_mods(self) -> list[ast.ImportFrom | ast.Import]:
        parts = []
        for mod in self.mods:
            if mod.module in self.ignore:
                continue
            if len(mod.imports) > 0:
                new = ast.ImportFrom(module=mod.module, names=[ast.alias(name=i) for i in mod.imports]) # type: ignore
            else:
                new = ast.Import(names=[ast.alias(name=mod.module)])
            
            parts.append(new)
            
        return parts
    def generate_source(self):
        return ast.unparse(self.tree)
    
    def combine_modules(self):
        parts: list[str] = []
        for mod in self.mods:
            try:
                parts.append(mod.source)
                print(f"Added: {mod.module}")
            except FileNotFoundError as e:
                print(f"Mod: {mod} failed")
                pass
        
        parts.append(self._contents)
        new_source = "\n".join(parts)
        self._contents = new_source
        self.generate_tree()
        
    def strip_modules(self):
        module_stripper = ModFinder(strip_imports=True)
        self.tree = module_stripper.visit(self.tree)
    
    def search_builtins(self):
        mod_find = ModFinder(strip_imports=False)
        mod_find.visit(self.tree)
        
        self.mods = []
        for mod in mod_find.imports:
            if mod.startswith(self.core):
                continue
            self.mods.append(FoundModule(mod, ()))
        
        for mod, imps in mod_find.import_from:
            if mod.startswith(self.core):
                continue
            self.mods.append(FoundModule(
                mod,
                imps
            ))
            
            
    
    def search_core_modules(self):
        root = self._core_mod.path.parent.resolve()
        seen: set[Path] = set()
        ordered: list[FoundModule] = []

        def module_name_for(py: Path) -> str:
            relative = py.relative_to(root.parent)
            parts = list(relative.parts)
            if parts[-1] == "__init__.py":
                parts = parts[:-1]
            else:
                parts[-1] = py.stem
            return ".".join(parts)

        def load(py: Path):
            py = py.resolve()
            if py in seen:
                return
            seen.add(py)

            source = py.read_text(encoding="utf-8")
            tree = ast.parse(source)

            finder = ModFinder(strip_imports=False)
            finder.visit(tree)

            imports: list[str] = []
            for mod in finder.imports:
                if mod.startswith(self.core):
                    imports.append(mod)
            for mod, _ in finder.import_from:
                if mod.startswith(self.core):
                    imports.append(mod)

            imports = list(dict.fromkeys(imports))

            for imp in imports:
                dep = FoundModule(imp, ())
                if dep.module.startswith(self.core):
                    try:
                        load(dep.path)
                    except FileNotFoundError:
                        pass

            ordered.append(FoundModule(module_name_for(py), tuple(imports)))

        for py in root.rglob("*.py"):
            load(py)

        self.mods = ordered