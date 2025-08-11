import importlib
import json
import pathlib
from distro_support._distro import SupportRange
from distro_support.errors import UnknownDistributionError, UnknownVersionError


def get_support_range(
    distribution: str, version: str, *, get_online: bool = False
) -> SupportRange:
    distro_file = pathlib.Path(__file__).with_name(f"{distribution}.json")
    if not distro_file.exists():
        raise UnknownDistributionError(distribution)

    distro_data = json.loads(distro_file.read_text())
    if version in distro_data:
        return SupportRange.from_json(distro_data[version])
    if not get_online:
        raise UnknownVersionError(distribution, version)

    distro_mod = importlib.import_module(f"{__package__}.{distribution}")

    distro_data = distro_mod.get_distro_info()
    if version in distro_data:
        return SupportRange.from_json(distro_data[version])
    raise UnknownVersionError(distribution, version)
