"""Downloader for distro info for debian-like distributions."""

import csv
import http.client
from urllib import request


def get_distro_info(url: str, *, name: str, esm_name: str) -> dict[str, dict[str, str]]:
    response: http.client.HTTPResponse = request.urlopen(url)
    if response.status != 200:
        raise ConnectionError(response.status)
    reader = csv.DictReader(response.read().decode().splitlines())
    series = {}
    for row in reader:
        version = row["version"].removesuffix(" LTS")
        series[version] = {
            "distribution": name,
            "version": version,
            "begin_support": row["release"],
            "end_support": row["eol"],
            "begin_dev": row["created"],
            "end_extended_support": row[f"eol-{esm_name}"],
        }
    return series
