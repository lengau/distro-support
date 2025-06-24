"""Information about Debian support"""

from . import _debian_like_downloader

SUPPORT_INFO_URL = "https://salsa.debian.org/debian/distro-info-data/-/raw/main/debian.csv?ref_type=heads&inline=false"


def get_distro_info() -> dict[str, dict[str, str]]:
    return _debian_like_downloader.get_distro_info(
        SUPPORT_INFO_URL, name="debian", esm_name="elts"
    )
