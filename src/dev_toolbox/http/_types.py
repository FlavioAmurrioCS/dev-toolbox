from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import IO
    from typing import Any
    from typing import Optional
    from typing import TypeVar
    from typing import Union

    from typing_extensions import Literal
    from typing_extensions import NotRequired
    from typing_extensions import Protocol
    from typing_extensions import TypedDict
    from typing_extensions import Unpack

    FileContent = Union[IO[bytes], bytes, str]
    _FileSpec = Union[
        FileContent,
        tuple[Optional[str], FileContent],
    ]
    _Params = Union[dict[str, Any], tuple[tuple[str, Any], ...], list[tuple[str, Any]], None]

    HTTP_METHOD = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]

    class _CompleteRequestArgs(TypedDict):
        url: str
        method: HTTP_METHOD
        auth: NotRequired[tuple[str, str] | None]
        cookies: NotRequired[dict[str, str] | None]
        data: NotRequired[Mapping[str, Any] | None]
        files: NotRequired[Mapping[str, _FileSpec]]
        headers: NotRequired[Mapping[str, Any] | None]
        json: NotRequired[Any | None]
        params: NotRequired[_Params]
        timeout: NotRequired[float | None]

    class ResponseLike(Protocol):
        def json(self) -> Any: ...  # noqa: ANN401

        def raise_for_status(self) -> Any: ...  # noqa: ANN401

    ResponseLike_co = TypeVar(
        "ResponseLike_co",
        covariant=True,
        bound=ResponseLike,
    )

    R_co = TypeVar(
        "R_co",
        covariant=True,
    )

    class RequestLike(Protocol[R_co]):
        def request(self, **kwargs: Unpack[_CompleteRequestArgs]) -> R_co: ...

    class RequestLikeAsync(Protocol[R_co]):
        async def request(self, **kwargs: Unpack[_CompleteRequestArgs]) -> R_co: ...
