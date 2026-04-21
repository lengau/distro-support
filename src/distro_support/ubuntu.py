"""Information about Ubuntu support."""

from . import _debian_like_downloader

SUPPORT_INFO_URL = (
    "https://salsa.debian.org/debian/distro-info-data/-/raw/main/ubuntu.csv"
)


def get_distro_info() -> dict[str, dict[str, str]]:
    return _debian_like_downloader.get_distro_info(
        SUPPORT_INFO_URL, name="ubuntu", esm_name="esm"
    )
