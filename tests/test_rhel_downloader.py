"""Tests for the RHEL downloader."""

import json
from unittest.mock import MagicMock, patch

import pytest

from distro_support.rhel import _parse_date, get_distro_info

# Minimal realistic API response mirroring the Red Hat lifecycle API structure.
_FAKE_API_RESPONSE = {
    "data": [
        {
            "versions": [
                {
                    "name": "9",
                    "phases": [
                        {
                            "name": "General availability",
                            "end_date": "2022-05-18T00:00:00.000Z",
                        },
                        {
                            "name": "Full support",
                            "end_date": "2027-05-31T00:00:00.000Z",
                        },
                        {
                            "name": "Maintenance support",
                            "end_date": "2032-05-31T00:00:00.000Z",
                        },
                        {
                            "name": "Extended life cycle support (ELS) add-on",
                            "end_date": "2035-05-31T00:00:00.000Z",
                        },
                        {
                            "name": "Extended life phase",
                            "end_date": "Ongoing",
                        },
                    ],
                },
                {
                    "name": "7",
                    "phases": [
                        {
                            "name": "General availability",
                            "end_date": "2014-06-10T00:00:00.000Z",
                        },
                        {
                            "name": "Full support",
                            "end_date": "2019-08-06T00:00:00.000Z",
                        },
                        {
                            "name": "Maintenance support",
                            "end_date": "2024-06-30T00:00:00.000Z",
                        },
                        {
                            "name": "Extended life cycle support (ELS) add-on",
                            "end_date": "2029-05-31T00:00:00.000Z",
                        },
                        {
                            "name": "Extended life phase",
                            "end_date": "Ongoing",
                        },
                    ],
                },
                {
                    # Version with N/A GA date (as seen in some older entries)
                    "name": "6",
                    "phases": [
                        {
                            "name": "General availability",
                            "end_date": "N/A",
                        },
                        {
                            "name": "Maintenance support",
                            "end_date": "2020-11-30T00:00:00.000Z",
                        },
                        # No ELS phase for this entry
                    ],
                },
            ]
        }
    ]
}


def _make_mock_response(data: dict):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps(data).encode()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    return mock_response


@pytest.fixture
def mock_urlopen():
    with patch("distro_support.rhel.request.urlopen") as mock:
        mock.return_value = _make_mock_response(_FAKE_API_RESPONSE)
        yield mock


class TestParseDate:
    def test_iso_timestamp(self):
        assert _parse_date("2022-05-18T00:00:00.000Z") == "2022-05-18"

    def test_plain_iso_date(self):
        assert _parse_date("2022-05-18") == "2022-05-18"

    def test_ongoing_returns_none(self):
        assert _parse_date("Ongoing") is None

    def test_ongoing_case_insensitive(self):
        assert _parse_date("ongoing") is None

    def test_na_returns_none(self):
        assert _parse_date("N/A") is None

    def test_na_case_insensitive(self):
        assert _parse_date("n/a") is None

    def test_none_returns_none(self):
        assert _parse_date(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_date("") is None


class TestGetDistroInfo:
    def test_returns_all_versions(self, mock_urlopen):
        result = get_distro_info()
        assert set(result.keys()) == {"9", "7", "6"}

    def test_distribution_name(self, mock_urlopen):
        result = get_distro_info()
        for ver in result.values():
            assert ver["distribution"] == "rhel"

    def test_version_field_matches_key(self, mock_urlopen):
        result = get_distro_info()
        for key, ver in result.items():
            assert ver["version"] == key

    def test_begin_dev_equals_begin_support(self, mock_urlopen):
        """begin_dev is set to the GA date so is_in_development_on always returns False."""
        result = get_distro_info()
        for ver in result.values():
            assert ver["begin_dev"] == ver["begin_support"]

    def test_full_version_dates(self, mock_urlopen):
        result = get_distro_info()
        assert result["9"]["begin_support"] == "2022-05-18"
        assert result["9"]["end_support"] == "2032-05-31"
        assert result["9"]["end_extended_support"] == "2035-05-31"

    def test_ongoing_eol_is_none(self, mock_urlopen):
        # Extended life phase is "Ongoing" — should not bleed into our fields
        result = get_distro_info()
        assert result["9"]["end_extended_support"] == "2035-05-31"

    def test_na_ga_date_is_none(self, mock_urlopen):
        result = get_distro_info()
        assert result["6"]["begin_support"] is None

    def test_missing_els_phase_is_none(self, mock_urlopen):
        result = get_distro_info()
        assert result["6"]["end_extended_support"] is None

    def test_sends_user_agent(self, mock_urlopen):
        get_distro_info()
        req = mock_urlopen.call_args[0][0]
        assert req.get_header("User-agent") == "distro-support"

    def test_http_error_raises(self):
        mock_response = _make_mock_response(_FAKE_API_RESPONSE)
        mock_response.status = 503
        with patch("distro_support.rhel.request.urlopen", return_value=mock_response):
            with pytest.raises(ConnectionError):
                get_distro_info()
