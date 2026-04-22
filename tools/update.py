"""Update distribution support data."""

import json
import pathlib

from distro_support import alpine, debian, devuan, rhel, ubuntu


def _version_sort_key(version: str) -> tuple[int, ...]:
    if not version:
        return (float("inf"),)  # type: ignore[return-value]
    try:
        return tuple(int(x) for x in version.split("."))
    except ValueError:
        return (0,)


def update(module):
    data_path = pathlib.Path(module.__file__).with_suffix(".json")
    data = module.get_distro_info()
    sorted_data = dict(
        sorted(data.items(), key=lambda item: _version_sort_key(item[0]))
    )
    data_path.write_text(json.dumps(sorted_data, indent="  ") + "\n")


if __name__ == "__main__":
    print("Updating Ubuntu data")
    update(ubuntu)
    print("Updating Debian data")
    update(debian)
    print("Updating Devuan data")
    update(devuan)
    print("Updating Alpine data")
    update(alpine)
    print("Updating RHEL data")
    update(rhel)
