# from __future__ import annotations
# import json
# import pickle
# import sys
# import unittest
# import pytest
# from dev_toolbox.attrdict import AttrDict
# kepler_dict = {
#     "orbital_period": {
#         "mercury": 88,
#         "venus": 225,
#         "earth": 365,
#         "mars": 687,
#         "jupiter": 4331,
#         "saturn": 10_756,
#         "uranus": 30_687,
#         "neptune": 60_190,
#     },
#     "dist_from_sun": {
#         "mercury": 58,
#         "venus": 108,
#         "earth": 150,
#         "mars": 228,
#         "jupiter": 778,
#         "saturn": 1_400,
#         "uranus": 2_900,
#         "neptune": 4_500,
#     },
# }
# class PyTest(unittest.TestCase):
#     json = json
#     loads = staticmethod(json.loads)
#     dumps = staticmethod(json.dumps)
#     AttrDict = AttrDict
#     JSONDecodeError = staticmethod(json.JSONDecodeError)
# class TestAttrDict(PyTest):
#     def test_dict_subclass(self) -> None:
#         assert issubclass(self.AttrDict, dict)
#     def test_slots(self) -> None:
#         d = self.AttrDict(x=1, y=2)
#         with pytest.raises(TypeError):
#             vars(d)
#     def test_constructor_signatures(self) -> None:
#         AttrDict = self.AttrDict
#         target = {"x": 1, "y": 2}
#         assert AttrDict(x=1, y=2) == target  # kwargs
#         assert AttrDict({"x": 1, "y": 2}) == target  # mapping
#         assert AttrDict({"x": 1, "y": 0}, y=2) == target  # mapping, kwargs
#         assert AttrDict([("x", 1), ("y", 2)]) == target  # iterable
#         assert AttrDict([("x", 1), ("y", 0)], y=2) == target  # iterable, kwargs
#     def test_getattr(self) -> None:
#         d = self.AttrDict(x=1, y=2)
#         assert d.x == 1
#         with pytest.raises(AttributeError):
#             d.z
#     def test_setattr(self) -> None:
#         d = self.AttrDict(x=1, y=2)
#         d.x = 3
#         d.z = 5
#         assert d == {"x": 3, "y": 2, "z": 5}
#     def test_delattr(self) -> None:
#         d = self.AttrDict(x=1, y=2)
#         del d.x
#         assert d == {"y": 2}
#         with pytest.raises(AttributeError):
#             del d.z
#     def test_dir(self) -> None:
#         d = self.AttrDict(x=1, y=2)
#         assert set(dir(d)), set(dir(dict)).union({"x", "y"})
#     def test_repr(self) -> None:
#         # This repr is doesn't round-trip.  It matches a regular dict.
#         # That seems to be the norm for AttrDict recipes being used
#         # in the wild.  Also it supports the design concept that an
#         # AttrDict is just like a regular dict but has optional
#         # attribute style lookup.
#         assert repr(self.AttrDict(x=1, y=2)) == repr({"x": 1, "y": 2})
#     def test_overlapping_keys_and_methods(self) -> None:
#         d = self.AttrDict(items=50)
#         assert d["items"] == 50
#         assert d.items() == dict(d).items()
#     def test_invalid_attribute_names(self) -> None:
#         d = self.AttrDict(
#             {
#                 "control": "normal case",
#                 "class": "keyword",
#                 "two words": "contains space",
#                 "hypen-ate": "contains a hyphen",
#             }
#         )
#         assert d.control == dict(d)["control"]
#         assert d["class"] == dict(d)["class"]
#         assert d["two words"] == dict(d)["two words"]
#         assert d["hypen-ate"] == dict(d)["hypen-ate"]
#     def test_object_hook_use_case(self) -> None:
#         AttrDict = self.AttrDict
#         json_string = self.dumps(kepler_dict)
#         kepler_ad = self.loads(json_string, object_hook=AttrDict)
#         assert kepler_ad == kepler_dict  # Match regular dict
#         assert isinstance(kepler_ad, AttrDict)  # Verify conversion
#         assert isinstance(kepler_ad.orbital_period, AttrDict)  # Nested
#         # Exercise dotted lookups
#         assert kepler_ad.orbital_period == kepler_dict["orbital_period"]
#         assert kepler_ad.orbital_period.earth == kepler_dict["orbital_period"]["earth"]
#         assert kepler_ad["orbital_period"].earth == kepler_dict["orbital_period"]["earth"]
#         # Dict style error handling and Attribute style error handling
#         with pytest.raises(KeyError):
#             kepler_ad.orbital_period["pluto"]
#         with pytest.raises(AttributeError):
#             kepler_ad.orbital_period.Pluto
#         # Order preservation
#         assert list(kepler_ad.items()) == list(kepler_dict.items())
#         assert list(kepler_ad.orbital_period.items()) == list(kepler_dict["orbital_period"].items())  # noqa: E501
#         # Round trip
#         assert self.dumps(kepler_ad) == json_string
#     def test_pickle(self) -> None:
#         AttrDict = self.AttrDict
#         json_string = self.dumps(kepler_dict)
#         kepler_ad = self.loads(json_string, object_hook=AttrDict)
#         # Pickling requires the cached module to be the real module
#         cached_module = sys.modules.get("json")
#         sys.modules["json"] = self.json
#         try:
#             for protocol in range(6):
#                 kepler_ad2 = pickle.loads(pickle.dumps(kepler_ad, protocol))
#                 assert kepler_ad2 == kepler_ad
#                 assert type(kepler_ad2) == AttrDict
#         finally:
#             sys.modules["json"] = cached_module
# if __name__ == "__main__":
#     unittest.main()
from __future__ import annotations
