"""Tests for the Linux Mint downloader."""

import json
import unittest
import unittest.mock

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
    mock_response.__enter__ = lambda self: self
    mock_response.__exit__ = unittest.mock.MagicMock(return_value=False)
    return mock_response


class LinuxMintDownloaderTestCase(unittest.TestCase):
    """Test suite for the Linux Mint downloader."""

    @unittest.mock.patch("distro_support.linuxmint.request.urlopen")
    def test_parses_mint_releases(self, mock_urlopen):
        mock_urlopen.return_value = _make_response(SAMPLE_MINT_RELEASES)

        result = linuxmint.get_distro_info()

        self.assertIn("22", result)
        self.assertIn("22.3", result)
        self.assertIn("21.3", result)
        self.assertIn("6", result)
        self.assertIn("lmde6", result)

        self.assertEqual(result["22"]["distribution"], "linuxmint")
        self.assertEqual(result["22"]["end_support"], "2029-05-31")

        self.assertEqual(result["6"]["distribution"], "linuxmint")
        self.assertEqual(result["6"]["end_support"], "2026-07-11")

        support_range = SupportRange.from_json(result["22.3"])
        self.assertEqual(support_range.version, "22.3")
        self.assertIsNotNone(support_range.end_support)

    @unittest.mock.patch("distro_support.linuxmint.request.urlopen")
    def test_http_error_raises(self, mock_urlopen):
        mock_urlopen.return_value = _make_response("", status=500)

        with self.assertRaises(ConnectionError):
            linuxmint.get_distro_info()

    @unittest.mock.patch("distro_support.linuxmint.request.urlopen")
    def test_mint_alias_module(self, mock_urlopen):
        mock_urlopen.return_value = _make_response(SAMPLE_MINT_RELEASES)

        result = mint.get_distro_info()
        self.assertIn("22.3", result)

    @unittest.mock.patch("distro_support.linuxmint.request.urlopen")
    def test_get_support_range_online(self, mock_urlopen):
        mock_urlopen.return_value = _make_response(SAMPLE_MINT_RELEASES)

        range_obj = distro_support.get_support_range(
            "linuxmint", "22.3", get_online=True
        )
        self.assertEqual(range_obj.distribution, "linuxmint")
        self.assertEqual(range_obj.version, "22.3")

        range_alias = distro_support.get_support_range("mint", "22.3", get_online=True)
        self.assertEqual(range_alias.distribution, "linuxmint")
        self.assertEqual(range_alias.version, "22.3")
