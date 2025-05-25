from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import io
    from typing import Any
    from typing import Literal
    from typing import Sequence
    from typing import TypedDict

    Methods = Literal["get", "post", "put", "delete"]

    class Request(TypedDict):
        summary: str
        description: str
        operationId: str
        parameters: list[dict[str, Any]]
        requestBody: dict[str, Any] | None
        responses: dict[str, dict[str, Any]]

    class Swagger(TypedDict):
        paths: dict[str, dict[Methods, Request]]


def generate_http_client(openapi: dict, output: io.TextIOBase) -> None:
    output.write(
        """\
from __future__ import annotations
import json
import requests
from typing import Any, Dict, List, Optional, Union
"""
    )

    for path, path_data in openapi["paths"].items():
        for method, method_data in path_data.items():
            output.write("\n")
            generate_http_client_method(path, method, method_data, output)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate HTTP client code")
    parser.add_argument(
        "openapi_file",
        type=argparse.FileType("r"),
        help="OpenAPI file to generate client code from",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file to write generated code to",
    )
    args = parser.parse_args(argv)

    openapi = json.load(args.openapi_file)
    generate_http_client(openapi, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
