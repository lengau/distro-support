"""Information about Ubuntu support."""

import csv
import http.client
from urllib import request

SUPPORT_INFO_URL = (
    "https://git.launchpad.net/ubuntu/+source/distro-info-data/plain/ubuntu.csv"
)


def get_distro_info() -> dict[str, dict[str, str]]:
    response: http.client.HTTPResponse = request.urlopen(SUPPORT_INFO_URL)
    if response.status != 200:
        raise ConnectionError(response.status)
    reader = csv.DictReader(response.read().decode().splitlines())
    series = {}
    for row in reader:
        version = row["version"].removesuffix(" LTS")
        series[version] = {
            "distribution": "ubuntu",
            "version": version,
            "begin_support": row["release"],
            "end_support": row["eol-server"],
            "begin_dev": row["created"],
            "end_extended_support": row["eol-esm"],
        }
    return series
