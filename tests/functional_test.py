from __future__ import annotations

from typing import TYPE_CHECKING

from dev_toolbox.great_value.functional import NoItem
from dev_toolbox.great_value.functional import Stream

if TYPE_CHECKING:
    from pathlib import Path


def test_initialization() -> None:
    s = Stream([1, 2, 3])
    assert list(s) == [1, 2, 3]


def test_map() -> None:
    s = Stream([1, 2, 3]).map(lambda x: x + 1)
    assert list(s) == [2, 3, 4]


def test_filter() -> None:
    s = Stream([1, 2, 3, 4]).filter(lambda x: x % 2 == 0)
    assert list(s) == [2, 4]


def test_type_is() -> None:
    s = Stream([1, "a", 2, "b"]).type_is(int)
    assert list(s) == [1, 2]


def test_unique() -> None:
    s = Stream([1, 2, 2, 3, 1]).unique()
    assert list(s) == [1, 2, 3]


def test_enumerate() -> None:
    s = Stream(["a", "b", "c"]).enumerate()
    assert list(s) == [(0, "a"), (1, "b"), (2, "c")]


def test_peek() -> None:
    result: list[int] = []
    s = Stream([1, 2, 3]).peek(result.append)
    assert list(s) == [1, 2, 3]
    assert result == [1, 2, 3]


def test_flatten() -> None:
    s = Stream([[1, 2], [3, 4]]).flatten()
    assert list(s) == [1, 2, 3, 4]


def test_flat_map() -> None:
    s = Stream([1, 2, 3]).flat_map(lambda x: [x, x])
    assert list(s) == [1, 1, 2, 2, 3, 3]


def test_islice() -> None:
    s = Stream([1, 2, 3, 4]).islice(2)
    assert list(s) == [1, 2]


def test_batched() -> None:
    s = Stream([1, 2, 3, 4]).batched(2)
    assert list(s) == [(1, 2), (3, 4)]


def test_min() -> None:
    s = Stream([3, 1, 2])
    assert s.min() == 1


def test_max() -> None:
    s = Stream([3, 1, 2])
    assert s.max() == 3  # noqa: PLR2004


def test_sorted() -> None:
    s = Stream([3, 1, 2]).sorted()
    assert list(s) == [1, 2, 3]


def test_join() -> None:
    s = Stream(["a", "b", "c"])
    assert s.join(",") == "a,b,c"


def test_first() -> None:
    s = Stream([1, 2, 3])
    assert s.first() == 1


def test_find() -> None:
    s = Stream([1, 2, 3])
    assert s.find(lambda x: x == 2) == 2  # noqa: PLR2004
    assert s.find(lambda x: x == 4) == NoItem  # noqa: PLR2004


def test_group_by() -> None:
    s = Stream([1, 2, 3, 4, 5]).group_by(lambda x: x % 2 == 0)
    assert list(s) == [(False, [1, 3, 5]), (True, [2, 4])]


def test_for_each() -> None:
    result: list[int] = []
    s = Stream([1, 2, 3])
    s.for_each(result.append)
    assert result == [1, 2, 3]


def test_cache() -> None:
    s = Stream([1, 2, 3]).cache()
    assert list(s) == [1, 2, 3]


def test_to_list() -> None:
    s = Stream([1, 2, 3])
    assert s.to_list() == [1, 2, 3]


def test_to_tuple() -> None:
    s = Stream([1, 2, 3])
    assert s.to_tuple() == (1, 2, 3)


def test_to_set() -> None:
    s = Stream([1, 2, 2, 3])
    assert s.to_set() == {1, 2, 3}


def test_to_dict() -> None:
    s = Stream([("a", 1), ("b", 2)])
    assert s.to_dict() == {"a": 1, "b": 2}


def test_len() -> None:
    s = Stream([1, 2, 3])
    assert s.len() == 3  # noqa: PLR2004


def test_sum() -> None:
    s = Stream([1, 2, 3])
    assert s.sum() == 6  # noqa: PLR2004


def test_reduce() -> None:
    s = Stream([1, 2, 3])
    assert s.reduce(lambda x, y: x + y) == 6  # noqa: PLR2004


def test_reverse() -> None:
    s = Stream([1, 2, 3]).reverse()
    assert list(s) == [3, 2, 1]


def test_from_io(tmp_path: Path) -> None:
    p = tmp_path / "test.txt"
    p.write_text("line1\nline2\nline3")
    s = Stream.from_io(open(p))  # noqa: SIM115
    assert list(s) == ["line1\n", "line2\n", "line3"]


def test_range() -> None:
    s = Stream.range(0, 3)
    assert list(s) == [0, 1, 2]


def test_sections() -> None:
    s = Stream([1, 2, 3, 4, 1, 2, 3, 4]).sections(lambda x: x == 1)
    assert list(s) == [(1, 2, 3, 4), (1, 2, 3, 4)]


def test_take() -> None:
    s = Stream([1, 2, 3, 4]).take(2)
    assert list(s) == [1, 2]


def test_drop() -> None:
    s = Stream([1, 2, 3, 4]).drop(2)
    assert list(s) == [3, 4]


def test_dropwhile() -> None:
    s = Stream([1, 2, 3, 4]).dropwhile(lambda x: x < 3)  # noqa: PLR2004
    assert list(s) == [3, 4]


def test_takewhile() -> None:
    s = Stream([1, 2, 3, 4]).takewhile(lambda x: x < 3)  # noqa: PLR2004
    assert list(s) == [1, 2]


def test_zip() -> None:
    s = Stream([1, 2, 3]).zip([4, 5, 6])
    assert list(s) == [(1, 4), (2, 5), (3, 6)]


def test_chain() -> None:
    s = Stream([1, 2, 3]).chain([4, 5, 6])
    assert list(s) == [1, 2, 3, 4, 5, 6]


def test_filterfalse() -> None:
    s = Stream([1, 2, 3, 4]).filterfalse(lambda x: x % 2 == 0)
    assert list(s) == [1, 3]


def test_zip_longest() -> None:
    s = Stream([1, 2, 3]).zip_longest([4, 5])
    assert list(s) == [(1, 4), (2, 5), (3, None)]


def test_accumulate() -> None:
    s = Stream([1, 2, 3]).accumulate()
    assert list(s) == [1, 3, 6]


def test_typing_cast() -> None:
    s = Stream([1, 2, 3]).typing_cast(str)
    assert list(s) == [1, 2, 3]


def test_collect() -> None:
    s = Stream([1, 2, 3])
    assert s.collect(sum) == 6  # noqa: PLR2004
