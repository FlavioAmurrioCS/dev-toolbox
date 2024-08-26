from __future__ import annotations

import functools
import itertools
from collections import defaultdict
from collections.abc import Sized
from itertools import islice
from typing import Generic
from typing import Iterable
from typing import overload
from typing import TYPE_CHECKING
from typing import TypeVar


if TYPE_CHECKING:
    from typing import Generator, TextIO, BinaryIO
    from typing import Any
    from typing import Iterator
    from typing import Callable
    from typing import Hashable
    from _typeshed import SupportsRichComparisonT
    from _typeshed import SupportsRichComparison
    from typing_extensions import TypeGuard
    from typing_extensions import TypeIs

    _HashableT = TypeVar("_HashableT", bound=Hashable)

    _T = TypeVar("_T")
    _U = TypeVar("_U")
    _V = TypeVar("_V")
    _W = TypeVar("_W")
    _R = TypeVar("_R")
    _S = TypeVar("_S")
    _K = TypeVar("_K")  # noqa: PYI018

_T_co = TypeVar("_T_co", covariant=True)


class NoItem: ...


class Stream(Generic[_T_co], Iterable[_T_co], Sized):
    __items: Iterable[_T_co]
    __slots__ = ("__items",)

    def __init__(self, items: Iterable[_T_co]) -> None:
        self.__items = items

    def map(self, func: Callable[[_T_co], _R]) -> Stream[_R]:
        # Lazy
        return Stream(func(x) for x in self.__items)

    @overload
    def filter(self: Stream[_U | None], predicate: None = ...) -> Stream[_U]: ...
    @overload
    def filter(self: Stream[_U], predicate: Callable[[_U], TypeGuard[_V]]) -> Stream[_V]: ...
    @overload
    def filter(self: Stream[_U], predicate: Callable[[_U], TypeIs[_V]]) -> Stream[_V]: ...
    @overload
    def filter(self: Stream[_U], predicate: Callable[[_U], Any]) -> Stream[_U]: ...
    def filter(self, predicate=None):  # type: ignore[no-untyped-def]
        # Lazy
        return Stream(filter(predicate, self.__items))

    def type_is(self: Stream[_U], cls: type[_V]) -> Stream[_V]:
        # Lazy
        return Stream(x for x in self.__items if isinstance(x, cls))

    @staticmethod
    def __unique_helper(
        items: Iterable[_U], key: Callable[[_U], _HashableT]
    ) -> Generator[_U, None, None]:
        seen: set[_HashableT] = set()
        for item in items:
            k = key(item)
            if k not in seen:
                seen.add(k)
                yield item

    @overload
    def unique(self: Stream[_HashableT], key: None = ...) -> Stream[_HashableT]: ...
    @overload
    def unique(self: Stream[_U], key: Callable[[_U], _HashableT]) -> Stream[_U]: ...
    def unique(self, key=None):  # type: ignore[no-untyped-def]
        # Lazy
        return Stream(self.__unique_helper(items=self.__items, key=(key or (lambda x: x))))

    def enumerate(self, start: int = 0) -> Stream[tuple[int, _T_co]]:
        # Lazy
        return Stream(enumerate(self.__items, start=start))

    def peek(self: Stream[_U], func: Callable[[_U], Any]) -> Stream[_U]:
        # Lazy
        def func_and_return(item: _U) -> _U:
            func(item)
            return item

        return Stream(func_and_return(x) for x in self.__items)

    def flatten(self: Stream[Iterable[_U]]) -> Stream[_U]:
        # Lazy
        return Stream(item for sub in self.__items for item in sub)

    def flat_map(self, func: Callable[[_T_co], Iterable[_U]]) -> Stream[_U]:
        # Lazy
        return Stream(item for x in self.__items for item in func(x))

    ############################################################################
    # region: Itertools methods
    ############################################################################

    @overload
    def islice(self, stop: int | None, /) -> Stream[_T_co]: ...
    @overload
    def islice(
        self, start: int | None, stop: int | None, step: int | None = ..., /
    ) -> Stream[_T_co]: ...
    def islice(self, *args) -> Stream[_T_co]:  # type: ignore[no-untyped-def]
        # Lazy
        return Stream(islice(self.__items, *args))

    def batched(self, size: int) -> Stream[tuple[_T_co, ...]]:
        # Lazy
        items = iter(self.__items)
        return Stream(iter(lambda: tuple(islice(items, size)), ()))

    ############################################################################
    # endregion: Itertools methods
    ############################################################################

    ############################################################################
    # region: Eager methods
    ############################################################################

    # region: Built-in methods
    @overload
    def min(
        self: Stream[SupportsRichComparisonT], /, *, key: None = None
    ) -> SupportsRichComparisonT: ...
    @overload
    def min(self: Stream[_U], /, *, key: Callable[[_U], SupportsRichComparison]) -> _U: ...
    @overload
    def min(
        self: Stream[SupportsRichComparisonT], /, *, key: None = None, default: _U
    ) -> SupportsRichComparisonT | _U: ...
    @overload
    def min(
        self: Stream[_U], /, *, key: Callable[[_U], SupportsRichComparison], default: _V
    ) -> _U | _V: ...
    def min(self, /, *, key=None, **kwargs):  # type: ignore[no-untyped-def]
        # Eager
        return min(self.__items, key=key, **kwargs)

    @overload
    def max(
        self: Stream[SupportsRichComparisonT], /, *, key: None = None
    ) -> SupportsRichComparisonT: ...
    @overload
    def max(self: Stream[_U], /, *, key: Callable[[_U], SupportsRichComparison]) -> _U: ...
    @overload
    def max(
        self: Stream[SupportsRichComparisonT], /, *, key: None = None, default: _U
    ) -> SupportsRichComparisonT | _U: ...
    @overload
    def max(
        self: Stream[_U], /, *, key: Callable[[_U], SupportsRichComparison], default: _V
    ) -> _U | _V: ...
    def max(self, /, *, key=None, **kwargs):  # type: ignore[no-untyped-def]
        # Eager
        return max(self.__items, key=key, **kwargs)

    @overload
    def sorted(
        self: Stream[SupportsRichComparisonT], /, *, key: None = None, reverse: bool = False
    ) -> Stream[SupportsRichComparisonT]: ...
    @overload
    def sorted(
        self: Stream[_T_co],
        /,
        *,
        key: Callable[[_T_co], SupportsRichComparison],
        reverse: bool = False,
    ) -> Stream[_T_co]: ...
    def sorted(self, /, *, key=None, reverse=False):  # type: ignore[no-untyped-def]
        # Eager
        return Stream(sorted(self.__items, key=key, reverse=reverse))

    def join(self: Stream[str], sep: str) -> str:
        # Eager
        return sep.join(self.__items)

    @overload
    def first(self, /) -> _T_co: ...
    @overload
    def first(self: Stream[_U], default: _V, /) -> _U | _V: ...
    def first(self, *args):  # type: ignore[no-untyped-def]
        # Eager
        return next(iter(self.__items), *args)

    # endregion: Built-in methods

    # region: Custom methods
    def find(self, func: Callable[[_T_co], object]) -> _T_co | type[NoItem]:
        # Eager
        return next((item for item in self.__items if func(item)), NoItem)

    def group_by(
        self, key: Callable[[_T_co], _HashableT]
    ) -> Stream[tuple[_HashableT, list[_T_co]]]:
        # Eager
        dct: dict[_HashableT, list[_T_co]] = defaultdict(list)
        for item in self.__items:
            dct[key(item)].append(item)
        return Stream(dct.items())

    def for_each(self, func: Callable[[_T_co], Any]) -> None:
        # Eager
        for item in self.__items:
            func(item)

    def cache(self) -> Stream[_T_co]:
        # Eager
        return Stream(tuple(self.__items))

    # endregion: Custom methods

    # region: Collectors
    def to_list(self) -> list[_T_co]:
        # Eager
        return list(self.__items)

    def to_tuple(self) -> tuple[_T_co, ...]:
        # Eager
        return tuple(self.__items)

    def to_set(self) -> set[_T_co]:
        # Eager
        return set(self.__items)

    def to_dict(self: Stream[tuple[_HashableT, _V]]) -> dict[_HashableT, _V]:
        # Eager
        return dict(self.__items)

    # endregion: Collectors

    def len(self) -> int:
        # Eager
        return len(self)

    def __len__(self) -> int:
        # Eager
        if not hasattr(self.__items, "__len__"):
            self.__items = tuple(self.__items)
        return len(self.__items)  # type: ignore[arg-type]

    ############################################################################
    # endregion: Eager methods
    ############################################################################

    def __iter__(self) -> Iterator[_T_co]:
        # Lazy
        return iter(self.__items)

    def __repr__(self) -> str:
        # Lazy
        return f"{self.__class__.__name__}({self.__items})"

    @overload
    @classmethod
    def from_io(cls, io: TextIO) -> Stream[str]: ...
    @overload
    @classmethod
    def from_io(cls, io: BinaryIO) -> Stream[bytes]: ...
    @classmethod
    def from_io(cls, io):  # type: ignore[no-untyped-def]
        """Note: The IO object will be closed after the stream is exhausted. Ignore SIM115."""

        def gen():  # type: ignore[no-untyped-def]  # noqa: ANN202
            with io as file:
                yield from file

        return cls(gen())

    @staticmethod
    def __sections_helper(
        items: Iterable[_U], predicate: Callable[[_U], object]
    ) -> Generator[tuple[_U, ...], None, None]:
        buffer: list[_U] = []
        for item in itertools.dropwhile(lambda x: not predicate(x), items):
            if predicate(item):
                if buffer:
                    yield tuple(buffer)
                buffer.clear()
            buffer.append(item)
        if buffer:
            yield tuple(buffer)

    def sections(self, predicate: Callable[[_T_co], object]) -> Stream[tuple[_T_co, ...]]:
        # Lazy
        return Stream(self.__sections_helper(self.__items, predicate))

    def take(self, n: int) -> Stream[_T_co]:
        # Lazy
        return Stream(itertools.islice(self.__items, n))

    def drop(self, n: int) -> Stream[_T_co]:
        # Lazy
        return Stream(itertools.islice(self.__items, n, None))

    def dropwhile(self, predicate: Callable[[_T_co], object]) -> Stream[_T_co]:
        # Lazy
        return Stream(itertools.dropwhile(predicate, self.__items))

    def takewhile(self, predicate: Callable[[_T_co], object]) -> Stream[_T_co]:
        # Lazy
        return Stream(itertools.takewhile(predicate, self.__items))

    @overload
    def sum(self: Stream[int], start: int = 0) -> int: ...
    @overload
    def sum(self: Stream[float], start: int = 0) -> float: ...
    def sum(self: Stream[int | float], start: int = 0) -> int | float:
        # Eager
        return sum(self.__items, start=start)

    @overload
    def zip(self, iter1: Iterable[_U], /) -> Stream[tuple[_T_co, _U]]: ...
    @overload
    def zip(self, iter1: Iterable[_U], iter2: Iterable[_V], /) -> Stream[tuple[_T_co, _U, _V]]: ...
    @overload
    def zip(
        self, iter1: Iterable[_U], iter2: Iterable[_V], iter3: Iterable[_W], /
    ) -> Stream[tuple[_T_co, _U, _V, _W]]: ...
    def zip(self: Stream[_U], *iterables: Iterable[_U]) -> Stream[tuple[_U, ...]]:
        # Lazy
        return Stream(zip(self.__items, *iterables))

    def chain(self: Stream[_U], iterable: Iterable[_U], *iterables: Iterable[_U]) -> Stream[_U]:
        # Lazy
        return Stream(itertools.chain(self.__items, iterable, *iterables))

    @overload
    def reduce(self: Stream[_S], function: Callable[[_T, _S], _T], initial: _T, /) -> _T: ...
    @overload
    def reduce(self: Stream[_T], function: Callable[[_T, _T], _T], /) -> _T: ...
    def reduce(self, function, *args):  # type: ignore[no-untyped-def]
        """
        Apply a function of two arguments cumulatively to the items of a sequence,
        from left to right, so as to reduce the sequence to a single value.
        For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates
        ((((1+2)+3)+4)+5).  If initial is present, it is placed before the items
        of the sequence in the calculation, and serves as a default when the
        sequence is empty.
        """  # noqa: D205
        # Eager
        return functools.reduce(function, self.__items, *args)

    @overload
    def filterfalse(self: Stream[_U], predicate: None = ...) -> Stream[_U]: ...
    @overload
    def filterfalse(self: Stream[_U], predicate: Callable[[_U], Any]) -> Stream[_U]: ...
    def filterfalse(self, predicate=None):  # type: ignore[no-untyped-def]
        return Stream(itertools.filterfalse(predicate, self.__items))

    @overload
    def zip_longest(self, iter1: Iterable[_U], /) -> Stream[tuple[_T_co, _U]]: ...
    @overload
    def zip_longest(
        self, iter1: Iterable[_U], iter2: Iterable[_V], /
    ) -> Stream[tuple[_T_co, _U, _V]]: ...
    @overload
    def zip_longest(
        self, iter1: Iterable[_U], iter2: Iterable[_V], iter3: Iterable[_W], /
    ) -> Stream[tuple[_T_co, _U, _V, _W]]: ...
    def zip_longest(self: Stream[_U], *iterables: Iterable[_U]) -> Stream[tuple[_U, ...]]:
        # Lazy
        return Stream(itertools.zip_longest(self.__items, *iterables))

    @overload
    def accumulate(
        self: Stream[_U], func: None = None, *, initial: _U | None = ...
    ) -> Stream[_U]: ...
    @overload
    def accumulate(
        self: Stream[_V], func: Callable[[_U, _V], _U], *, initial: _U | None = ...
    ) -> Stream[_U]: ...
    def accumulate(self, func=None, initial=None):  # type: ignore[no-untyped-def]
        """Return series of accumulated sums (or other binary function results)."""
        # Lazy
        return Stream(itertools.accumulate(self.__items, func, initial=initial))


