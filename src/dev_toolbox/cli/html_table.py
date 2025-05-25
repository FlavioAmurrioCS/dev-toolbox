from __future__ import annotations

from html.parser import HTMLParser
from typing import TYPE_CHECKING
from typing import List
from typing import Sequence

if TYPE_CHECKING:
    from typing_extensions import TypeAlias  # pyright: ignore[reportShadowedImports]

    Row: TypeAlias = Sequence[str]
    Table: TypeAlias = List[Row]


class TablesParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[Table] = []
        self._table: Table = []
        self._row: list[str] = []
        self._cell: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: ARG002
        if tag == "table":
            self._table = []
        elif tag == "tr":
            self._row = []
        elif tag == "td":
            self._cell = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            self.tables.append(self._table)
        elif tag == "tr":
            self._table.append(self._row)
        elif tag == "td":
            self._row.append(self._cell)  # type: ignore

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell += data

    @classmethod
    def parse_tables(cls, html_txt: str) -> list[Table]:
        parser = cls()
        parser.feed(html_txt)
        return [
            [[e.strip() for e in row] for row in table if row] for table in parser.tables if table
        ]


def get_column_widths(table: Sequence[Sequence[str]]) -> list[int]:
    return [max(len(row[i]) for row in table) for i in range(len(table[0]))]


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse all tables in an HTML file and print.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--file", type=str, default="/dev/stdin", help="HTML file to parse.")
    parser.add_argument("--json", action="store_true", help="Output as JSON.")
    args = parser.parse_args(args=argv)
    with open(args.file) as file:
        tables = TablesParser.parse_tables(file.read())
    if args.json:
        import json

        print(json.dumps(tables, indent=2))
        return 0
    for table in tables:
        lengths = get_column_widths(table)
        sum_lengths = sum(lengths) + len(lengths) * 3 - 1
        print("┍" + ("-" * sum_lengths) + "┑")
        for row in table:
            display_txt = " | ".join(cell.ljust(length) for cell, length in zip(row, lengths))
            print(f"| {display_txt} |")
        print("┕" + ("-" * sum_lengths) + "┙")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
