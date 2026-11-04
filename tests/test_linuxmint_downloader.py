"""Tests for the Linux Mint downloader."""

import json
import unittest.mock

import pytest

import distro_support
from distro_support import linuxmint, mint
from distro_support._distro import SupportRange

SAMPLE_MINT_RELEASES = json.dumps(
    {
        "website": {
            "Linux Mint 22.3 Zena": "zena",
            "Linux Mint 22 Wilma": "wilma",
            "Linux Mint 21.3 Virginia": "virginia",
            "LMDE 6 Faye": "faye",
        },
        "codenames": ["wilma", "zena", "virginia", "faye"],
        "groups": {
            "22": ["wilma", "zena"],
            "21": ["virginia"],
            "lmde6": ["faye"],
        },
        "bases": {
            "zena": "noble",
            "wilma": "noble",
            "virginia": "jammy",
            "faye": "bookworm",
        },
        "versions": {
            "zena": 22.3,
            "wilma": 22,
            "virginia": 21.3,
            "faye": 6,
        },
    }
)


def _make_response(body: str, status: int = 200):
    mock_response = unittest.mock.MagicMock()
    mock_response.status = status
    mock_response.read.return_value = body.encode()
    return mock_response


@unittest.mock.patch("distro_support.linuxmint.request.urlopen")
def test_parses_mint_releases(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_MINT_RELEASES)

    result = linuxmint.get_distro_info()

    assert "22" in result
    assert "22.3" in result
    assert "21.3" in result
    assert "6" in result
    assert "lmde6" in result

    # Check Ubuntu 24.04 noble base mapping
    assert result["22"]["distribution"] == "linuxmint"
    assert result["22"]["end_support"] == "2029-05-31"

    # Check Debian 12 bookworm base mapping
    assert result["6"]["distribution"] == "linuxmint"
    assert result["6"]["end_support"] == "2026-07-11"

    # Check SupportRange conversion
    support_range = SupportRange.from_json(result["22.3"])
    assert support_range.version == "22.3"
    assert support_range.end_support is not None


@unittest.mock.patch("distro_support.linuxmint.request.urlopen")
def test_http_error_raises(mock_urlopen):
    mock_urlopen.return_value = _make_response("", status=500)

    with pytest.raises(ConnectionError):
        linuxmint.get_distro_info()


@unittest.mock.patch("distro_support.linuxmint.request.urlopen")
def test_mint_alias_module(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_MINT_RELEASES)

    result = mint.get_distro_info()
    assert "22.3" in result


@unittest.mock.patch("distro_support.linuxmint.request.urlopen")
def test_get_support_range_online(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_MINT_RELEASES)

    range_obj = distro_support.get_support_range("linuxmint", "22.3", get_online=True)
    assert range_obj.distribution == "linuxmint"
    assert range_obj.version == "22.3"

    range_alias = distro_support.get_support_range("mint", "22.3", get_online=True)
    assert range_alias.distribution == "linuxmint"
    assert range_alias.version == "22.3"
