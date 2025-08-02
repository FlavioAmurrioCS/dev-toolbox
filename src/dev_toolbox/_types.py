from __future__ import annotations

from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import TypeVar
from typing import Union

if TYPE_CHECKING:
    from collections.abc import Sequence

    from typing_extensions import TypeAlias
    from typing_extensions import TypeGuard

    _T = TypeVar("_T")

    JSONValue: TypeAlias = Union[
        str, int, float, bool, None, list["JSONValue"], dict[str, "JSONValue"]
    ]


def is_list_of(lst: Sequence[object], tp: type[_T]) -> TypeGuard[list[_T]]:
    return isinstance(lst, list) and all(isinstance(x, tp) for x in lst)


def is_namedtuple(obj: object) -> TypeGuard[NamedTuple]:
    t = type(obj)
    b = t.__bases__
    if len(b) != 1 or b[0] is not tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(isinstance(n, str) for n in f)
