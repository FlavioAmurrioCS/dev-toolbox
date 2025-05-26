from __future__ import annotations

import io
import json
import logging
import re
import tempfile
import zipfile
from email.parser import BytesParser
from typing import TYPE_CHECKING
from typing import Mapping
from typing import NamedTuple
from typing import TypedDict
from typing import TypeVar
from urllib.parse import urljoin
from urllib.parse import urlparse

if TYPE_CHECKING:
    from email.message import Message

    import httpx
    import requests

    T = TypeVar("T", bound=Mapping)  # type: ignore[type-arg]

    class Metadata(TypedDict):
        author: str
        author_email: str
        bugtrack_url: str | None
        classifiers: list[str]
        description: str
        description_content_type: str
        docs_url: str | None
        download_url: str | None
        dynamic: str | None
        home_page: str
        keywords: str | None
        license: str
        license_expression: str | None
        license_files: str | None
        maintainer: str | None
        maintainer_email: str | None
        name: str
        package_url: str
        platform: str | None
        project_url: str
        project_urls: dict[str, str]
        provides_extra: list[str]
        release_url: str
        requires_dist: list[str]
        requires_python: str
        summary: str
        version: str
        yanked: bool
        yanked_reason: str | None


logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
# )


def _extract_version_from_filename(x: str) -> str:
    x = x.split("/")[-1]
    return x.split(".tar.gz")[0].split("-")[-1] if x.endswith(".tar.gz") else x.split("-")[1]


def _parsed_version(x: str) -> tuple[int, ...]:
    return tuple(map(int, re.findall(r"\d+", x)))


def _normalize_string(x: str) -> str:
    return x.strip().lower().replace("-", "_")


def _parse_message(x: Message[str, str]) -> Metadata:
    metadata = {}  # type: ignore[var-annotated]
    for key, value in x.items():
        if key in metadata:
            if isinstance(metadata[key], list):
                metadata[key].append(value)
            else:
                metadata[key] = [metadata[key], value]
        else:
            metadata[key] = value  # type: ignore[assignment]

    ret = {_normalize_string(k): v for k, v in metadata.items()}
    ret["project_urls"] = {}  # type: ignore[assignment]
    items = ret.pop("project_url", [])
    items = items if isinstance(items, list) else [items]
    for line in items:
        key, value = line.split(",", 1)
        ret["project_urls"][key.strip()] = value.strip()  # type: ignore[call-overload]
    ret["classifiers"] = ret.pop("classifier", [])
    ret.pop("metadata_version", None)

    return ret  # type: ignore[return-value]


def _json_clean(obj: T) -> T:
    return json.loads(
        json.dumps({k: v for k, v in obj.items() if v is not None}, sort_keys=True, skipkeys=True)
    )


_header: dict[str, str] = {  # format
    # "Accept": "application/vnd.pypi.simple.v1+json"
}


class PypiIndexApi(NamedTuple):
    client: requests.Session | httpx.Client
    base_url: str = "https://pypi.org"

    def http_get(self, path: str) -> str:
        url = urljoin(self.base_url, path)
        response = self.client.get(url, headers=_header)
        response.raise_for_status()
        return response.text

    def get_all_projects(self) -> list[str]:
        response = self.http_get("/simple/")
        try:
            return [x["name"] for x in json.loads(response)["projects"]]
        except json.JSONDecodeError:
            logger.debug("Not JSON, trying to parse as HTML")

        pattern = re.compile(r'<a href="([^"]+)">([^<]+)</a>')
        return [x.group(2) for x in pattern.finditer(response)]

    def get_distributions(self, package_name: str) -> list[str]:
        response = self.http_get(f"/simple/{package_name}/")
        urls: list[str] = []
        try:
            urls.extend(x["url"] for x in json.loads(response)["files"])
        except json.JSONDecodeError:
            logger.debug("Not JSON, trying to parse as HTML")

            pattern = re.compile(r'href="([^"]+)"')
            urls.extend(
                urlparse(urljoin(self.base_url, x.group(1)))._replace(fragment="").geturl()
                for x in pattern.finditer(response)
            )
        return urls

    def get_versions(self, package_name: str) -> list[str]:
        files = self.get_distributions(package_name)
        return sorted(
            {_extract_version_from_filename(x) for x in files},
            key=lambda x: _parsed_version(x),
        )

    def get_metadata(self, package_name: str) -> Metadata:
        response = self.http_get(f"/pypi/{package_name}/json")
        ret = {}
        try:
            ret.update(json.loads(response)["info"])
            ret.pop("description", None)
            ret.pop("license", None)
            ret.pop("downloads", None)
        except json.JSONDecodeError:
            ret.update(self._get_metadata_from_whl(package_name))

        return _json_clean(ret)  # type: ignore[return-value]

    def _get_metadata_from_whl(self, package_name: str) -> Metadata:
        latest_wheel_url = max(
            (x for x in self.get_distributions(package_name) if x.endswith(".whl")),
            key=lambda x: _parsed_version(_extract_version_from_filename(x)),
        )
        with tempfile.TemporaryDirectory():
            response = self.client.get(latest_wheel_url)
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                metadata_path = next(
                    (x for x in zf.namelist() if x.endswith("METADATA")),
                    None,
                )
                if not metadata_path:
                    msg = f"METADATA file not found in {latest_wheel_url}"
                    raise FileNotFoundError(msg)
                with zf.open(metadata_path) as metadata_file:
                    ret = _parse_message(BytesParser().parse(metadata_file))
                    ret.pop("license", None)  # type: ignore[misc]
                    return ret
