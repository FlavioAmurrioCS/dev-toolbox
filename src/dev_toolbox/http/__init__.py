from __future__ import annotations

from inspect import isawaitable
from typing import cast
from typing import overload
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dev_toolbox.http._types import HTTP_METHOD
    from dev_toolbox.http._types import _CompleteRequestArgs
    from dev_toolbox.http._types import R_co
    from dev_toolbox.http._types import _OptionalRequestsArgs
    from dev_toolbox.http._types import RequestLike
    from dev_toolbox.http._types import RequestLikeAsync
    from typing_extensions import Unpack
    from typing import Awaitable
    from _typeshed import Incomplete


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

    def __init__(
        self, *, url: str, method: HTTP_METHOD = "GET", **kwargs: Unpack[_OptionalRequestsArgs]
    ) -> None:
        self._request_args = {"method": method, "url": url, **kwargs}

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
