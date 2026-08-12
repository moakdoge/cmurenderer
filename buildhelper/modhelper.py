import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Self
from . import ROOT
@dataclass(slots=True)
class FoundModule:
    module: str
    imports: tuple[str, ...]


    '''
    TODO: implement
    @classmethod
    def from_ast_node(cls, node: ast.AST) -> Self:
        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                raise NotImplementedError(f"We only support import_from and import!")
            return cls(node.module, tuple([n.name for n in node.names]))

        if isinstance(node, ast.Import):
            for alias in node.names:
                print(alias.name)
    '''       
       
    @property
    def path(self) -> Path:
        path = ROOT / (self.module.replace(".", "/") + ".py")
        if path.exists():
            return path

        init_path = ROOT / self.module.replace(".", "/") / "__init__.py"
        if init_path.exists():
            return init_path
        
        raise FileNotFoundError(f"Module {self.module} not found!")
    
    @property
    def source(self) -> str:
        return self.path.read_text()