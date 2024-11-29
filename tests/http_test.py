from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from dev_toolbox.http import RequestTemplate
    from _typeshed import Incomplete


@pytest.fixture
def template() -> RequestTemplate:
    from dev_toolbox.http import RequestTemplate

    return RequestTemplate(
        url="http://ip.jsontest.com/",
        method="GET",
        headers={"User-Agent": "Mozilla/5.0"},
    )


def test_requests(template: RequestTemplate) -> None:
    import requests

    requests_session = requests.Session()

    # y: RequestLike = requests_session

    a = template.request(requests_session)
    a = template.json(requests_session)

    r1: requests.Response = template.request(requests_session)
    j1: Incomplete = template.json(requests_session)

    # from typing_extensions import reveal_type
    # reveal_type(template.request(requests_session))
    # reveal_type(template.json(requests_session))

    print(a, r1, j1)


def test_httpx(template: RequestTemplate) -> None:
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
    print(a, r2, j2)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_httpx_async(template: RequestTemplate) -> None:
    import httpx

    httpx_async_client = httpx.AsyncClient()
    a = await template.request(httpx_async_client)
    a = await template.json(httpx_async_client)

    # r3: Awaitable[httpx._models.Response] = template.request(httpx_async_client)
    # j3: Awaitable[Incomplete] = template.json(httpx_async_client)

    # reveal_type(template.request(httpx_async_client))
    # reveal_type(template.json(httpx_async_client))

    print(a)


def test_great_value(template: RequestTemplate) -> None:
    from dev_toolbox.http.great_value import GreatValueRequests
    from dev_toolbox.http.great_value import GreatValueResponse

    gv_client = GreatValueRequests()
    a = template.request(gv_client)
    a = template.json(gv_client)

    r3: GreatValueResponse = template.request(gv_client)
    j3: Incomplete = template.json(gv_client)

    # reveal_type(template.request(httpx_async_client))
    # reveal_type(template.json(httpx_async_client))

    print(a, r3, j3)


# def test_main() -> None:
#     from dev_toolbox.http import RequestTemplate

#     template = RequestTemplate(
#         url="http://ip.jsontest.com/",
#         headers={"User-Agent": "Mozilla/5.0"},
#     )

#     test_great_value(template)
#     test_requests(template)
#     test_httpx(template)
#     test_httpx_async(template)


# def test_main2() -> None:
#     from dev_toolbox.http import RequestTemplate
#     from dev_toolbox.http.great_value import GreatValueRequests

#     client = GreatValueRequests(base_url="https://motionless-hearty-bongo.anvil.app")

#     template = RequestTemplate(method="POST", url="/gron", json={"name": "John Doe"})
#     response = template.request(client)
#     print(response.response.read().decode("utf-8"))

#     template = RequestTemplate(
#         url="/get_tables",
#         params={"url": "https://aws.amazon.com/ec2/instance-types/"},
#     )
#     response = template.json(client)
#     print(response)


# if __name__ == "__main__":
#     test_main2()
