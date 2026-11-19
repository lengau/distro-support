"""Information about Linux Mint support."""

import json
import pathlib
from urllib import request

SUPPORT_INFO_URL = "http://packages.linuxmint.com/releases.json"  # nosec B310 # nosemgrep

UBUNTU_SERIES_TO_VERSION = {
    "precise": "12.04",
    "trusty": "14.04",
    "xenial": "16.04",
    "bionic": "18.04",
    "focal": "20.04",
    "jammy": "22.04",
    "noble": "24.04",
    "resolute": "26.04",
}

DEBIAN_SERIES_TO_VERSION = {
    "wheezy": "7",
    "jessie": "8",
    "stretch": "9",
    "buster": "10",
    "bullseye": "11",
    "bookworm": "12",
    "trixie": "13",
    "forky": "14",
}

HISTORICAL_BASES = {
    "ulyana": "focal",
    "ulyssa": "focal",
    "uma": "focal",
    "una": "focal",
    "tara": "bionic",
    "tessa": "bionic",
    "tina": "bionic",
    "tricia": "bionic",
    "sarah": "xenial",
    "serena": "xenial",
    "sonya": "xenial",
    "sylvia": "xenial",
    "qiana": "trusty",
    "rebecca": "trusty",
    "rafaela": "trusty",
    "rosa": "trusty",
    "maya": "precise",
    "elsie": "bullseye",
    "debbie": "buster",
    "cindy": "stretch",
    "betsy": "jessie",
    "debian": "wheezy",
}

HISTORICAL_VERSIONS = {
    "ulyana": "20",
    "ulyssa": "20.1",
    "uma": "20.2",
    "una": "20.3",
    "tara": "19",
    "tessa": "19.1",
    "tina": "19.2",
    "tricia": "19.3",
    "sarah": "18",
    "serena": "18.1",
    "sonya": "18.2",
    "sylvia": "18.3",
    "qiana": "17",
    "rebecca": "17.1",
    "rafaela": "17.2",
    "rosa": "17.3",
    "maya": "13",
    "elsie": "5",
    "debbie": "4",
    "cindy": "3",
    "betsy": "2",
    "debian": "1",
}

KNOWN_RELEASE_DATES = {
    "27": "2026-08-01",
    "22.3": "2026-01-11",
    "22.2": "2025-09-04",
    "22.1": "2025-01-14",
    "22": "2024-07-25",
    "21.3": "2024-01-12",
    "21.2": "2023-07-16",
    "21.1": "2022-12-20",
    "21": "2022-07-31",
    "20.3": "2022-01-07",
    "20.2": "2021-07-08",
    "20.1": "2021-01-08",
    "20": "2020-06-27",
    "19.3": "2019-12-18",
    "19.2": "2019-08-02",
    "19.1": "2018-12-19",
    "19": "2018-06-29",
    "18.3": "2017-11-27",
    "18.2": "2017-07-02",
    "18.1": "2016-12-16",
    "18": "2016-06-30",
    "17.3": "2015-12-04",
    "17.2": "2015-06-30",
    "17.1": "2014-11-29",
    "17": "2014-05-31",
    "13": "2012-05-23",
    "7": "2025-10-14",
    "lmde7": "2025-10-14",
    "6": "2023-09-27",
    "lmde6": "2023-09-27",
    "5": "2022-03-20",
    "lmde5": "2022-03-20",
    "4": "2020-03-20",
    "lmde4": "2020-03-20",
    "3": "2018-08-31",
    "lmde3": "2018-08-31",
    "2": "2015-04-10",
    "lmde2": "2015-04-10",
    "1": "2010-09-07",
    "lmde1": "2010-09-07",
}


def _load_upstream_data(distribution: str) -> dict[str, dict[str, str | None]]:
    path = pathlib.Path(__file__).with_name(f"{distribution}.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _build_entry(
    version_str: str,
    base: str,
    ubuntu_info: dict[str, dict[str, str | None]],
    debian_info: dict[str, dict[str, str | None]],
) -> dict[str, str | None] | None:
    upstream_info: dict[str, str | None] | None = None
    if base in UBUNTU_SERIES_TO_VERSION:
        u_ver = UBUNTU_SERIES_TO_VERSION[base]
        upstream_info = ubuntu_info.get(u_ver)
    elif base in DEBIAN_SERIES_TO_VERSION:
        d_ver = DEBIAN_SERIES_TO_VERSION[base]
        upstream_info = debian_info.get(d_ver)

    if not upstream_info:
        return None

    begin_support = KNOWN_RELEASE_DATES.get(version_str) or upstream_info.get(
        "begin_support"
    )
    return {
        "distribution": "linuxmint",
        "version": version_str,
        "begin_support": begin_support,
        "end_support": upstream_info.get("end_support"),
        "begin_dev": upstream_info.get("begin_dev"),
        "end_extended_support": None,
    }


def get_distro_info() -> dict[str, dict[str, str | None]]:
    response = request.urlopen(  # nosec B310 # nosemgrep
        SUPPORT_INFO_URL, timeout=10
    )
    if response.status != 200:
        raise ConnectionError(response.status)
    mint_data = json.load(response)

    ubuntu_info = _load_upstream_data("ubuntu")
    debian_info = _load_upstream_data("debian")

    bases = dict(HISTORICAL_BASES)
    bases.update(mint_data.get("bases", {}))

    versions = dict(HISTORICAL_VERSIONS)
    for codename, ver in mint_data.get("versions", {}).items():
        versions[codename] = str(ver)

    series: dict[str, dict[str, str | None]] = {}
    for codename, version_str in versions.items():
        base = bases.get(codename)
        if not base:
            continue

        entry = _build_entry(version_str, base, ubuntu_info, debian_info)
        if not entry:
            continue

        series[version_str] = entry

        # LMDE releases use both numeric and prefixed identifiers in practice.
        if base in DEBIAN_SERIES_TO_VERSION:
            lmde_key = f"lmde{version_str}"
            lmde_entry = dict(entry)
            lmde_entry["version"] = lmde_key
            series[lmde_key] = lmde_entry

    return series
