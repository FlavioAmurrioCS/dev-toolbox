from __future__ import annotations

import argparse
import inspect
import os
import pkgutil
import re
from typing import TYPE_CHECKING

from dev_toolbox.data_structures.tree import TreeNode

if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterable
    from collections.abc import Sequence
    from types import ModuleType


def get_class_relations(files: list[str]) -> set[tuple[str, str]]:
    relations: set[tuple[str, str]] = set()
    for file in files:
        with open(file) as f:
            for line in f:
                if line.startswith("class "):
                    _, child, parent, *_ = re.split(r"[^a-zA-Z0-9_]+", line)
                    parent = parent or "object"
                    relations.add((parent, child))
    return relations


def iter_modules(modules: Iterable[ModuleType]) -> Generator[ModuleType, None, None]:
    # seen = set()
    seen = set()
    for module in modules:
        if module.__name__ not in seen:
            seen.add(module.__name__)
            yield module
        for _, name, _ in pkgutil.walk_packages(module.__path__, f"{module.__name__}."):
            if name not in seen:
                seen.add(name)
                yield __import__(name, fromlist=["_trash"])


def get_relations(modules: Iterable[ModuleType | str]) -> set[tuple[str, str]]:
    relations: set[tuple[str, str]] = set()

    _modules: Iterable[ModuleType] = (
        (__import__(_module, fromlist=["_trash"]) if isinstance(_module, str) else _module)
        for _module in modules
    )

    for module in iter_modules(_modules):
        # print(f"{module.__name__=}")
        for cls_name, clz in inspect.getmembers(module, inspect.isclass):
            if not clz.__module__.startswith(module.__name__):
                continue
            _, *rest = inspect.getmro(clz)
            for parent in rest[:1]:
                relations.add((parent.__name__, cls_name))

    return relations


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print tree of classes.")
    parser.add_argument("files_or_modules", nargs="*", help="Files to process.")
    parser.add_argument("--root", help="Modules to process.", default=".")
    args = parser.parse_args(argv)
    if os.path.exists(args.files_or_modules[0]) and os.path.isfile(args.files_or_modules[0]):
        relations = get_class_relations(args.files_or_modules)
    else:
        relations = get_relations(args.files_or_modules)

    tree_top_nodes = TreeNode.build_tree(list(relations))
    TreeNode(data="args.root", children=tree_top_nodes).print_tree()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
