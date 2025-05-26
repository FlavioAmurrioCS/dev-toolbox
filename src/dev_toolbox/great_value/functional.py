from __future__ import annotations

import functools
import itertools
from collections import defaultdict
from collections.abc import Sized
from itertools import islice
from typing import TYPE_CHECKING
from typing import Generic
from typing import Iterable
from typing import TypeVar
from typing import overload

if TYPE_CHECKING:
    from typing import Any
    from typing import BinaryIO
    from typing import Callable
    from typing import Generator
    from typing import Hashable
    from typing import Iterator
    from typing import TextIO

    from _typeshed import SupportsRichComparison
    from _typeshed import SupportsRichComparisonT
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
        """
        Apply a function to each item in the stream and return a new stream.

        Args:
        ----
            func (Callable): The function to apply to each item in the stream.

        Returns:
        -------
            Stream: A new stream containing the results of applying the function to each item.

        """
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
        """
        Filters the items in the stream based on the given predicate.

        Args:
        ----
            predicate (callable): A function that takes an item from the stream as input and returns
            a boolean value indicating whether the item should be included in the filtered stream.
            If no predicate is provided, all items will be included.

        Returns:
        -------
            Stream: A new stream containing only the items that satisfy the predicate.

        """
        # Lazy
        return Stream(filter(predicate, self.__items))

    def type_is(self: Stream[_U], cls: type[_V]) -> Stream[_V]:
        """
        Filters the stream to include only items that are instances of the specified class.

        Parameters
        ----------
            cls (type[_V]): The class to filter by.

        Returns
        -------
            Stream[_V]: A new stream containing only items that are instances of the specified class.

        """  # noqa: E501
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
        """
        Returns a new Stream object containing only the unique elements from the original Stream.

        Parameters
        ----------
            key (function, optional): A function that takes an element from the Stream and returns
            a value to compare for uniqueness. If not provided, the elements themselves will be
            compared.

        Returns
        -------
            Stream: A new Stream object containing only the unique elements.

        """
        # Lazy
        return Stream(self.__unique_helper(items=self.__items, key=(key or (lambda x: x))))

    def enumerate(self, start: int = 0) -> Stream[tuple[int, _T_co]]:
        """
        Lazily enumerates the items in the stream.

        Args:
        ----
            start (int, optional): The starting index for enumeration. Defaults to 0.

        Returns:
        -------
            Stream[tuple[int, _T_co]]: A stream of tuples containing the index and item.

        """
        # Lazy
        return Stream(enumerate(self.__items, start=start))

    def peek(self: Stream[_U], func: Callable[[_U], Any]) -> Stream[_U]:
        """
        Apply a function to each item in the stream, while keeping the original item unchanged.

        Args:
        ----
            self (Stream[_U]): The stream object.
            func (Callable[[_U], Any]): The function to apply to each item.

        Returns:
        -------
            Stream[_U]: A new stream object with the same items as the original stream.

        """

        # Lazy
        def func_and_return(item: _U) -> _U:
            func(item)
            return item

        return Stream(func_and_return(x) for x in self.__items)

    def flatten(self: Stream[Iterable[_U]]) -> Stream[_U]:
        """
        Flattens a stream of iterables into a single stream.

        Returns
        -------
            Stream[_U]: A new stream containing all the elements from the original stream's
            iterables.

        """
        # Lazy
        return Stream(item for sub in self.__items for item in sub)

    def flat_map(self, func: Callable[[_T_co], Iterable[_U]]) -> Stream[_U]:
        """
        Applies the given function to each element in the stream and flattens the result.

        Args:
        ----
            func (Callable[[_T_co], Iterable[_U]]): A function that takes an element of type _T_co
            and returns an iterable of type _U.

        Returns:
        -------
            Stream[_U]: A new stream containing the flattened result of applying the function to
            each element.

        """
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
        """
        Return an iterator whose next() method returns selected values from an iterable.

        If start is specified, will skip all preceding elements;
        otherwise, start defaults to zero. Step defaults to one. If
        specified as another value, step determines how many values are
        skipped between successive calls. Works like a slice() on a list
        but returns an iterator.
        """
        # Lazy
        return Stream(islice(self.__items, *args))

    def batched(self, size: int) -> Stream[tuple[_T_co, ...]]:
        """
        Returns a stream of batches, where each batch contains 'size' number of items from the original stream.

        Parameters
        ----------
            size (int): The number of items in each batch.

        Returns
        -------
            Stream[tuple[_T_co, ...]]: A stream of batches, where each batch is a tuple of 'size' number of items.

        """  # noqa: E501
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
        """
        Returns the minimum value from the items in the object.

        Args:
        ----
            key: A function that serves as a key for the comparison. Defaults to None.
            **kwargs: Additional keyword arguments to be passed to the `min` function.

        Returns:
        -------
            The minimum value from the items in the object.

        """
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
        """
        Return the maximum value in the collection.

        Args:
        ----
            key (callable, optional): A function to serve as the key for comparison. Defaults to None.
            **kwargs: Additional keyword arguments to be passed to the max function.

        Returns:
        -------
            The maximum value in the collection.

        Raises:
        ------
            TypeError: If the collection is empty and no default value is provided.

        """  # noqa: E501
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
        """
        Returns a new Stream containing the items of the current Stream, sorted in ascending order.

        Parameters
        ----------
        - key: A function that will be used to extract a comparison key from each item. Defaults to None.
        - reverse: A boolean value indicating whether the items should be sorted in descending order. Defaults to False.

        Returns
        -------
        - A new Stream containing the sorted items.

        """  # noqa: E501
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
        """
        Returns the first item in the collection.

        Parameters
        ----------
            *args: Optional arguments to be passed to the `next` function.

        Returns
        -------
            The first item in the collection.

        Raises
        ------
            StopIteration: If the collection is empty and no default value is provided.

        """
        # Eager
        return next(iter(self.__items), *args)

    # endregion: Built-in methods

    # region: Custom methods
    def find(self, func: Callable[[_T_co], object]) -> _T_co | type[NoItem]:
        """
        Find the first item in the collection that satisfies the given function.

        Parameters
        ----------
            func (Callable): A function that takes an item from the collection as input and returns a boolean value.

        Returns
        -------
            The first item in the collection that satisfies the given function, or `NoItem` if no item is found.

        """  # noqa: E501
        # Eager
        return next((item for item in self.__items if func(item)), NoItem)

    def group_by(
        self, key: Callable[[_T_co], _HashableT]
    ) -> Stream[tuple[_HashableT, list[_T_co]]]:
        """
        Groups the items in the stream by the given key function.

        Args:
        ----
            key: A callable that takes an item from the stream and returns a hashable key.

        Returns:
        -------
            A Stream of tuples, where each tuple contains a key and a list of items that have that key.

        Example:
        -------
            stream = Stream([1, 2, 3, 4, 5])
            result = stream.group_by(lambda x: x % 2 == 0)
            for key, items in result:
                print(key, items)
            Output:
            True [2, 4]
            False [1, 3, 5].

        """  # noqa: E501
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
        """
        Returns a cached version of the stream.

        Returns
        -------
            Stream: A new Stream object containing the items from the original stream.

        """
        # Eager
        return Stream(tuple(self.__items))

    # endregion: Custom methods

    # region: Collectors
    def to_list(self) -> list[_T_co]:
        """
        Convert the items in the object to a list.

        Returns
        -------
            list[_T_co]: A list containing the items in the object.

        """
        # Eager
        return list(self.__items)

    def to_tuple(self) -> tuple[_T_co, ...]:
        """
        Converts the items in the object to a tuple.

        Returns
        -------
            tuple: A tuple containing the items in the object.

        """
        # Eager
        return tuple(self.__items)

    def to_set(self) -> set[_T_co]:
        """
        Convert the items in the object to a set.

        Returns
        -------
            set[_T_co]: A set containing the items in the object.

        """
        # Eager
        return set(self.__items)

    def to_dict(self: Stream[tuple[_HashableT, _V]]) -> dict[_HashableT, _V]:
        """
        Converts the stream of tuples into a dictionary.

        Returns
        -------
            dict[_HashableT, _V]: The resulting dictionary.

        """
        # Eager
        return dict(self.__items)

    # endregion: Collectors

    def len(self) -> int:
        """
        Returns the length of the object.

        :return: The length of the object.
        :rtype: int
        """
        # Eager
        return len(self)

    def __len__(self) -> int:
        """
        Returns the length of the object.

        Note: This method may fail if `self.__items` is a generator. In that case, you should call
        the `cache` method first and then call `len` on the stream.

        Returns
        -------
            int: The length of the object.

        """
        return len(self.__items)  # type: ignore[arg-type]

    ############################################################################
    # endregion: Eager methods
    ############################################################################

    def __iter__(self) -> Iterator[_T_co]:
        """
        Returns an iterator over the items in the object.

        :return: An iterator over the items.
        :rtype: Iterator[_T_co]
        """
        # Lazy
        return iter(self.__items)

    def __repr__(self) -> str:
        """
        Return a string representation of the object.

        Returns
        -------
            str: The string representation of the object.

        """
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
        """
        Returns a Stream of tuples, where each tuple represents a section of consecutive elements from the original Stream
        that satisfy the given predicate.

        Parameters
        ----------
            predicate (Callable[[_T_co], object]): A function that takes an element from the Stream and returns a boolean
                value indicating whether the element satisfies the condition.

        Returns
        -------
            Stream[tuple[_T_co, ...]]: A Stream of tuples, where each tuple represents a section of consecutive elements
                from the original Stream that satisfy the given predicate.

        """  # noqa: E501
        # Lazy
        return Stream(self.__sections_helper(self.__items, predicate))

    def take(self, n: int) -> Stream[_T_co]:
        """
        Returns a new Stream containing the first `n` elements of the current Stream.

        Parameters
        ----------
            n (int): The number of elements to take from the Stream.

        Returns
        -------
            Stream[_T_co]: A new Stream containing the first `n` elements.

        """
        # Lazy
        return Stream(itertools.islice(self.__items, n))

    def drop(self, n: int) -> Stream[_T_co]:
        """
        Drops the first `n` elements from the stream and returns a new stream.

        Parameters
        ----------
        - n: An integer representing the number of elements to drop from the stream.

        Returns
        -------
        - Stream[_T_co]: A new stream containing the remaining elements after dropping `n` elements.

        """
        # Lazy
        return Stream(itertools.islice(self.__items, n, None))

    def dropwhile(self, predicate: Callable[[_T_co], object]) -> Stream[_T_co]:
        """
        Lazily drops elements from the stream while the predicate is true.

        Args:
        ----
            predicate: A callable that takes an element from the stream as input and returns a boolean value.

        Returns:
        -------
            A new Stream object containing the remaining elements after the predicate becomes false.

        """  # noqa: E501
        # Lazy
        return Stream(itertools.dropwhile(predicate, self.__items))

    def takewhile(self, predicate: Callable[[_T_co], object]) -> Stream[_T_co]:
        """
        Returns a new Stream containing elements from the original Stream that satisfy the given predicate function.

        Parameters
        ----------
            predicate (Callable[[_T_co], object]): A function that takes an element of the Stream
                as input and returns a boolean value indicating whether the element should be included
                in the new Stream.

        Returns
        -------
            Stream[_T_co]: A new Stream containing elements from the original Stream that satisfy
                the given predicate function.

        """  # noqa: E501
        # Lazy
        return Stream(itertools.takewhile(predicate, self.__items))

    @overload
    def sum(self: Stream[int], start: int = 0) -> int: ...
    @overload
    def sum(self: Stream[float], start: int = 0) -> float: ...
    def sum(self: Stream[int | float], start: int = 0) -> int | float:
        """
        Calculate the sum of the elements in the stream.

        Args:
        ----
            self (Stream[int | float]): The stream of elements.
            start (int, optional): The starting value for the sum. Defaults to 0.

        Returns:
        -------
            int | float: The sum of the elements in the stream.

        """
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
        """
        Lazily zips the elements of the stream with the corresponding elements from the given iterables.

        Args:
        ----
            self (Stream[_U]): The stream object.
            *iterables (Iterable[_U]): The iterables to zip with the stream.

        Returns:
        -------
            Stream[tuple[_U, ...]]: A new stream containing tuples of the zipped elements.

        """  # noqa: E501
        # Lazy
        return Stream(zip(self.__items, *iterables))

    def chain(self: Stream[_U], iterable: Iterable[_U], *iterables: Iterable[_U]) -> Stream[_U]:
        """
        Chains the items of the current stream with the items from the given iterable(s).

        Args:
        ----
            iterable (Iterable[_U]): The iterable to chain with the current stream.
            *iterables (Iterable[_U]): Additional iterables to chain with the current stream.

        Returns:
        -------
            Stream[_U]: A new stream containing the chained items.

        """
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
        """
        # Eager
        return functools.reduce(function, self.__items, *args)

    @overload
    def filterfalse(self: Stream[_U], predicate: None = ...) -> Stream[_U]: ...
    @overload
    def filterfalse(self: Stream[_U], predicate: Callable[[_U], Any]) -> Stream[_U]: ...
    def filterfalse(self, predicate=None):  # type: ignore[no-untyped-def]
        """
        Return a new Stream object containing the elements from the original stream
        for which the predicate function returns False.

        Args:
        ----
            predicate (Callable): A function that takes an item from the stream as
                input and returns a boolean value indicating whether the item should
                be included in the new stream. If no predicate is provided, all items
                will be included in the new stream.

        Returns:
        -------
            Stream: A new Stream object containing the elements from the original
            stream for which the predicate function returns False.

        """
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
        """
        Returns a new Stream object that iterates over tuples containing elements from the input iterables.
        The iteration stops when the longest input iterable is exhausted.

        Parameters
        ----------
            self (Stream[_U]): The Stream object.
            *iterables (Iterable[_U]): The input iterables to be zipped.

        Returns
        -------
            Stream[tuple[_U, ...]]: A new Stream object that iterates over tuples containing elements from the input iterables.

        """  # noqa: E501
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

    def typing_cast(self, _: type[_U], /) -> Stream[_U]:
        """
        Casts the items in the stream to the specified type.

        Parameters
        ----------
            _: The type to cast the items to.

        Returns
        -------
            Stream[_U]: A new stream with the items casted to the specified type.

        """
        return Stream(self.__items)  # type: ignore[arg-type]

    def collect(self, func: Callable[[Iterable[_T_co]], _R]) -> _R:
        """
        Collects the items in the collection and applies the given function to them.

        Args:
        ----
            func (Callable[[Iterable[_T_co]], _R]): The function to apply to the items.

        Returns:
        -------
            _R: The result of applying the function to the items.

        """
        return func(self.__items)

    @staticmethod
    def range(start: int, stop: int, step: int = 1) -> Stream[int]:
        """
        Generate a stream of integers within a specified range.

        Args:
        ----
            start (int): The starting value of the range.
            stop (int): The ending value of the range (exclusive).
            step (int, optional): The step size between values (default is 1).

        Returns:
        -------
            Stream[int]: A stream of integers within the specified range.

        """
        return Stream(range(start, stop, step))

    def reverse(self) -> Stream[_T_co]:
        """
        Reverses the order of the items in the stream.

        Returns
        -------
            Stream: A new stream with the items in reverse order.

        """
        if hasattr(self.__items, "__reversed__") or (
            hasattr(self.__items, "__len__") and hasattr(self.__items, "__getitem__")
        ):
            return Stream(reversed(self.__items))  # type: ignore[call-overload]
        return Stream(reversed(tuple(self.__items)))

    @staticmethod
    def __subprocess_run(
        cmd: tuple[str, ...], pipe_in: Iterable[str] | None = None
    ) -> Generator[str, None, None]:
        import subprocess

        process = subprocess.Popen(
            args=cmd,
            stdin=subprocess.PIPE if pipe_in else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="ignore",
            universal_newlines=True,
        )
        with process:
            if pipe_in and process.stdin:
                with process.stdin as stdin:
                    for line in pipe_in:
                        stdin.write(line)
            if process.stdout is None:
                return
            with process.stdout as stdout:
                yield from iter(stdout.readline, "")

    @staticmethod
    def subprocess_run(command: tuple[str, ...]) -> Stream[str]:
        """
        Executes the given command using the `subprocess.run` function and returns a `Stream` object.

        Args:
        ----
            command (tuple[str, ...]): The command to be executed as a tuple of strings.

        Returns:
        -------
            Stream[str]: A `Stream` object that represents the output of the command.

        """  # noqa: E501
        return Stream(Stream.__subprocess_run(command))

    def pipe(self: Stream[str], command: tuple[str, ...]) -> Stream[str]:
        """
        Executes a command using subprocess and pipes the input from the current stream.

        Args:
        ----
            command (tuple[str, ...]): The command to be executed.

        Returns:
        -------
            Stream[str]: A new stream containing the output of the command.

        """
        return Stream(self.__subprocess_run(command, pipe_in=self.__items))


if __name__ == "__main__":

    def test() -> None:
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

    def main() -> None:
        Stream.subprocess_run(("seq", "10000")).pipe(("grep", "--color=always", "10")).for_each(
            lambda x: print(x, end="")
        )
        # for i in Stream.range(0, 10).map(lambda x: x).reverse():
        #     print(i)

    # main()
