from __future__ import annotations

from inspect import isawaitable
from typing import cast
from typing import overload
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any
    from typing import Awaitable
    from typing import Mapping
    from typing import Union
    from _typeshed import Incomplete
    from typing import IO
    from typing import Optional
    from typing import Tuple
    from typing import TypeVar
    from typing_extensions import Literal
    from typing_extensions import TypedDict
    from typing_extensions import Protocol
    from typing_extensions import Unpack

    FileContent = Union[IO[bytes], bytes, str]
    _FileSpec = Union[
        FileContent,
        Tuple[Optional[str], FileContent],
    ]

    class _OptionalRequestsArgs(TypedDict, total=False):
        auth: tuple[str, str] | None
        cookies: dict[str, str] | None
        data: Mapping[str, Any] | None
        files: Mapping[str, _FileSpec]
        headers: Mapping[str, Any] | None
        json: Any | None
        params: dict[str, Any] | tuple[tuple[str, Any], ...] | list[tuple[str, Any]] | None
        timeout: float | None

    HTTP_METHOD = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]

    class _RequieredRequestsArgs(TypedDict):
        method: HTTP_METHOD
        url: str

    class _CompleteRequestArgs(_RequieredRequestsArgs, _OptionalRequestsArgs): ...

    class ResponseLike(Protocol):
        def json(self, **kwargs: Any) -> Any: ...  # noqa: ANN401

        def raise_for_status(self) -> Any: ...  # noqa: ANN401

    R_co = TypeVar(
        "R_co",
        covariant=True,  #
        bound=ResponseLike,  #
    )

    class RequestLike(Protocol[R_co]):
        def request(
            self, method: HTTP_METHOD, url: str, **kwargs: Unpack[_OptionalRequestsArgs]
        ) -> R_co: ...

    class RequestLikeAsync(Protocol[R_co]):
        async def request(
            self, method: HTTP_METHOD, url: str, **kwargs: Unpack[_OptionalRequestsArgs]
        ) -> R_co: ...


class RequestTemplate:
    """
    A template for making HTTP requests.

    Args:
    ----
        method (HTTP_METHOD): The HTTP method to use for the request.
        url (str): The URL to send the request to.
        **kwargs: Additional keyword arguments to be passed to the request.

    Attributes:
    ----------
        _request_args (RequestLikeArgs): The arguments for the request.

    Methods:
    -------
        request: Sends the HTTP request.
        json: Sends the HTTP request and returns the response as JSON.

    """

    __slots__ = ("_request_args",)
    _request_args: _CompleteRequestArgs

    def __init__(self, method: HTTP_METHOD, url: str, **kwargs: _OptionalRequestsArgs) -> None:
        self._request_args = {"method": method, "url": url, **kwargs}  # type: ignore

    @overload
    def request(self, http_client: RequestLike[R_co]) -> R_co: ...

    @overload
    def request(self, http_client: RequestLikeAsync[R_co]) -> Awaitable[R_co]: ...

    def request(
        self, http_client: RequestLike[R_co] | RequestLikeAsync[R_co]
    ) -> R_co | Awaitable[R_co]:
        """
        Sends the HTTP request.

        Args:
        ----
            http_client (RequestLike[R_co] | RequestLikeAsync[R_co]): The HTTP client to use for the request.

        Returns:
        -------
            R_co | Awaitable[R_co]: The response from the HTTP request.

        """  # noqa: E501
        return http_client.request(**self._request_args)

    async def __asjon(self, response: Awaitable[R_co]) -> Incomplete:
        r = await response
        r.raise_for_status()
        return r.json()

    @overload
    def json(self, http_client: RequestLike[R_co]) -> Incomplete: ...

    @overload
    def json(self, http_client: RequestLikeAsync[R_co]) -> Awaitable[Incomplete]: ...

    def json(
        self, http_client: RequestLike[R_co] | RequestLikeAsync[R_co]
    ) -> Incomplete | Awaitable[Incomplete]:
        """
        Sends the HTTP request and returns the response as JSON.

        Args:
        ----
            http_client (RequestLike[R_co] | RequestLikeAsync[R_co]): The HTTP client to use for the request.

        Returns:
        -------
            Incomplete | Awaitable[Incomplete]: The response from the HTTP request as JSON.

        """  # noqa: E501
        response = self.request(http_client)
        if isawaitable(response):
            return self.__asjon(response)
        response = cast("R_co", response)
        response.raise_for_status()
        return response.json()


def _test1(template: RequestTemplate) -> None:
    import requests

    requests_session = requests.Session()

    # y: RequestLike = requests_session

    a = template.request(requests_session)
    a = template.json(requests_session)  # noqa: F841

    # from typing_extensions import reveal_type
    # reveal_type(template.request(requests_session))
    # reveal_type(template.json(requests_session))

    r1: requests.Response = template.request(requests_session)
    j1: Incomplete = template.json(requests_session)
    print(r1, j1)


def _test2(template: RequestTemplate) -> None:
    import httpx

    # e: RequestLike = httpx_client
    # p: RequestLike = httpx_async_client

    httpx_client = httpx.Client()
    a = template.request(httpx_client)
    a = template.json(httpx_client)

    r2: httpx._models.Response = template.request(httpx_client)
    j2: Incomplete = template.json(httpx_client)

    # reveal_type(template.request(httpx_client))
    # reveal_type(template.json(httpx_client))

    httpx_async_client = httpx.AsyncClient()
    a = template.request(httpx_async_client)
    a = template.json(httpx_async_client)  # noqa: F841

    r3: Awaitable[httpx._models.Response] = template.request(httpx_async_client)
    j3: Awaitable[Incomplete] = template.json(httpx_async_client)

    # reveal_type(template.request(httpx_async_client))
    # reveal_type(template.json(httpx_async_client))

    print(r2, j2, r3, j3)


def _test() -> None:
    template: RequestTemplate = RequestTemplate(method="GET", url="http://ip.jsontest.com/")
    _test1(template)
    # _test2(template)


if __name__ == "__main__":
    _test()
