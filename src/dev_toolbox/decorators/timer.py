from __future__ import annotations

import functools
import time
from typing import Callable
from typing import Generic
from typing import NamedTuple
from typing import TypeVar

from typing_extensions import ParamSpec

_P = ParamSpec("_P")
_R = TypeVar("_R")


class _Timer(Generic[_P, _R]):
    """
    A decorator class that measures the execution time of a function.

    Args:
    ----
        func (Callable[_P, _R]): The function to be timed.

    Attributes:
    ----------
        __wrapped__ (Callable[_P, _R]): The wrapped function.
        __times__ (list[float]): A list to store the execution times of the function.

    """

    __wrapped__: Callable[_P, _R]
    __times__: list[float]

    class _TimerStats(NamedTuple):
        funcname: str
        average: float
        median: float
        min: float  # noqa: A003
        max: float  # noqa: A003
        total: float

    def __init__(self, func: Callable[_P, _R]) -> None:
        self.__wrapped__ = func
        self.__times__ = []
        functools.update_wrapper(self, func)

    def stats(self) -> _Timer._TimerStats:
        """
        Calculate and return statistics about the timer.

        Returns
        -------
            _TimerStats: An object containing various statistics about the timer, including the
            function name, average time, median time, minimum time, maximum time, and total time.
        """
        sorted_data = sorted(self.__times__)
        return _Timer._TimerStats(
            funcname=self.__wrapped__.__qualname__,
            average=sum(self.__times__) / len(self.__times__),
            median=sorted_data[len(sorted_data) // 2],
            min=sorted_data[0],
            max=sorted_data[-1],
            total=sum(self.__times__),
        )

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        start = time.perf_counter_ns()
        ret = self.__wrapped__(*args, **kwargs)
        duration = time.perf_counter_ns() - start
        self.__times__.append(duration)
        return ret


def timer() -> Callable[[Callable[_P, _R]], _Timer[_P, _R]]:
    def _inner_timer(func: Callable[_P, _R]) -> _Timer[_P, _R]:
        return _Timer(func)

    return _inner_timer
