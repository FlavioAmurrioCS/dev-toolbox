from __future__ import annotations

import csv
import dataclasses
import json
import typing
from dataclasses import is_dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import NamedTuple
from typing import TypeVar

from dev_toolbox._types import is_list_of
from dev_toolbox._types import is_namedtuple

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

    from _typeshed import DataclassInstance
    from typing_extensions import TypeAlias

    T1 = TypeVar("T1")
    _TableRow: TypeAlias = Mapping[str, Any]
    _Table: TypeAlias = Sequence[_TableRow]

T0 = TypeVar("T0")


def asdicts(data: Sequence[object]) -> _Table:
    if not data:
        return []
    if is_list_of(data, dict):
        return data
    if is_dataclass(data[0]):
        return [dataclasses.asdict(row) for row in typing.cast("list[DataclassInstance]", data)]
    if is_namedtuple(data[0]):
        return [row._asdict() for row in typing.cast("list[NamedTuple]", data)]
    if is_list_of(data, list) or is_list_of(data, tuple):
        return [{str(i): v for i, v in enumerate(row)} for row in data]
    try:
        return [vars(x) for x in data]
    except TypeError:
        msg = "Unsupported data type"
        raise ValueError(msg) from None


def column_widths(data: _Table) -> dict[str, int]:
    if not data:
        return {}
    lengths = {key: len(key) for key in data[0]}
    for row in data:
        for key, value in row.items():
            lengths[key] = max(lengths[key], len(str(value)))
    return lengths


def markdown(data: _Table, aligner: Callable[[str, int], str] = str.ljust) -> str:
    if not data:
        return ""
    lengths = column_widths(data)
    col_names = data[0].keys()
    return "\n".join(
        (
            f"| {' | '.join(aligner(col, lengths[col]) for col in col_names)} |",
            f"| {' | '.join('-' * lengths[col] for col in col_names)} |",
            *(
                f"| {' | '.join(aligner(str(row[col]), lengths[col]) for col in col_names)} |"
                for row in data
            ),
            "\n",
        )
    )


def transpose(data: _Table) -> _Table:
    if not data:
        return []
    ret = []
    cols = list(data[0].keys())
    for col in cols:
        _cols = [row[col] for row in data]
        ret.append(_cols)
    return asdicts(ret)


def fix_col_names(data: _Table, col_names: Sequence[str]) -> _Table:
    return [dict(zip(col_names, row.values())) for row in data]


def filter_dict(data: _TableRow, keys: Sequence[str]) -> _TableRow:
    return {key: data.get(key) for key in keys}


def filter_dict_not(data: _TableRow, keys: Sequence[str]) -> _TableRow:
    return {key: val for key, val in data.items() if key not in keys}


def to_csv(data: _Table, filename: str) -> None:
    _data = asdicts(data)
    fieldnames = tuple(*(_data[0].keys() if _data else []))
    with open(filename, "w") as f:
        dict_writer = csv.DictWriter(f, fieldnames=fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(_data)


def to_json(data: _Table, filename: str) -> None:
    _data = asdicts(data)
    with open(filename, "w") as f:
        json.dump(_data, f, indent=2)
