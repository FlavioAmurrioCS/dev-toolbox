from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar

    T = TypeVar("T")


def obj_compare(a: T, b: T) -> bool:  # noqa: PLR0911, C901
    if type(a) is not type(b):
        return False

    mapping_types = (dict, Mapping)
    if isinstance(a, mapping_types):
        if not isinstance(b, mapping_types):
            return False

        if len(a) != len(b):
            return False

        for key in a:
            if key not in b:  # type: ignore[operator]
                return False
            if not obj_compare(a[key], b[key]):  # type: ignore[index]
                return False

        return True

    sequence_types = (list, tuple)
    if isinstance(a, sequence_types):
        if not isinstance(b, sequence_types):
            return False

        if len(a) != len(b):
            return False

        return all(obj_compare(left, right) for left, right in zip(a, b))

    return a == b
