"""Tests for the debian-like downloader."""

import unittest.mock

import pytest

from distro_support import _debian_like_downloader
from distro_support._distro import SupportRange


def _make_response(csv_text: str, status: int = 200):
    mock_response = unittest.mock.MagicMock()
    mock_response.status = status
    mock_response.read.return_value = csv_text.encode()
    mock_response.__enter__ = lambda self: self
    mock_response.__exit__ = unittest.mock.MagicMock(return_value=False)
    return mock_response


CSV_WITH_EMPTY_ESM = """\
version,release,eol,created,eol-esm
22.04 LTS,2022-04-21,2027-04-01,2021-10-14,2032-04-09
24.04 LTS,2024-04-25,2029-04-25,2023-10-12,
"""

CSV_WITHOUT_ESM = """\
version,release,eol,created
5,2021-01-01,2026-06-15,2020-01-01
"""


@unittest.mock.patch("distro_support._debian_like_downloader.request.urlopen")
def test_empty_esm_column_returns_none(mock_urlopen):
    """An empty eol-esm column must produce None, not an empty string.

    Without the `or None` fix, row.get() returns "" for an empty CSV cell.
    SupportRange.from_json() checks `is None`, so "" bypasses the guard and
    datetime.date.fromisoformat("") raises a ValueError when the data is used.
    """
    mock_urlopen.return_value = _make_response(CSV_WITH_EMPTY_ESM)

    result = _debian_like_downloader.get_distro_info(
        "https://example.com/data.csv", name="ubuntu", esm_name="esm"
    )

    assert result["24.04"]["end_extended_support"] is None
    # Verify the data round-trips through SupportRange.from_json without error
    support_range = SupportRange.from_json(result["24.04"])
    assert support_range.end_extended_support is None


@unittest.mock.patch("distro_support._debian_like_downloader.request.urlopen")
def test_populated_esm_column_returns_date_string(mock_urlopen):
    """A populated eol-esm column must be returned as-is."""
    mock_urlopen.return_value = _make_response(CSV_WITH_EMPTY_ESM)

    result = _debian_like_downloader.get_distro_info(
        "https://example.com/data.csv", name="ubuntu", esm_name="esm"
    )

    assert result["22.04"]["end_extended_support"] == "2032-04-09"


@unittest.mock.patch("distro_support._debian_like_downloader.request.urlopen")
def test_no_esm_name_returns_none(mock_urlopen):
    """When esm_name is not provided, end_extended_support must be None."""
    mock_urlopen.return_value = _make_response(CSV_WITHOUT_ESM)

    result = _debian_like_downloader.get_distro_info(
        "https://example.com/data.csv", name="devuan"
    )

    assert result["5"]["end_extended_support"] is None


@unittest.mock.patch("distro_support._debian_like_downloader.request.urlopen")
def test_http_error_raises(mock_urlopen):
    mock_urlopen.return_value = _make_response("", status=404)

    with pytest.raises(ConnectionError):
        _debian_like_downloader.get_distro_info(
            "https://example.com/data.csv", name="ubuntu"
        )
