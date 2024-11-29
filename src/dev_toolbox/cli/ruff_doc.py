from __future__ import annotations

import itertools
import os
from typing import Sequence

from dev_toolbox.cli.html_table import get_column_widths
from dev_toolbox.cli.html_table import TablesParser
from dev_toolbox.http import RequestTemplate
from dev_toolbox.http.great_value import gv_request


RUFF_URL = "https://docs.astral.sh/ruff/rules/"
_FILE_CACHE = "/tmp/ruff_rules.html"  # noqa: S108


ruff_rules_template = RequestTemplate(
    url=RUFF_URL,
    method="GET",
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",  # noqa: E501
        "Host": "docs.astral.sh",
    },
)


def _get_rules_html() -> str:
    if not os.path.exists(_FILE_CACHE):
        with ruff_rules_template.request(gv_request).response as response, open(
            _FILE_CACHE, "wb"
        ) as f:
            f.write(response.read())

    with open(_FILE_CACHE) as f:
        return f.read()


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Get Ruff rules from HTML.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--code", default=None, help="Code to search for.")
    args = parser.parse_args(args=argv)
    tables = TablesParser.parse_tables(_get_rules_html())
    if not args.code:
        table = list(itertools.chain.from_iterable(tables))
        code_len, name_len, *_ = get_column_widths(table)
        for code, name, msg, _last in table:
            print(f"{code.ljust(code_len)} | {name.ljust(name_len)} | {msg}")
        return 0
    for table in tables:
        for code, name, msg, _last in table:
            if args.code == code:
                print(f"Code:    {code}")
                print(f"Name:    {name}")
                print(f"Message: {msg}")
                print(f"URL:     {RUFF_URL}{name}")
                return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
