#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class Tree:
    def __init__(self) -> None:
        self.dirCount = 0
        self.fileCount = 0

    def register(self, absolute: str) -> None:
        if os.path.isdir(absolute):
            self.dirCount += 1
        else:
            self.fileCount += 1

    def summary(self) -> str:
        return f"{self.dirCount} directories, {self.fileCount} files"

    def walk(self, directory: str, prefix: str = "", remaining_depth: int = 99999) -> None:
        if not remaining_depth:
            return
        filepaths = sorted(os.listdir(directory))

        for index in range(len(filepaths)):
            if filepaths[index].startswith("."):
                continue

            absolute = os.path.join(directory, filepaths[index])
            self.register(absolute)

            if index == len(filepaths) - 1:
                print(f"{prefix}└── {filepaths[index]}")
                if os.path.isdir(absolute):
                    self.walk(absolute, prefix + "    ", remaining_depth - 1)
            else:
                print(f"{prefix}├── {filepaths[index]}")
                if os.path.isdir(absolute):
                    self.walk(absolute, prefix + "│   ", remaining_depth - 1)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Display the structure of a directory")
    parser.add_argument("directory", type=str, help="The directory to display")
    parser.add_argument(
        "--depth",
        type=int,
        default=99999,
        help="The maximum depth to display",
    )

    args = parser.parse_args(args=argv)

    tree = Tree()
    tree.walk(args.directory, remaining_depth=args.depth)
    print(tree.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
