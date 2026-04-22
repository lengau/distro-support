"""Information about Alpine Linux support."""

import http.client
import json
from urllib import request

RELEASES_URL = "https://alpinelinux.org/releases.json"


def get_distro_info() -> dict[str, dict[str, str | None]]:
    response: http.client.HTTPResponse = request.urlopen(RELEASES_URL, timeout=10)
    if response.status != 200:
        raise ConnectionError(response.status)

    data = json.load(response)
    series: dict[str, dict[str, str | None]] = {}

    for branch in data.get("release_branches", []):
        rel_branch: str = branch.get("rel_branch", "")
        if not rel_branch.startswith("v"):
            continue  # skip 'edge'

        version = rel_branch.lstrip("v")
        series[version] = {
            "distribution": "alpine",
            "version": version,
            "begin_support": branch.get("branch_date") or None,
            "end_support": branch.get("eol_date") or None,
            "begin_dev": None,
            "end_extended_support": None,
        }

    return series
