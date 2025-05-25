from __future__ import annotations

import json
import urllib.parse
from typing import TYPE_CHECKING
from typing import NamedTuple

if TYPE_CHECKING:
    from http.client import HTTPResponse

    from _typeshed import Incomplete
    from typing_extensions import Unpack

    from dev_toolbox.http._types import _CompleteRequestArgs
    from dev_toolbox.http._types import _Params


class GreatValueResponse(NamedTuple):
    response: HTTPResponse

    def json(self) -> Incomplete:
        content = self.response.read()
        return json.loads(content)

    def raise_for_status(self) -> None:
        status_code = self.response.status
        http_error_msg = ""
        if 400 <= status_code < 500:  # noqa: PLR2004
            http_error_msg = (
                f"{status_code} Client Error: {self.response.reason} for url: {self.response.url}"
            )

        elif 500 <= status_code < 600:  # noqa: PLR2004
            http_error_msg = (
                f"{status_code} Server Error: {self.response.reason} for url: {self.response.url}"
            )

        if http_error_msg:
            raise Exception(http_error_msg)  # noqa: TRY002


class GreatValueRequests(NamedTuple):
    base_url: str | None = None
    unverifiable: bool = True
    headers: dict[str, str] | None = None

    def construct_url(self, base_url: str | None, endpoint: str, params: _Params) -> str:
        if base_url is not None and not endpoint.startswith("http"):
            endpoint = urllib.parse.urljoin(base_url, endpoint)
        if params is not None:
            encoded = urllib.parse.urlencode(params)
            endpoint += "?" + encoded
        return endpoint

    def request(self, **kwargs: Unpack[_CompleteRequestArgs]) -> GreatValueResponse:
        url = kwargs["url"]
        method = kwargs["method"]
        final_url = self.construct_url(self.base_url, url, kwargs.get("params"))
        import urllib.request

        headers = {
            k.upper(): v
            for k, v in (*(self.headers or {}).items(), *(kwargs.get("headers") or {}).items())
        }

        if kwargs.get("data") and kwargs.get("json"):
            msg = "Cannot set both 'data' and 'json'"
            raise ValueError(msg)

        data = kwargs.get("data")

        json_content = kwargs.get("json")
        if json_content is not None:
            if "CONTENT-TYPE" not in headers:
                headers["CONTENT-TYPE"] = "application/json"
            data = json.dumps(json_content).encode("utf-8")  # type: ignore[assignment]

        req = urllib.request.Request(  # noqa: S310
            url=final_url,
            data=None,
            headers=headers,
            # origin_req_host=None,
            unverifiable=self.unverifiable,
            method=method,
        )
        response: HTTPResponse = urllib.request.urlopen(  # noqa: S310
            url=req,
            data=data,  # type: ignore[arg-type]
            timeout=kwargs.get("timeout"),
            # cafile=None,
            # capath=None,
            # cadefault=False,
            # context=None,
        )

        return GreatValueResponse(response=response)


gv_request = GreatValueRequests()
