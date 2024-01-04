from __future__ import annotations

try:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)
except (ImportError, LookupError):
    try:
        from dev_toolbox._version import (  # noqa: F401
            __version__,  #
        )
    except ModuleNotFoundError:
        msg = "dev-toolbox is not correctly installed. Please install it with pip."
        raise RuntimeError(msg)  # noqa: B904, TRY200
