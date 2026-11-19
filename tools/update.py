"""Update distribution support data."""

import json
import pathlib
import sys

from distro_support import alpine, debian, devuan, linuxmint, rhel, ubuntu


def _version_sort_key(version: str) -> tuple[int, ...]:
    if not version:
        return (sys.maxsize,)
    if version.startswith("lmde"):
        try:
            return (1000, *(int(x) for x in version.removeprefix("lmde").split(".")))
        except ValueError:
            return (1000, 0)
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
    print("Updating Linux Mint data")
    update(linuxmint)
