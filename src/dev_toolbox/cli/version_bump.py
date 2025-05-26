# flake8: noqa: S603
from __future__ import annotations

import argparse
import signal
import subprocess
from functools import partial
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import Sequence

from typing_extensions import Self

if TYPE_CHECKING:
    from types import FrameType


def handler(signal: int, frame: FrameType | None) -> None:  # noqa: ARG001
    raise SystemExit(1)


signal.signal(signal.SIGINT, handler)


class Version(NamedTuple):
    major: int
    minor: int
    micro: int

    @classmethod
    def parse(cls, version: str) -> Self:
        return cls(*map(int, version.lstrip("v").split(".")))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.micro}"


quick_run = partial(subprocess.run, check=True, encoding="utf-8", errors="ignore")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bump the version of a git repository",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "part",
        choices=["major", "minor", "micro"],
        help="The part of the version to bump",
        default="micro",
        nargs="?",
    )
    args = parser.parse_args(args=argv)

    if quick_run(("git", "status", "--porcelain=v1"), capture_output=True).stdout.strip():
        print("The working directory is not clean. Aborting.")
        return 1

    main_branch = quick_run(
        ("git", "symbolic-ref", "refs/remotes/origin/HEAD", "--short"), capture_output=True
    ).stdout.strip()[len("origin/") :]

    quick_run(("git", "checkout", main_branch))
    quick_run(("git", "pull"))

    if quick_run(
        ("git", "log", f"origin/{main_branch}..{main_branch}", "--oneline"), capture_output=True
    ).stdout.strip():
        print(f"Branch {main_branch} is not up to date with origin. Aborting.")
        return 1

    latest_tag = max(
        quick_run(("git", "tag", "--list"), capture_output=True).stdout.splitlines(),
        key=Version.parse,
    )
    _latest_tag_hash = quick_run(
        ("git", "show-ref", "-s", latest_tag), capture_output=True
    ).stdout.strip()
    _lastest_commit_hash = quick_run(
        ("git", "rev-parse", "HEAD"), capture_output=True
    ).stdout.strip()

    if _lastest_commit_hash == _latest_tag_hash:
        print(f"Latest tag: {latest_tag} is up to date is already pointing to the latest commit.")
        return 0
    old_version = Version.parse(latest_tag)
    if args.part == "major":
        new_version = Version.parse(f"{old_version.major + 1}.0.0")
    elif args.part == "minor":
        new_version = Version.parse(f"{old_version.major}.{old_version.minor + 1}.0")
    else:
        new_version = Version.parse(
            f"{old_version.major}.{old_version.minor}.{old_version.micro + 1}"
        )

    _new_version_tag = f"v{new_version}" if latest_tag.startswith("v") else str(new_version)
    print(f"Old version: {latest_tag}")
    print(f"New version: {_new_version_tag}")

    if input("Should we tag and push the new version? ").lower() not in {"yes", "y"}:
        return 0

    quick_run(("git", "tag", _new_version_tag))
    quick_run(("git", "push", "--tags"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
