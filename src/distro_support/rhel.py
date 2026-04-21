"""Information about Red Hat Enterprise Linux support."""

import json
from urllib import request

SUPPORT_INFO_URL = "https://access.redhat.com/product-life-cycles/api/v1/products?name=Red+Hat+Enterprise+Linux"

_PHASE_GA = "general availability"
_PHASE_MAINTENANCE = "maintenance support"
_PHASE_ELS = "extended life cycle support (els) add-on"


def _parse_date(value: str | None) -> str | None:
    """Return an ISO date string (YYYY-MM-DD), or None for missing/non-date values."""
    if not value or value.upper() == "N/A" or value.lower() == "ongoing":
        return None
    return value[:10]


def get_distro_info() -> dict[str, dict[str, str | None]]:
    req = request.Request(SUPPORT_INFO_URL, headers={"User-Agent": "distro-support"})
    with request.urlopen(req) as response:
        if response.status != 200:
            raise ConnectionError(response.status)
        data = json.loads(response.read())

    series = {}
    for version in data["data"][0]["versions"]:
        ver = version["name"]
        phases = {p["name"].lower(): p for p in version["phases"]}

        series[ver] = {
            "distribution": "rhel",
            "version": ver,
            "begin_support": _parse_date(phases.get(_PHASE_GA, {}).get("end_date")),
            "end_support": _parse_date(
                phases.get(_PHASE_MAINTENANCE, {}).get("end_date")
            ),
            "begin_dev": _parse_date(phases.get(_PHASE_GA, {}).get("end_date")),
            "end_extended_support": _parse_date(
                phases.get(_PHASE_ELS, {}).get("end_date")
            ),
        }
    return series
