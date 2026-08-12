import ast
from typing import Any

class ModFinder(ast.NodeTransformer):
    def __init__(self, strip_imports: bool = False) -> None:
        self.imports: set[str] = set()
        self.import_from: set[tuple[str, tuple[str, ...]]] = set()
        self._strip = strip_imports
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module:
            names = tuple(n.name for n in node.names)
            self.import_from.add((node.module, names))
        if self._strip:
            return ast.Pass()
        return node
    
    def visit_Import(self, node: ast.Import) -> Any:
        if node.names:
            for mod in node.names:
                self.imports.add(mod.name)
        if self._strip:
            return ast.Pass()
        return node