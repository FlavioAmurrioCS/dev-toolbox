from __future__ import annotations

import mmap
import os
from typing import Generator
from typing import NamedTuple

_MMAP_PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")


class FileSlice(NamedTuple):
    file_path: str
    start_offset: int
    end_offset: int

    @staticmethod
    def _align_offset(offset: int, page_size: int) -> int:
        """
        Align the given offset to the nearest page size boundary.

        This is useful for memory-mapped files, as offsets must be aligned
        to the system's page size for efficient access.

        Parameters
        ----------
        - offset (int): The original offset.
        - page_size (int): The system's memory page size.

        Returns
        -------
        - int: The aligned offset.

        """
        return (offset // page_size) * page_size

    def iter_lines(self) -> Generator[bytes]:
        """
        Iterates over lines in a file within a specified byte range.

        This method reads lines from a file using memory mapping for efficient access.
        It yields each line as a bytes object, starting from the specified `start_offset`
        and ending before the `end_offset`.

        Yields:
            bytes: A line from the file as a bytes object.

        Raises:
            ValueError: If the `start_offset` or `end_offset` is invalid or out of bounds.
            OSError: If there is an issue opening or memory-mapping the file.

        """
        offset = self._align_offset(self.start_offset, _MMAP_PAGE_SIZE)
        with open(self.file_path, "rb") as file:
            length = self.end_offset - offset
            with mmap.mmap(
                file.fileno(), length, access=mmap.ACCESS_READ, offset=offset
            ) as mmapped_file:
                mmapped_file.seek(self.start_offset - offset)
                yield from iter(mmapped_file.readline, b"")

    @staticmethod
    def from_file(file_path: str) -> FileSlice:
        """
        Creates a FileSlice object representing the entire content of a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            FileSlice: An object representing the file from the beginning to the end.

        Raises:
            OSError: If the file does not exist or cannot be accessed.

        """
        file_size_bytes = os.path.getsize(file_path)
        return FileSlice(file_path, 0, file_size_bytes)

    @staticmethod
    def split_file(file_path: str, splits: int) -> list[FileSlice]:
        r"""
        Splits a file into multiple chunks based on the specified number of splits.

        This function reads the file in binary mode and uses memory mapping to
        efficiently divide the file into chunks. Each chunk is represented as a
        `FileSlice` object, which contains the file path and the byte range
        (start and end) for that chunk. The splitting ensures that chunks end
        at newline boundaries whenever possible.

        Args:
            file_path (str): The path to the file to be split.
            splits (int): The number of chunks to split the file into.

        Returns:
            list[FileSlice]: A list of `FileSlice` objects representing the
            chunks of the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If `splits` is less than or equal to zero.

        Note:
            - If the file size is smaller than the number of splits, some chunks
              may be empty.
            - The function attempts to align chunk boundaries with newline
              characters (`\n`) to avoid splitting lines across chunks.

        """
        file_size_bytes = os.path.getsize(file_path)
        base_chunk_size = file_size_bytes // splits
        chunks: list[FileSlice] = []

        with open(file_path, "r+b") as file, mmap.mmap(
            file.fileno(), length=0, access=mmap.ACCESS_READ
        ) as mmapped_file:
            start_byte = 0
            for _ in range(splits):
                end_byte = min(start_byte + base_chunk_size, file_size_bytes)
                end_byte = mmapped_file.find(b"\n", end_byte)
                end_byte = end_byte + 1 if end_byte != -1 else file_size_bytes
                chunks.append(FileSlice(file_path, start_byte, end_byte))
                start_byte = end_byte

        return chunks