if __name__ == "__main__":
    s = Stream([1, 2, 3])
    _1 = s.map(lambda x: x + 1)
    _2 = s.filter()
    _3 = s.type_is(int)
    _4 = s.unique()
    _5 = s.enumerate()
    _6 = s.peek(print)
    _7 = s.map(lambda x: (x, x)).flatten()
    _8 = s.flat_map(lambda x: (x, x))
    _9 = s.islice(2)
    _10 = s.batched(2)
    _11 = s.min()
    _12 = s.max()
    _13 = s.sorted()
    _14 = s.map(str).join(",")
    _15 = s.first()
    _16 = s.find(lambda x: x == 2)  # noqa: PLR2004
    _17 = s.group_by(lambda x: x % 2 == 0)
    _18 = s.for_each(print)  # type: ignore[func-returns-value]
    _19 = s.cache()
    _20 = s.to_list()
    _21 = s.to_tuple()
    _22 = s.to_set()
    _23 = s.map(lambda x: (x, x)).to_dict()
    _24 = s.len()
    _25 = s.from_io(open("file.txt"))  # noqa: SIM115
    _26 = s.sections(lambda x: x == 2)  # noqa: PLR2004
    _27 = s.take(2)
    _28 = s.drop(2)
    _29 = s.dropwhile(lambda x: x == 1)
    _30 = s.takewhile(lambda x: x == 1)
    _31 = s.sum()
    _32 = s.zip("range(10)")
    _33 = s.chain(range(10))  # Fix this
    _34 = s.reduce(lambda x, y: x + y, 0.1)
    _35 = s.filterfalse()
    _36 = s.zip_longest("")
    _37 = s.accumulate()
