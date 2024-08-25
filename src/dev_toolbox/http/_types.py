from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Dict
    from typing import List
    from typing import Any
    from typing import Mapping
    from typing import Union
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
    _Params = Union[Dict[str, Any], Tuple[Tuple[str, Any], ...], List[Tuple[str, Any]], None]

    class _OptionalRequestsArgs(TypedDict, total=False):
        auth: tuple[str, str] | None
        cookies: dict[str, str] | None
        data: Mapping[str, Any] | None
        files: Mapping[str, _FileSpec]
        headers: Mapping[str, Any] | None
        json: Any | None
        params: _Params
        timeout: float | None

    HTTP_METHOD = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]

    class _RequieredRequestsArgs(TypedDict):
        method: HTTP_METHOD
        url: str

    class _CompleteRequestArgs(_RequieredRequestsArgs, _OptionalRequestsArgs): ...

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
        def request(
            self, method: HTTP_METHOD, url: str, **kwargs: Unpack[_OptionalRequestsArgs]
        ) -> R_co: ...

    class RequestLikeAsync(Protocol[R_co]):
        async def request(
            self, method: HTTP_METHOD, url: str, **kwargs: Unpack[_OptionalRequestsArgs]
        ) -> R_co: ...
