from __future__ import annotations

import glob
import os
from contextlib import ExitStack
from typing import Callable
from typing import Generic
from typing import IO
from typing import Sequence
from typing import TYPE_CHECKING
from typing import TypeVar

from typing_extensions import LiteralString

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import Self


_LiteralStringT = TypeVar("_LiteralStringT", bound=LiteralString)
_IOT = TypeVar("_IOT", bound=IO)  # type: ignore[type-arg]


class MultiFileOpener(Generic[_LiteralStringT, _IOT]):
    """
    A context manager for opening multiple files.

    This class allows you to open multiple files at once and manage them as a context manager.
    It provides methods to access the opened files and automatically closes them when the context is exited.

    Args:
    ----
        filenames (Sequence[_LiteralStringT]): A sequence of filenames to open.
        base_dir (str, optional): The base directory to prepend to the filenames. Defaults to "".
        extension (str, optional): The file extension to append to the filenames. Defaults to "".
        opener (Callable[[str], _IOT], optional): A callable that takes a filename and returns a file object. Defaults to `open` function.

    Attributes:
    ----------
        __filenames__ (tuple[_LiteralStringT, ...]): The tuple of filenames to open.
        __extension__ (str): The file extension to append to the filenames.
        __base_dir__ (str): The base directory to prepend to the filenames.
        __opener__ (Callable[[str], _IOT]): The callable used to open the files.
        __open_files__ (dict[_LiteralStringT, _IOT]): A dictionary to store the opened files.
        __stack__ (ExitStack): An `ExitStack` object to manage the context.

    Methods:
    -------
        __enter__(): Enters the context and opens the files.
        __exit__(tp: type[BaseException] | None, inst: BaseException | None, tb: TracebackType | None) -> bool | None: Exits the context and closes all the files.
        __getitem__(key: _LiteralStringT) -> _IOT: Returns the file object associated with the given key.

    Example:
    -------
    ```python
    with MultiFileOpener(["file1", "file2"], base_dir="/path/to/files", extension=".txt") as opener:
        file1 = opener["file1"]
        file2 = opener["file2"]
        # Use the opened files
    ```

    """  # noqa: E501

    __filenames__: tuple[_LiteralStringT, ...]
    __extension__: str
    __base_dir__: str
    __opener__: Callable[[str], _IOT]
    __open_files__: dict[_LiteralStringT, _IOT]
    __stack__: ExitStack

    def __init__(
        self,
        *,
        filenames: Sequence[_LiteralStringT],
        base_dir: str = "",
        extension: str = "",
        opener: Callable[[str], _IOT] = lambda x: open(x, "w"),  # type: ignore[assignment,return-value]  # noqa: SIM115
    ) -> None:
        """
        Initialize the MultiFile object.

        Args:
        ----
            filenames (Sequence[_LiteralStringT]): A sequence of filenames.
            base_dir (str, optional): The base directory for the filenames. Defaults to "".
            extension (str, optional): The file extension to be appended to the filenames. Defaults to "".
            opener (Callable[[str], _IOT], optional): A callable that opens a file. Defaults to `open(x, "w")`.

        Returns:
        -------
            None

        """  # noqa: E501
        self.__filenames__ = tuple(filenames)
        self.__extension__ = "." + extension.lstrip(".")
        self.__base_dir__ = base_dir
        self.__opener__ = opener
        self.__open_files__ = {}

    def _file_path(self, filename: _LiteralStringT) -> str:
        """
        Returns the full file path by joining the base directory, filename, and extension.

        Args:
        ----
            filename (str): The name of the file.

        Returns:
        -------
            str: The full file path.

        """
        return os.path.join(self.__base_dir__, filename + self.__extension__)

    def __enter__(self) -> Self:
        """
        Enter method for context manager.

        Opens the specified files using the provided opener function and adds them to the stack of open files.

        Returns
        -------
            Self: The current instance of the context manager.

        """  # noqa: E501
        self.__stack__ = ExitStack().__enter__()
        try:
            for filename in self.__filenames__:
                path = self._file_path(filename)
                self.__open_files__[filename] = self.__stack__.enter_context(self.__opener__(path))  # type: ignore[assignment]
        except BaseException:
            self.__stack__.close()
            raise
        return self

    def __exit__(
        self,
        tp: type[BaseException] | None,
        inst: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        """
        Exits the context and closes all the files.

        Args:
        ----
            tp (Optional[Type[BaseException]]): The type of the exception raised, if any.
            inst (Optional[BaseException]): The exception instance raised, if any.
            tb (Optional[TracebackType]): The traceback object for the exception, if any.

        Returns:
        -------
            Optional[bool]: True if the exception was handled, False otherwise.

        """
        return self.__stack__.__exit__(tp, inst, tb)

    def __getitem__(self, key: _LiteralStringT) -> _IOT:
        """
        Retrieve the file associated with the given key.

        Args:
        ----
            key: The key used to retrieve the file.

        Returns:
        -------
            The file associated with the given key.

        """
        return self.__open_files__[key]


class MultiFileOpenerSequence(MultiFileOpener[_LiteralStringT, _IOT]):
    """
    A class for opening multiple files in sequence.

    Args:
    ----
        filenames (Sequence[_LiteralStringT]): A sequence of filenames.
        start (int, optional): The starting counter value. Defaults to 0.
        base_dir (str, optional): The base directory for the files. Defaults to "".
        extension (str, optional): The file extension. Defaults to "".
        opener (Callable[[str], _IOT], optional): A callable that opens a file. Defaults to lambda x: open(x, "w").

    Attributes:
    ----------
        __counter__ (int): The current counter value.

    Methods:
    -------
        _file_path(filename: _LiteralStringT) -> str: Returns the file path for a given filename.
        next_file() -> int: Closes the current file, increments the counter, opens the next file, and returns the new counter value.

    """  # noqa: E501

    def __init__(
        self,
        *,
        filenames: Sequence[_LiteralStringT],
        start: int | None = None,
        base_dir: str = "",
        extension: str = "",
        opener: Callable[[str], _IOT] = lambda x: open(x, "w"),  # type: ignore[assignment,return-value]  # noqa: SIM115
    ) -> None:
        """
        Initialize a MultiFile object.

        Args:
        ----
            filenames (Sequence[_LiteralStringT]): A sequence of filenames.
            start (int, optional): The starting counter value. Defaults to 0.
            base_dir (str, optional): The base directory for the filenames. Defaults to "".
            extension (str, optional): The file extension for the filenames. Defaults to "".
            opener (Callable[[str], _IOT], optional): A callable that opens a file. Defaults to lambda x: open(x, "w").

        Returns:
        -------
            None

        """  # noqa: E501
        super().__init__(filenames=filenames, base_dir=base_dir, extension=extension, opener=opener)
        if start is None:
            last_file = self.list_files(filenames[0])
            start = int(last_file[-1].split("_")[-1].split(".")[0]) + 1 if last_file else 0
        self.__counter__ = start

    def _file_path(self, filename: _LiteralStringT) -> str:
        """
        Returns the file path for a given filename.

        Args:
        ----
            filename (_LiteralStringT): The filename.

        Returns:
        -------
            str: The file path.

        """
        return os.path.join(
            self.__base_dir__, f"{filename}_{self.__counter__:05}{self.__extension__}"
        )

    def list_files(self, filename: _LiteralStringT | None = None) -> list[str]:
        """
        Returns a sorted list of file paths matching the given filename pattern.

        Args:
        ----
            filename (str, optional): The filename pattern to match. If not provided, the first filename in the list will be used. Defaults to None.

        Returns:
        -------
            list[str]: A sorted list of file paths matching the filename pattern.

        """  # noqa: E501
        results = glob.glob(
            os.path.join(
                self.__base_dir__,
                f"{filename or self.__filenames__[0]}_?????{self.__extension__}",
            )
        )
        return sorted(results)

    def next_file(self) -> int:
        """
        Closes the current file, increments the counter, opens the next file, and returns the new counter value.

        Returns
        -------
            int: The new counter value.

        """  # noqa: E501
        self.__stack__.close()
        self.__counter__ += 1
        self.__enter__()
        return self.__counter__
