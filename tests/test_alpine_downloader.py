"""Tests for the Alpine Linux downloader."""

import json
import unittest.mock

import pytest

from distro_support import alpine
from distro_support._distro import SupportRange

SAMPLE_JSON = json.dumps(
    {
        "latest_stable": "v3.21",
        "release_branches": [
            {
                "rel_branch": "edge",
                "git_branch": "master",
            },
            {
                "rel_branch": "v3.21",
                "branch_date": "2024-12-05",
                "eol_date": "2026-11-01",
                "git_branch": "3.21-stable",
            },
            {
                "rel_branch": "v3.20",
                "branch_date": "2024-05-22",
                "eol_date": "2026-04-01",
                "git_branch": "3.20-stable",
            },
            {
                "rel_branch": "v3.19",
                "branch_date": "2023-12-07",
                "eol_date": "2025-11-01",
                "git_branch": "3.19-stable",
            },
        ],
    }
)


def _make_response(body: str, status: int = 200):
    mock_response = unittest.mock.MagicMock()
    mock_response.status = status
    mock_response.read.return_value = body.encode()
    return mock_response


@unittest.mock.patch("distro_support.alpine.request.urlopen")
def test_parses_all_versioned_branches(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_JSON)

    result = alpine.get_distro_info()

    assert set(result.keys()) == {"3.21", "3.20", "3.19"}


@unittest.mock.patch("distro_support.alpine.request.urlopen")
def test_skips_edge(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_JSON)

    result = alpine.get_distro_info()

    assert "edge" not in result


@unittest.mock.patch("distro_support.alpine.request.urlopen")
def test_correct_dates(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_JSON)

    result = alpine.get_distro_info()

    assert result["3.21"]["begin_support"] == "2024-12-05"
    assert result["3.21"]["end_support"] == "2026-11-01"


@unittest.mock.patch("distro_support.alpine.request.urlopen")
def test_no_dev_or_esm_fields(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_JSON)

    result = alpine.get_distro_info()

    assert result["3.21"]["begin_dev"] is None
    assert result["3.21"]["end_extended_support"] is None


@unittest.mock.patch("distro_support.alpine.request.urlopen")
def test_roundtrip_through_support_range(mock_urlopen):
    mock_urlopen.return_value = _make_response(SAMPLE_JSON)

    result = alpine.get_distro_info()
    sr = SupportRange.from_json(result["3.21"])

    assert sr.distribution == "alpine"
    assert sr.version == "3.21"
    assert sr.end_extended_support is None


@unittest.mock.patch("distro_support.alpine.request.urlopen")
def test_http_error_raises(mock_urlopen):
    mock_urlopen.return_value = _make_response("", status=404)

    with pytest.raises(ConnectionError):
        alpine.get_distro_info()
