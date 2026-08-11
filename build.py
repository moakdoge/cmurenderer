import datetime
from pathlib import Path
import ast
from typing import Any

ROOT = Path(__file__).parent
ENTRY = ROOT / "main.py"
OUT = ROOT / "cmu_bundle.py"

seen = set()
parts = []


def module_to_path(module: str) -> Path | None:
    path = ROOT / (module.replace(".", "/") + ".py")
    if path.exists():
        return path

    init_path = ROOT / module.replace(".", "/") / "__init__.py"
    if init_path.exists():
        return init_path

    return None


def local_import_path(node: ast.AST) -> Path | None:
    if isinstance(node, ast.ImportFrom):
        if node.module is None:
            return None
        return module_to_path(node.module)

    if isinstance(node, ast.Import):
        for alias in node.names:
            path = module_to_path(alias.name)
            if path:
                return path

    return None


def strip_local_imports(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()

    remove_lines = set()

    for node in tree.body:
        path = local_import_path(node)
        if path:
            for i in range(node.lineno, node.end_lineno + 1): # type: ignore
                remove_lines.add(i)

    return "\n".join(
        line for i, line in enumerate(lines, start=1)
        if i not in remove_lines
    )

import io
import tokenize


def strip_comments_and_blank_lines(source: str) -> str:
    out = []

    for line in source.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        out.append(line.rstrip())

    return "\n".join(out)


class ReleaseOptimizer(ast.NodeTransformer):
    def visit_Assert(self, node):
        return None

    def visit_FunctionDef(self, node):
        #self.generic_visit(node)

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body.pop(0)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body.pop(0)
        self.generic_visit(node)
        return node

    def visit_Module(self, node):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body.pop(0)

        self.generic_visit(node)
        return node
        
    def visit_If(self, node):
        # Remove: if TYPE_CHECKING:
        if (
            isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        ):
            return ast.Pass()

        # Fold: if False:
        if isinstance(node.test, ast.Constant):
            if node.test.value is False:
                # Keep the else branch, if present.
                return node.orelse or ast.Pass()

            if node.test.value is True:
                # Keep the body and discard the else branch.
                return node.body

        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            name = None

        if name == "is_web":
            return ast.Constant(True)
        
        if name == "is_desktop":
            return ast.Constant(False)

        self.generic_visit(node)
        return node
    
def add_file(path: Path):
    path = path.resolve()

    if path in seen:
        return

    seen.add(path)

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    tree = ReleaseOptimizer().visit(tree)
    tree = ReleaseOptimizer().visit(tree)
   # tree = ReleaseOptimizer().visit(tree)
    ast.fix_missing_locations(tree)

    optimized_source = ast.unparse(tree)

    source = strip_local_imports(optimized_source)
    for node in tree.body:
        
        dep = local_import_path(node)
        if dep:
            add_file(dep)

    cleaned = strip_local_imports(source)
    cleaned = strip_comments_and_blank_lines(cleaned)
    parts.append(f"\n\n# ===== {path.relative_to(ROOT)} =====\n")
    parts.append(cleaned)




add_file(ENTRY)

part1 = [
    "### CREATED BY @MOAKDOGE ###",
    f"### CREATED ON: {datetime.datetime.now().strftime("%D")} ###"
]

for line in part1[::-1]:
    parts.insert(0, line)
OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"Wrote {OUT}")