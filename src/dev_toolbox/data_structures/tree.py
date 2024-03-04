#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from functools import lru_cache
from typing import Callable
from typing import Generator
from typing import Generic
from typing import Hashable
from typing import Sequence
from typing import TYPE_CHECKING
from typing import TypeVar


if TYPE_CHECKING:
    from typing_extensions import Self

_T = TypeVar("_T", bound=Hashable)


@dataclass(unsafe_hash=True)
class TreeNode(Generic[_T]):
    """Node for tree."""

    data: _T = field(hash=True)
    parent: Self | None = field(default=None, hash=False)
    children: list[Self] = field(default_factory=list, hash=False)

    @classmethod
    def build_tree(cls, parent_child_connections: list[tuple[_T, _T]]) -> list[Self]:
        """Build tree from connections."""
        nodes: dict[_T, Self] = {}
        for parent, child in parent_child_connections:
            if parent not in nodes:
                nodes[parent] = cls(data=parent)
            if child not in nodes:
                nodes[child] = cls(data=child)
            nodes[parent].children.append(nodes[child])
            nodes[child].parent = nodes[parent]

        for node in nodes.values():
            node.children = sorted(node.children, key=lambda x: (cls.children_count(x), x.data))
        return sorted(
            (v for v in nodes.values() if v.parent is None),
            key=lambda x: (cls.children_count(x), x.data),
        )

    def connections(self) -> Generator[tuple[_T, _T], None, None]:
        """Get connections."""
        for child in self.children:
            yield (self.data, child.data)
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

    def print_node(self, level: int = 0, _repr: Callable[[_T], str] = str) -> None:
        """Print node."""
        print("  " * level + "- " + _repr(self.data))
        for child in self.children:
            child.print_node(level + 1, _repr=_repr)

    def print_tree(self, *, prefix: str = "", _repr: Callable[[_T], str] = str) -> None:
        if not prefix:
            print(_repr(self.data))
        for i, child in enumerate(self.children):
            if i == len(self.children) - 1:
                print(f"{prefix}└── {_repr(child.data)}")
                child.print_tree(prefix=prefix + "    ", _repr=_repr)
            else:
                print(f"{prefix}├── {_repr(child.data)}")
                child.print_tree(prefix=f"{prefix}│   ", _repr=_repr)

    @classmethod
    def parse_indent_hierarchy(cls, lines: Sequence[str]) -> list[Self]:
        """Parse indent hierarchy."""
        parent_child_connections: list[tuple[str, str]] = []
        stack: list[tuple[int, str]] = []
        for line in lines:
            indent = len(line) - len(line.lstrip())
            while stack and indent <= stack[-1][0]:
                stack.pop()
            if stack:
                parent = stack[-1][1]
                child = line.strip()
                parent_child_connections.append((parent, child))
            stack.append((indent, line.strip()))
        return cls.build_tree(parent_child_connections)  # type: ignore[arg-type]
