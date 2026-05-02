from pathlib import Path
import ast

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
            for i in range(node.lineno, node.end_lineno + 1):
                remove_lines.add(i)

    return "\n".join(
        line for i, line in enumerate(lines, start=1)
        if i not in remove_lines
    )


def add_file(path: Path):
    path = path.resolve()

    if path in seen:
        return

    seen.add(path)

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        dep = local_import_path(node)
        if dep:
            add_file(dep)

    cleaned = strip_local_imports(source)

    parts.append(f"\n\n# ===== {path.relative_to(ROOT)} =====\n")
    parts.append(cleaned)


add_file(ENTRY)

OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"Wrote {OUT}")