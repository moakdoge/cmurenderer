import ast
import copy
from pathlib import Path

from buildhelper.mod_class import ModFinder
from buildhelper.modhelper import FoundModule


class Loader:
    def __init__(self, 
                 main: Path,
                 core_lib: str
        ) -> None:
        self.main = main
        self.core = core_lib
        self._core_mod = FoundModule(core_lib, ())
        self._contents = main.read_text()
        self._tree: ast.Module
        self.tree: ast.Module 
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
            if len(mod.imports) > 0:
                new = ast.ImportFrom(module=mod.module, names=[ast.alias(name=i) for i in mod.imports]) # type: ignore
            else:
                new = ast.Import(names=[ast.alias(name=mod.module)])
            
            parts.append(new)
            
        return parts
    def generate_source(self):
        return ast.unparse(self.tree)
    
    def combine_modules(self):
        parts: list[str] = [self._contents]
        for mod in self.mods:
            try:
                parts.insert(0, mod.source)
                print(f"Added: {mod.module}")
            except FileNotFoundError as e:
                print(f"Mod: {mod} failed")
                pass
            
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
        parent = self._core_mod.path.parent
        for py in parent.rglob("*.py"):
            fixed_parts = list(py.parts)
            fixed_parts[-1] = fixed_parts[-1].split(".")[0]
            mod_name = ".".join(fixed_parts)
            
            if fixed_parts[-1] != "__init__":
                self.mods.append(FoundModule(
                    mod_name,
                    ()
                ))