"""Проверяет направление статических импортов между слоями."""

import ast
from importlib.util import resolve_name
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {
    "domain": {"application", "infrastructure", "presentation"},
    "application": {"infrastructure", "presentation"},
    "infrastructure": {"presentation"},
    "presentation": set(),
}
ADAPTER_LIBRARIES = {"argparse", "click", "fastapi", "filelock", "flask", "sqlite3"}


def targets(node, package: str) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if not isinstance(node, ast.ImportFrom):
        return []
    module = node.module or ""
    if node.level:
        module = resolve_name("." * node.level + module, package)
    return [module, *(f"{module}.{alias.name}" for alias in node.names)]


def main() -> int:
    problems = []
    for file in sorted((ROOT / "src").rglob("*.py")):
        path = file.relative_to(ROOT)
        if len(path.parts) < 3:
            continue
        layer = path.parts[1]
        package = ".".join(path.parent.parts)
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for target in targets(node, package):
                parts = target.split(".")
                forbidden_layer = len(parts) > 1 and parts[0] == "src" and parts[1] in FORBIDDEN[layer]
                forbidden_library = layer in {"domain", "application"} and parts[0] in ADAPTER_LIBRARIES
                if forbidden_layer or forbidden_library:
                    problems.append(f"{path.as_posix()}:{node.lineno}: {layer} импортирует {target}")
    if problems:
        print("\n".join(problems))
        return 1
    print("Направления зависимостей между слоями соблюдены.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
