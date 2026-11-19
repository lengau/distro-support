import json
import pathlib
from types import ModuleType

from distro_support._distro import SupportRange
from distro_support.errors import UnknownDistributionError, UnknownVersionError

ALIASES = {
    "mint": "linuxmint",
}


def _load_distro_module(name: str) -> ModuleType:
    match name:
        case "alpine":
            from . import alpine

            return alpine
        case "debian":
            from . import debian

            return debian
        case "devuan":
            from . import devuan

            return devuan
        case "linuxmint":
            from . import linuxmint

            return linuxmint
        case "rhel":
            from . import rhel

            return rhel
        case "ubuntu":
            from . import ubuntu

            return ubuntu
        case _:
            raise UnknownDistributionError(name)


def get_support_range(
    distribution: str, version: str, *, get_online: bool = False
) -> SupportRange:
    canonical = ALIASES.get(distribution, distribution)
    distro_file = pathlib.Path(__file__).with_name(f"{canonical}.json")
    if not distro_file.exists():
        raise UnknownDistributionError(distribution)

    distro_data = json.loads(distro_file.read_text())
    if version in distro_data:
        return SupportRange.from_json(distro_data[version])
    if not get_online:
        raise UnknownVersionError(distribution, version)

    distro_mod = _load_distro_module(canonical)

    distro_data = distro_mod.get_distro_info()
    if version in distro_data:
        return SupportRange.from_json(distro_data[version])
    raise UnknownVersionError(distribution, version)
