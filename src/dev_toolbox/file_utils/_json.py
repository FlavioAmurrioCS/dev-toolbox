from __future__ import annotations

from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import TypeVar

T = TypeVar("T")


def partition_by_condition(
    iterable: Iterable[T], start_predicate: Callable[[T], bool]
) -> Iterator[list[T]]:
    chunk: list[T] = []
    for item in iterable:
        if start_predicate(item):
            if chunk:
                yield chunk
            chunk = []
        chunk.append(item)
    if chunk:
        yield chunk


def stream_json_objects(
    filename: str,
    json_loader: Callable[[bytes], T] | None = None,
) -> Generator[T]:
    if json_loader is None:
        import json

        json_loader = json.loads
    with open(filename, "rb") as f:
        yield from (
            json_loader(b"".join(chunk))
            for chunk in partition_by_condition(f, lambda x: x.startswith(b"{"))
        )
