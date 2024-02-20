from __future__ import annotations

from typing import Dict
from typing import List
from typing import TYPE_CHECKING
from typing import Union


if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    JSON_TYPE: TypeAlias = Union[
        str, int, float, bool, None, List["JSON_TYPE"], Dict[str, "JSON_TYPE"]
    ]
