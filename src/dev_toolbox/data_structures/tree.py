#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from functools import lru_cache
from typing import Generator
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing_extensions import Self


@dataclass(unsafe_hash=True)
class Node:
    """Node for tree."""

    name: str = field(hash=True)
    parent: Self | None = field(default=None, hash=False)
    children: list[Self] = field(default_factory=list, hash=False)

    @classmethod
    def build_tree(cls, parent_child_connections: list[tuple[str, str]]) -> list[Self]:
        """Build tree from connections."""
        nodes: dict[str, Self] = {}
        for parent, child in parent_child_connections:
            if parent not in nodes:
                nodes[parent] = cls(name=parent)
            if child not in nodes:
                nodes[child] = cls(name=child)
            nodes[parent].children.append(nodes[child])
            nodes[child].parent = nodes[parent]

        for node in nodes.values():
            node.children = sorted(node.children, key=lambda x: (cls.children_count(x), x.name))
        return sorted(
            (v for v in nodes.values() if v.parent is None),
            key=lambda x: (cls.children_count(x), x.name),
        )

    def connections(self) -> Generator[tuple[str, str], None, None]:
        """Get connections."""
        for child in self.children:
            yield (self.name, child.name)
            yield from child.connections()

    def nodes(self) -> Generator[Self, None, None]:
        """Get nodes."""
        yield self
        for child in self.children:
            yield from child.nodes()

    @classmethod
    @lru_cache(maxsize=None)
    def children_count(cls, node: Self) -> int:
        """Count children."""
        return sum(1 + cls.children_count(child) for child in node.children)

    def print_node(self, level: int = 0) -> None:
        """Print node."""
        print("  " * level + "- " + self.name)
        for child in self.children:
            child.print_node(level + 1)

    def print_tree(self, *, prefix: str = "") -> None:
        if not prefix:
            print(self.name)
        for i, child in enumerate(self.children):
            if i == len(self.children) - 1:
                print(f"{prefix}└── {child.name}")
                child.print_tree(prefix=prefix + "    ")
            else:
                print(f"{prefix}├── {child.name}")
                child.print_tree(prefix=f"{prefix}│   ")
