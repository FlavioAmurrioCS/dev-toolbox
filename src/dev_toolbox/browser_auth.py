from __future__ import annotations

import logging
import sys
import webbrowser
from typing import TYPE_CHECKING
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

if TYPE_CHECKING:
    from typing import Callable
    from typing import Iterable
    from typing import Literal
    from typing import MutableMapping
    from typing import TypedDict
    from typing import TypeVar

    from _typeshed.wsgi import StartResponse
    from typing_extensions import Any
    from typing_extensions import TypeAlias

    R = TypeVar("R")

    WSGIEnvironment: TypeAlias = "dict[str, Any]"

    class SimpleRequestEvent(TypedDict):
        url: str
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]
        headers: MutableMapping[str, str]
        params: dict[str, list[str]]
        content: bytes


logger = logging.getLogger(__name__)


def _get_http_headers(environ: WSGIEnvironment) -> dict[str, str]:
    headers = {}
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            headers[key[5:].replace("_", "-")] = value
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            headers[key.replace("_", "-")] = value
    headers.pop("HOST", None)
    return headers


def create_request_event(environ: WSGIEnvironment) -> SimpleRequestEvent:
    headers = _get_http_headers(environ)
    content_length = int(headers.pop("CONTENT-LENGTH", "") or "0")
    body = environ["wsgi.input"].read(content_length)

    return {
        "method": environ["REQUEST_METHOD"],
        "url": environ["PATH_INFO"],
        "headers": headers,
        "params": parse_qs(environ["QUERY_STRING"]),
        "content": body,
    }


def browser_auth(  # noqa: PLR0913
    *,
    url: str,
    handler: Callable[[SimpleRequestEvent], R],
    port: int = 3000,
    host: str = "127.0.0.1",
    timeout: float | None = None,
    handled_msg: str = "Go back to terminal.",
) -> R:
    storage: list[R] = []

    def handler2(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        request_event = create_request_event(environ)
        response_event = handler(request_event)
        storage.append(response_event)
        start_response(
            "200 OK",
            [],
        )
        return (f"<html><body><h1>Success</h1><p>{handled_msg}</p></body></html>".encode(),)

    server = make_server(host, port, handler2)
    logger.info("Opening browser for authentication: %s", url)
    if not webbrowser.open_new_tab(url):
        print(f"Please open {url} in your browser", file=sys.stderr)

    server.timeout = timeout
    with server as httpd:
        sa = httpd.socket.getsockname()
        server_host, server_port = sa[0], sa[1]
        logger.info("Waiting for callback on http://%s:%d", server_host, server_port)
        try:
            server.handle_request()
        except KeyboardInterrupt:
            msg = "Server stopped by user"
            raise SystemExit(msg) from None

    return storage[0]


if __name__ == "__main__":
    import argparse
    import json

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Browser Auth")
    parser.add_argument(
        "--url",
        default="https://www.google.com",
        help="URL to open in the browser (default: %(default)s)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to listen on for the callback (default: %(default)s)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to listen on for the callback (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Timeout for the server (default: %(default)s)",
    )
    args = parser.parse_args()
    result = browser_auth(
        url=args.url, handler=lambda x: x, port=args.port, host=args.host, timeout=args.timeout
    )
    print(json.dumps({**result, "content": result["content"].decode("utf-8")}, indent=2))
