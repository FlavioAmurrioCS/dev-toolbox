from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from dev_toolbox._types import JSON_TYPE


class AttrDict(dict):  # type:ignore[type-arg]
    """
    Dict like object that supports attribute style dotted access.
    This class is intended for use with the *object_hook* in json.loads():
        >>> from json import loads, AttrDict
        >>> json_string = '{"mercury": 88, "venus": 225, "earth": 365, "mars": 687}'
        >>> orbital_period = loads(json_string, object_hook=AttrDict)
        >>> orbital_period["earth"]  # Dict style lookup
        365
        >>> orbital_period.earth  # Attribute style lookup
        365
        >>> orbital_period.keys()  # All dict methods are present
        dict_keys(['mercury', 'venus', 'earth', 'mars'])
    Attribute style access only works for keys that are valid attribute names.
    In contrast, dictionary style access works for all keys.
    For example, ``d.two words`` contains a space and is not syntactically
    valid Python, so ``d["two words"]`` should be used instead.
    If a key has the same name as dictionary method, then a dictionary
    lookup finds the key and an attribute lookup finds the method:
        >>> d = AttrDict(items=50)
        >>> d["items"]  # Lookup the key
        50
        >>> d.items()  # Call the method
        dict_items([('items', 50)]).
    """  # noqa: D205

    __slots__ = ()

    def __getattr__(self, attr: str) -> JSON_TYPE:
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr) from None

    def __setattr__(self, attr: str, value: JSON_TYPE) -> None:
        self[attr] = value

    def __delattr__(self, attr: str) -> None:
        try:
            del self[attr]
        except KeyError:
            raise AttributeError(attr) from None

    def __dir__(self) -> list[Any]:
        return list(self) + dir(type(self))
